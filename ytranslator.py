import os
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import argparse

# Third-party imports
from googletrans import Translator
from yt_dlp import YoutubeDL
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Configuration
from dataclasses import dataclass, field

@dataclass
class AppConfig:
    TARGET_LANGUAGES: Dict[str, str] = field(default_factory=lambda: {
        'Alemán': 'de',
        #'Chino (Simplificado)': 'zh-cn',
        #'Coreano': 'ko',
        #'Danés': 'da',
        #'Francés': 'fr',
        #'Hindi': 'hi',
        'Inglés': 'en',
        'Italiano': 'it',
        #'Japonés': 'ja',
        #'Noruego': 'no',
        #'Polaco': 'pl',
        'Portugués': 'pt',
        #'Ruso': 'ru',
        #'Sueco': 'sv',
        #'Ucraniano': 'uk',
        #'Árabe': 'ar',
    })
    SCOPES: List[str] = field(default_factory=lambda: ['https://www.googleapis.com/auth/youtube.force-ssl'])
    CREDENTIALS_FILE: Path = Path('client_secrets.json')
    TOKEN_FILE: Path = Path('token.json')
    DEFAULT_OUTPUT_DIR: Path = Path('translations')
    MAX_WORKERS: int = 3
    LOG_LEVEL: str = 'INFO'

config = AppConfig()

# Logging setup
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('LOG_ytranslator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Custom Exceptions
class TranslationError(Exception):
    """Base exception for translation errors"""

class AuthenticationError(Exception):
    """Authentication related errors"""

class YouTubeServiceError(Exception):
    """YouTube API related errors"""

# Translation Strategy Pattern
class TranslationStrategy:
    def translate(self, text: str, target_lang: str) -> str:
        raise NotImplementedError

class GoogleTranslateStrategy(TranslationStrategy):
    def __init__(self):
        from googletrans import Translator
        self.translator = Translator()
        self.cache: Dict[Tuple[str, str], str] = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def translate(self, text: str, target_lang: str) -> str:
        if not text.strip():
            return text
        cache_key = (text, target_lang)
        if cache_key in self.cache:
            return self.cache[cache_key]
        # Intenta primero con googletrans
        try:
            translated = self._translate_with_googletrans(text, target_lang)
            if translated:
                print(f"[Traductor] Usando googletrans para {target_lang}")
                self.cache[cache_key] = translated
                return translated
        except Exception as e:
            logger.warning(f"googletrans failed: {str(e)}")
        # Fallback a requests directo si googletrans falla
        try:
            translated = self._translate_with_fallback(text, target_lang)
            if translated:
                print(f"[Traductor] Usando fallback (API pública) para {target_lang}")
                self.cache[cache_key] = translated
                return translated
        except Exception as e:
            logger.error(f"Fallback translation failed: {str(e)}")
        print(f"[Traductor] No se pudo traducir para {target_lang}, devolviendo original.")
        return text  # Fallback al texto original

    def _translate_with_googletrans(self, text: str, target_lang: str) -> str:
        try:
            return self.translator.translate(text, dest=target_lang).text
        except AttributeError:
            return ""
        except Exception as e:
            logger.warning(f"googletrans error: {str(e)}")
            return ""

    def _translate_with_fallback(self, text: str, target_lang: str) -> str:
        """Fallback usando requests directamente a la API de Google Translate"""
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'auto',
                'tl': target_lang,
                'dt': 't',
                'q': text
            }
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                return ''.join([part[0] for part in data[0] if part])
        except Exception as e:
            logger.error(f"Fallback API error: {str(e)}")
        return ""

# YouTube Client usando yt-dlp
class YouTubeClient:
    def __init__(self, translation_strategy: TranslationStrategy):
        self.translation_strategy = translation_strategy

    def get_video_info(self, url: str) -> Dict:
        """Extrae título y subtítulos automáticos en español (si existen) usando yt-dlp"""
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': False,  # No descargar manuales
            'writeautomaticsub': True,  # Solo automáticos
            'subtitleslangs': ['es', 'es-419'],
            'quiet': True,
            'no_warnings': True,
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise YouTubeServiceError("No se pudo obtener información del video")
                video_id = info.get('id')
                title = info.get('title')
                subtitles = self._extract_automatic_subtitles(info)
                return {
                    'video_id': video_id,
                    'original_title': title,
                    'original_language': 'es',
                    'subtitles': subtitles
                }
        except Exception as e:
            logger.error(f"yt-dlp error: {str(e)}")
            raise YouTubeServiceError(f"Error al obtener info del video: {str(e)}")

    def _extract_automatic_subtitles(self, info: dict) -> str:
        """Extrae solo subtítulos automáticos en español"""
        auto_subs = info.get('automatic_captions', {})
        for lang in ['es', 'es-419']:
            if lang in auto_subs:
                sub_url = auto_subs[lang][0]['url']
                return self._download_subtitle(sub_url)
        raise ValueError("No se encontraron subtítulos automáticos en español")

    def _download_subtitle(self, url: str) -> str:
        """Descarga subtítulos, maneja VTT, SRT, listas M3U8 segmentadas y JSON de YouTube"""
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            content = response.text
            # Detecta si es una playlist M3U8
            if url.endswith('.m3u8') or '#EXTM3U' in content:
                logger.info("Detected M3U8 playlist for subtitles. Downloading and merging segments...")
                vtt_text = self._download_and_merge_m3u8_segments(url, content)
                return self._vtt_to_srt(vtt_text)
            # Si es VTT normal
            if url.endswith('.vtt') or 'WEBVTT' in content[:20]:
                return self._vtt_to_srt(content)
            # Si es SRT directo
            if url.endswith('.srt') or '-->' in content:
                return content
            # Si es JSON de YouTube
            try:
                data = json.loads(content)
                if 'events' in data:
                    return self._json_to_srt(data)
            except Exception:
                pass
            logger.warning("Unknown subtitle format. Returning raw content.")
            return content
        except Exception as e:
            logger.error(f"Error downloading subtitles: {str(e)}")
            raise

    def _json_to_srt(self, data: dict) -> str:
        """Convierte el formato JSON de subtítulos de YouTube a SRT"""
        srt = []
        counter = 1
        for event in data.get('events', []):
            if 'segs' not in event:
                continue
            # Tiempos
            start = int(event.get('tStartMs', 0))
            duration = int(event.get('dDurationMs', 0))
            end = start + duration
            start_srt = self._ms_to_srt_time(start)
            end_srt = self._ms_to_srt_time(end)
            # Texto
            text = ''.join(seg.get('utf8', '') for seg in event['segs'] if 'utf8' in seg).strip()
            if not text:
                continue
            srt.append(str(counter))
            srt.append(f"{start_srt} --> {end_srt}")
            srt.append(text)
            srt.append('')
            counter += 1
        return '\n'.join(srt)

    def _ms_to_srt_time(self, ms: int) -> str:
        """Convierte milisegundos a formato SRT (hh:mm:ss,mmm)"""
        h = ms // 3600000
        m = (ms % 3600000) // 60000
        s = (ms % 60000) // 1000
        ms = ms % 1000
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    def _download_and_merge_m3u8_segments(self, m3u8_url: str, m3u8_content: Optional[str] = None) -> str:
        """Descarga y une todos los segmentos VTT listados en una playlist M3U8"""
        try:
            if m3u8_content is None:
                m3u8_content = requests.get(m3u8_url, timeout=15).text
            base_url = m3u8_url.rsplit('/', 1)[0]
            vtt_urls = []
            for line in m3u8_content.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    # Si la URL es relativa, la hacemos absoluta
                    if line.startswith('http'):
                        vtt_urls.append(line)
                    else:
                        vtt_urls.append(f"{base_url}/{line}")
            vtt_texts = []
            for vtt_url in vtt_urls:
                try:
                    vtt_resp = requests.get(vtt_url, timeout=10)
                    vtt_resp.raise_for_status()
                    vtt_texts.append(vtt_resp.text.strip())
                except Exception as e:
                    logger.warning(f"Failed to download VTT segment: {vtt_url} ({str(e)})")
            # Unir todos los VTTs (quitando cabeceras duplicadas)
            merged = []
            for idx, vtt in enumerate(vtt_texts):
                lines = vtt.splitlines()
                # Quitar cabecera WEBVTT excepto en el primero
                if idx > 0 and lines and lines[0].startswith('WEBVTT'):
                    lines = lines[1:]
                merged.extend(lines)
            return '\n'.join(merged)
        except Exception as e:
            logger.error(f"Error merging M3U8 VTT segments: {str(e)}")
            raise

    def _vtt_to_srt(self, vtt_text: str) -> str:
        """Convierte texto VTT a SRT simple (básico)"""
        srt = []
        counter = 1
        for block in vtt_text.strip().split('\n\n'):
            lines = block.strip().split('\n')
            if len(lines) >= 2 and '-->' in lines[0]:
                srt.append(str(counter))
                srt.append(lines[0].replace('.', ','))
                srt.extend(lines[1:])
                srt.append('')
                counter += 1
        return '\n'.join(srt)

# Translation Processor
class TranslationProcessor:
    def __init__(self, client: YouTubeClient, output_dir: Path):
        self.client = client
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def process_video(self, url: str) -> Dict:
        """Main processing method"""
        video_info = self.client.get_video_info(url)
        self._save_original_subtitles(video_info['subtitles'])
        
        translated_titles = self._translate_titles(video_info['original_title'])
        translated_subs = self._translate_subtitles(video_info['subtitles'])
        
        return {
            'video_id': video_info['video_id'],
            'titles': translated_titles,
            'subtitles': translated_subs
        }

    def _translate_titles(self, title: str) -> Dict[str, Dict[str, str]]:
        """Translates video titles to all target languages"""
        results = {}
        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            future_to_lang = {
                executor.submit(
                    self._translate_title,
                    title,
                    lang_name,
                    lang_code
                ): (lang_name, lang_code)
                for lang_name, lang_code in config.TARGET_LANGUAGES.items()
            }
            
            for future in as_completed(future_to_lang):
                lang_name, lang_code = future_to_lang[future]
                try:
                    results[lang_name] = future.result()
                except Exception as e:
                    logger.error(f"Failed to translate title to {lang_name}: {str(e)}")
        
        self._save_translated_titles(title, results)
        return results

    def _translate_title(self, title: str, lang_name: str, lang_code: str) -> Dict[str, str]:
        """Translates a single title"""
        try:
            translated = self.client.translation_strategy.translate(title, lang_code)
            if not translated or translated.strip() == "" or translated.strip() == title.strip():
                print(f"⚠️  [ADVERTENCIA] No se pudo traducir el título al idioma {lang_name} ({lang_code}) o la traducción es igual al original.")
            return {'code': lang_code, 'title': translated}
        except Exception as e:
            print(f"❌  [ERROR] Falló la traducción del título a {lang_name} ({lang_code}): {str(e)}")
            logger.error(f"Title translation error ({lang_name}): {str(e)}")
            raise

    def _translate_subtitles(self, subtitles: str) -> Dict[str, Path]:
        """Translates subtitles to all target languages y añade español manual."""
        results = {}
        subs_dir = self.output_dir / 'subtitles'
        os.makedirs(subs_dir, exist_ok=True)
        # Añadir subtítulos en español (manual)
        original_es_path = subs_dir / 'original_es.srt'
        if original_es_path.exists():
            results['es'] = original_es_path
        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            future_to_lang = {
                executor.submit(
                    self._translate_single_subtitle,
                    subtitles,
                    lang_code,
                    subs_dir
                ): lang_code
                for lang_code in config.TARGET_LANGUAGES.values()
            }
            for future in as_completed(future_to_lang):
                lang_code = future_to_lang[future]
                try:
                    results[lang_code] = future.result()
                except Exception as e:
                    logger.error(f"Failed to translate subtitles to {lang_code}: {str(e)}")
        return results

    def _translate_single_subtitle(self, subtitles: str, lang_code: str, output_dir: Path) -> Path:
        """Translates subtitles to a single language"""
        try:
            translated_parts = []
            subtitle_parts = subtitles.split('\n\n')
            for part in subtitle_parts:
                if part.strip():
                    lines = part.split('\n')
                    if len(lines) >= 3:
                        header = '\n'.join(lines[:2])
                        # Traducir línea por línea para evitar errores
                        text_lines = lines[2:]
                        translated_lines = []
                        for line in text_lines:
                            if line.strip():
                                translated_line = self.client.translation_strategy.translate(line, lang_code)
                                if not translated_line or translated_line.strip() == "" or translated_line.strip() == line.strip():
                                    print(f"⚠️  [ADVERTENCIA] No se pudo traducir una línea al idioma {lang_code} o la traducción es igual al original.")
                                translated_lines.append(translated_line)
                            else:
                                translated_lines.append('')
                        translated_text = '\n'.join(translated_lines)
                        translated_parts.append(f"{header}\n{translated_text}")
            output_file = output_dir / f'translated_{lang_code}.srt'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(translated_parts))
            return output_file
        except Exception as e:
            print(f"❌  [ERROR] Falló la traducción de subtítulos a {lang_code}: {str(e)}")
            logger.error(f"Subtitle translation error ({lang_code}): {str(e)}")
            raise

    def _save_original_subtitles(self, subtitles: str) -> None:
        """Saves original subtitles to file"""
        original_file = self.output_dir / 'subtitles' / 'original_es.srt'
        os.makedirs(original_file.parent, exist_ok=True)
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write(subtitles)

    def _save_translated_titles(self, original_title: str, translations: Dict) -> None:
        """Saves translated titles to JSON file"""
        output_file = self.output_dir / 'translated_titles.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'original_title': original_title,
                'translations': translations
            }, f, ensure_ascii=False, indent=2)

# YouTube Manager
class YouTubeManager:
    def __init__(self):
        self.service = None

    def authenticate(self) -> None:
        """Authenticates with YouTube API"""
        try:
            creds = None
            if config.TOKEN_FILE.exists():
                creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.SCOPES)
            if not creds or not creds.valid:
                if not config.CREDENTIALS_FILE.exists():
                    raise AuthenticationError(f"Credentials file not found: {config.CREDENTIALS_FILE}")
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.CREDENTIALS_FILE, config.SCOPES)
                creds = flow.run_local_server(port=0)
                with open(config.TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            self.service = build('youtube', 'v3', credentials=creds)
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise AuthenticationError(f"Failed to authenticate: {str(e)}")

    def upload_translations(self, video_id: str, titles: Dict, subtitles: Dict) -> None:
        """Uploads translations to YouTube"""
        if not self.service:
            logger.error("YouTube API service is not authenticated (self.service is None)")
            raise YouTubeServiceError("Not authenticated with YouTube API")
        try:
            # Update titles
            self._update_video_titles(video_id, titles)
            # Upload subtitles
            self._upload_subtitles(video_id, subtitles)
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            raise YouTubeServiceError(f"YouTube API error: {e.error_details}")
        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            raise YouTubeServiceError(f"Failed to upload translations: {str(e)}")

    def _update_video_titles(self, video_id: str, titles: Dict) -> None:
        """Updates video titles in multiple languages, ensuring categoryId is set. No modifica el título original en español."""
        if not self.service:
            logger.error("YouTube API service is not authenticated (self.service is None)")
            raise YouTubeServiceError("Not authenticated with YouTube API")
        # Obtener el snippet actual para extraer el categoryId y el título original
        video_response = self.service.videos().list(
            part="snippet",
            id=video_id
        ).execute()
        items = video_response.get('items', [])
        if not items:
            raise YouTubeServiceError(f"No se encontró el video con id {video_id}")
        snippet = items[0]['snippet']
        # Guardar valores originales
        original_title = snippet.get('title', '')[:100]  # Truncar a 100 chars
        category_id = str(snippet.get('categoryId', '22'))  # Siempre string
        description = snippet.get('description', '')
        # Construir un nuevo snippet SOLO con los campos permitidos y válidos
        snippet_update = {
            'title': original_title,
            'categoryId': category_id,
        }
        if description:
            snippet_update['description'] = description
        # Solo añadir traducciones, no modificar el título original
        localizations = {}
        for lang_name, translation in titles.items():
            code = translation.get('code')
            title_trad = translation.get('title', '').strip()[:100]  # Truncar a 100 chars
            if code and code != 'es' and title_trad and title_trad != original_title:
                localizations[code] = {'title': title_trad}
        print(f"Longitud del título original: {len(original_title)}")
        for code, loc in localizations.items():
            print(f"Localización {code}: longitud título={len(loc['title'])}")
        print(f"Claves de localizations: {list(localizations.keys())}")
        if localizations:
            print(f"Localizaciones a subir: {json.dumps(localizations, ensure_ascii=False, indent=2)}")
        else:
            print("No hay localizaciones válidas para subir.")
        body = {
            "id": video_id,
            "snippet": snippet_update
        }
        if localizations:
            body["localizations"] = localizations
        # Imprime el body completo antes de subir
        print("Cuerpo final que se enviará a la API (con truncado y descripción):")
        print(json.dumps(body, ensure_ascii=False, indent=2))
        try:
            response = self.service.videos().update(
                part="snippet,localizations" if localizations else "snippet",
                body=body
            ).execute()
            print("Respuesta de la API:")
            print(json.dumps(response, ensure_ascii=False, indent=2))
        except HttpError as e:
            print("Error al actualizar con localizations:")
            print(e)
            print(getattr(e, 'content', ''))
            # Ahora intenta solo actualizar el snippet SIN localizations
            print("Intentando de nuevo solo con snippet (sin localizations)...")
            body2 = {
                "id": video_id,
                "snippet": snippet_update
            }
            print(json.dumps(body2, ensure_ascii=False, indent=2))
            try:
                response = self.service.videos().update(
                    part="snippet",
                    body=body2
                ).execute()
                print("Respuesta de la API (solo snippet):")
                print(json.dumps(response, ensure_ascii=False, indent=2))
            except HttpError as e2:
                print("Error final al actualizar solo snippet:")
                print(e2)
                print(getattr(e2, 'content', ''))
                raise YouTubeServiceError(f"YouTube API error: {e2}")

    def _upload_subtitles(self, video_id: str, subtitles: Dict) -> None:
        """Uploads all subtitles (including Spanish) with the language name as track name (no date/time)."""
        if not self.service:
            logger.error("YouTube API service is not authenticated (self.service is None)")
            raise YouTubeServiceError("Not authenticated with YouTube API")
        # Crear un diccionario inverso para mapear lang_code a nombre legible
        lang_code_to_name = {v: k for k, v in config.TARGET_LANGUAGES.items()}
        lang_code_to_name['es'] = 'Español'
        # Obtener las pistas de subtítulos existentes
        try:
            existing_captions = self.service.captions().list(
                part="snippet",
                videoId=video_id
            ).execute().get('items', [])
        except Exception as e:
            logger.error(f"No se pudieron obtener las pistas de subtítulos existentes: {str(e)}")
            existing_captions = []
        for lang_code, file_path in subtitles.items():
            track_name = lang_code_to_name.get(lang_code, lang_code)
            # Comprobar si ya existe una pista con ese idioma y nombre
            already_exists = False
            for cap in existing_captions:
                snippet = cap.get('snippet', {})
                if snippet.get('language') == lang_code and snippet.get('name') == track_name:
                    already_exists = True
                    break
            if already_exists:
                print(f"Ya existe una pista de subtítulos para {track_name} ({lang_code}), omitiendo subida.")
                logger.info(f"Ya existe una pista de subtítulos para {track_name} ({lang_code}), omitiendo subida.")
                continue
            try:
                print(f"Subiendo subtítulos para {track_name} ({lang_code}): {file_path}")
                media = MediaFileUpload(
                    file_path,
                    mimetype='application/octet-stream',
                    resumable=True
                )
                self.service.captions().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "videoId": video_id,
                            "language": lang_code,
                            "name": track_name,
                            "isDraft": False
                        }
                    },
                    media_body=media
                ).execute()
                print(f"Subtítulos subidos correctamente para {track_name} ({lang_code})")
                logger.info(f"Successfully uploaded subtitles for {lang_code} with name {track_name}")
            except Exception as e:
                logger.error(f"Failed to upload subtitles for {lang_code}: {str(e)}")
                print(f"Error al subir subtítulos para {track_name} ({lang_code}): {str(e)}")
                continue

# Main Application
class YouTubeTranslatorApp:
    def __init__(self):
        self.translation_strategy = GoogleTranslateStrategy()
        self.youtube_client = YouTubeClient(self.translation_strategy)
        self.youtube_manager = YouTubeManager()

    def run(self):
        """Main application loop"""
        parser = argparse.ArgumentParser(description='YouTube Translation Tool')
        parser.add_argument('url', nargs='?', help='YouTube video URL')
        parser.add_argument('--output', '-o', default=config.DEFAULT_OUTPUT_DIR,
                          help='Output directory for translations')
        parser.add_argument('--upload', '-u', action='store_true',
                          help='Upload translations to YouTube')
        args = parser.parse_args()

        try:
            if not args.url:
                self._interactive_mode()
            else:
                self._process_video(args.url, Path(args.output), args.upload)
        except Exception as e:
            logger.error(f"Application error: {str(e)}")
            raise

    def _interactive_mode(self):
        """Interactive command line interface"""
        while True:
            print("\nYouTube Translator Tool")
            print("1. Translate video")
            print("2. Authenticate with YouTube")
            print("3. Exit")
            
            choice = input("Select option (1-3): ")
            
            if choice == '3':
                break
            elif choice == '2':
                self._authenticate_interactive()
            elif choice == '1':
                self._translate_interactive()
            else:
                print("Invalid option")

    def _authenticate_interactive(self):
        """Interactive authentication"""
        try:
            print("\nAuthenticating with YouTube...")
            self.youtube_manager.authenticate()
            print("Authentication successful!")
        except Exception as e:
            print(f"Authentication failed: {str(e)}")

    def _translate_interactive(self):
        """Interactive translation process"""
        url = input("\nEnter YouTube video URL: ").strip()
        if not url:
            print("URL cannot be empty")
            return
            
        output_dir = input(f"Enter output directory (default: {config.DEFAULT_OUTPUT_DIR}): ").strip()
        output_dir = Path(output_dir) if output_dir else config.DEFAULT_OUTPUT_DIR
        
        upload = input("Upload to YouTube? (y/n): ").lower() == 'y'
        
        self._process_video(url, output_dir, upload)

    def _process_video(self, url: str, output_dir: Path, upload: bool):
        """Processes a single video"""
        try:
            print("\nStarting translation process...")
            processor = TranslationProcessor(self.youtube_client, output_dir)
            result = processor.process_video(url)
            print("\nTranslation completed successfully!")
            
            if upload:
                if not self.youtube_manager.service:
                    print("\nAuthenticating with YouTube...")
                    self.youtube_manager.authenticate()
                
                print("\nUploading translations to YouTube...")
                self.youtube_manager.upload_translations(
                    result['video_id'],
                    result['titles'],
                    result['subtitles']
                )
                print("\nUpload completed successfully!")
            
            print(f"\nResults saved to: {output_dir}")
        except Exception as e:
            print(f"\nError: {str(e)}")
            logger.error(f"Processing failed: {str(e)}")

if __name__ == "__main__":
    app = YouTubeTranslatorApp()
    app.run()
