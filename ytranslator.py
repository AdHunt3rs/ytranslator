print("""
██╗   ██╗████████╗██████╗  █████╗ ███╗   ██╗███████╗██╗      █████╗ ████████╗ ██████╗ ██████╗ 
╚██╗ ██╔╝╚══██╔══╝██╔══██╗██╔══██╗████╗  ██║██╔════╝██║     ██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗
 ╚████╔╝    ██║   ██████╔╝███████║██╔██╗ ██║███████╗██║     ███████║   ██║   ██║   ██║██████╔╝
  ╚██╔╝     ██║   ██╔══██╗██╔══██║██║╚██╗██║╚════██║██║     ██╔══██║   ██║   ██║   ██║██╔══██╗
   ██║      ██║   ██║  ██║██║  ██║██║ ╚████║███████║███████╗██║  ██║   ██║   ╚██████╔╝██║  ██║
   ╚═╝      ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝

            |   2025   |   V: 0.7   |   adhunt3rs   |
----------------------------------------------------------------------------------------------""")
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
        #'Alemán': 'de',
        #'Chino (Simplificado)': 'zh-CN',
        #'Coreano': 'ko',
        #'Danés': 'da',
        #'Español': 'es',
        #'Francés': 'fr',
        #'Hindi': 'hi',
        'Inglés': 'en',
        #'Italiano': 'it',
        #'Japonés': 'ja',
        #'Noruego': 'no',
        #'Polaco': 'pl',
        #'Portugués': 'pt',
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
    def translate(self, text: str, target_lang: str, source_lang: str = 'auto') -> str:
        raise NotImplementedError

class GoogleTranslateStrategy(TranslationStrategy):
    def __init__(self):
        from googletrans import Translator
        self.translator = Translator()
        self.cache: Dict[Tuple[str, str, str], str] = {}  # (text, target_lang, source_lang)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def translate(self, text: str, target_lang: str, source_lang: str = 'auto') -> str:
        if not text.strip():
            return text
        cache_key = (text, target_lang, source_lang)
        if cache_key in self.cache:
            return self.cache[cache_key]
        # Intenta primero con googletrans
        try:
            translated = self._translate_with_googletrans(text, target_lang, source_lang)
            if translated:
                print(f"[Traductor] Usando googletrans para {target_lang} (desde {source_lang})")
                self.cache[cache_key] = translated
                return translated
        except Exception as e:
            logger.warning(f"googletrans failed: {str(e)}")
        # Fallback a requests directo si googletrans falla
        try:
            translated = self._translate_with_fallback(text, target_lang, source_lang)
            if translated:
                print(f"[Traductor] Usando fallback (API pública) para {target_lang} (desde {source_lang})")
                self.cache[cache_key] = translated
                return translated
        except Exception as e:
            logger.error(f"Fallback translation failed: {str(e)}")
        print(f"[Traductor] No se pudo traducir para {target_lang}, devolviendo original.")
        return text  # Fallback al texto original

    def _translate_with_googletrans(self, text: str, target_lang: str, source_lang: str = 'auto') -> str:
        try:
            return self.translator.translate(text, src=source_lang, dest=target_lang).text
        except AttributeError:
            return ""
        except Exception as e:
            logger.warning(f"googletrans error: {str(e)}")
            return ""

    def _translate_with_fallback(self, text: str, target_lang: str, source_lang: str = 'auto') -> str:
        """Fallback usando requests directamente a la API de Google Translate"""
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': source_lang,
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

    def get_video_info(self, url: str, preferred_lang: Optional[str] = None) -> Dict:
        """Extrae título, descripción y subtítulos automáticos en el idioma base detectado o definido por el usuario usando yt-dlp"""
        # Determinar idioma preferido
        lang_list = []
        if preferred_lang and preferred_lang != 'auto':
            lang_list.append(preferred_lang)
        # Añadir variantes comunes si es español
        if preferred_lang in ['es', 'es-419', 'es-ES', 'es-MX']:
            lang_list.extend([l for l in ['es', 'es-419', 'es-ES', 'es-MX'] if l != preferred_lang])
        # Si no hay preferido, buscar todos los idiomas soportados por Google Translate
        if not lang_list:
            lang_list = ['es', 'en', 'fr', 'it', 'de', 'pt', 'ru', 'ja', 'ko', 'zh-cn', 'ar', 'hi', 'pl', 'uk', 'sv', 'no', 'da']
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': False,  # No descargar manuales
            'writeautomaticsub': True,  # Solo automáticos
            'subtitleslangs': lang_list,
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
                description = info.get('description', None)
                # Detectar idioma base si es posible
                detected_lang = info.get('language') or info.get('original_language') or info.get('subtitles_language')
                if not detected_lang:
                    detected_langs = list(info.get('automatic_captions', {}).keys())
                    detected_lang = detected_langs[0] if detected_langs else None
                # Elegir idioma de subtítulo a usar
                subs_lang = preferred_lang if preferred_lang and preferred_lang != 'auto' else detected_lang
                subtitles = self._extract_automatic_subtitles(info, subs_lang)
                return {
                    'video_id': video_id,
                    'original_title': title,
                    'original_language': detected_lang or 'auto',
                    'subtitles': subtitles,
                    'description': description
                }
        except Exception as e:
            logger.error(f"yt-dlp error: {str(e)}")
            raise YouTubeServiceError(f"Error al obtener info del video: {str(e)}")

    def _extract_automatic_subtitles(self, info: dict, lang: Optional[str] = None) -> str:
        """Extrae subtítulos automáticos en el idioma solicitado o, si no existe, en el primero disponible"""
        auto_subs = info.get('automatic_captions', {})
        # Si se especifica idioma y existe, usarlo
        if lang and lang in auto_subs:
            sub_url = auto_subs[lang][0]['url']
            return self._download_subtitle(sub_url)
        # Si no, usar el primero disponible
        for l, tracks in auto_subs.items():
            if tracks:
                return self._download_subtitle(tracks[0]['url'])
        raise ValueError("No se encontraron subtítulos automáticos en el idioma base ni en ningún otro idioma disponible")

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
    def __init__(self, client: YouTubeClient, output_dir: Path, source_lang: str = 'auto'):
        self.client = client
        self.output_dir = output_dir
        self.source_lang = source_lang
        os.makedirs(self.output_dir, exist_ok=True)

    def process_video(self, url: str) -> Dict:
        """Main processing method"""
        video_info = self.client.get_video_info(url, preferred_lang=self.source_lang)
        self._save_original_subtitles(video_info['subtitles'], video_info.get('original_language', self.source_lang))
        translated_titles = self._translate_titles(video_info['original_title'])
        translated_subs = self._translate_subtitles(video_info['subtitles'], video_info.get('original_language', self.source_lang))
        return {
            'video_id': video_info['video_id'],
            'titles': translated_titles,
            'subtitles': translated_subs
        }

    def process_video_custom(self, url: str, translate_title: bool, translate_subs: bool, translate_desc: bool) -> Dict:
        """Procesa el vídeo según las opciones elegidas"""
        video_info = self.client.get_video_info(url, preferred_lang=self.source_lang)
        result = {'video_id': video_info['video_id']}
        lang = video_info.get('original_language', self.source_lang)
        if translate_title:
            result['titles'] = self._translate_titles(video_info['original_title'])
        if translate_subs:
            self._save_original_subtitles(video_info['subtitles'], lang)
            result['subtitles'] = self._translate_subtitles(video_info['subtitles'], lang)
        if translate_desc:
            desc = video_info.get('description')
            if desc is None:
                desc = self._get_description_from_api(video_info['video_id'])
            result['descriptions'] = self._translate_descriptions(desc or "")
        return result

    def _get_description_from_api(self, video_id: str) -> str:
        """Obtiene la descripción del video usando la API de YouTube si no está en video_info"""
        try:
            youtube = build('youtube', 'v3', credentials=None)
            response = youtube.videos().list(part="snippet", id=video_id).execute()
            items = response.get('items', [])
            if items:
                return items[0]['snippet'].get('description', '')
        except Exception as e:
            logger.warning(f"No se pudo obtener la descripción vía API: {str(e)}")
        return ""

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
            translated = self.client.translation_strategy.translate(title, lang_code, self.source_lang)
            if not translated or translated.strip() == "" or translated.strip() == title.strip():
                print(f"⚠️  [ADVERTENCIA] No se pudo traducir el título al idioma {lang_name} ({lang_code}) o la traducción es igual al original.")
            return {'code': lang_code, 'title': translated}
        except Exception as e:
            print(f"❌  [ERROR] Falló la traducción del título a {lang_name} ({lang_code}): {str(e)}")
            logger.error(f"Title translation error ({lang_name}): {str(e)}")
            raise

    def _translate_subtitles(self, subtitles: str, lang: str = 'es') -> Dict[str, Path]:
        """Translates subtitles to all target languages y añade original manual del idioma base."""
        results = {}
        subs_dir = self.output_dir / 'subtitles'
        os.makedirs(subs_dir, exist_ok=True)
        # Añadir subtítulos en idioma base (manual)
        original_path = subs_dir / f'original_{lang}.srt'
        if original_path.exists():
            results[lang] = original_path
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
        """Traduce cada bloque SRT completo (no línea por línea) para mayor coherencia y mantiene la sincronización."""
        try:
            translated_parts = []
            subtitle_parts = subtitles.strip().split('\n\n')
            for part in subtitle_parts:
                if part.strip():
                    lines = part.split('\n')
                    if len(lines) >= 3:
                        header = '\n'.join(lines[:2])
                        text_block = '\n'.join(lines[2:]).strip()
                        translated_text = self.client.translation_strategy.translate(text_block, lang_code, self.source_lang)
                        if not translated_text or translated_text.strip() == '' or translated_text.strip() == text_block.strip():
                            print(f"⚠️  [ADVERTENCIA] No se pudo traducir un bloque al idioma {lang_code} o la traducción es igual al original.")
                        # Mantener el mismo número de líneas que el bloque original para evitar desincronización
                        orig_lines = text_block.split('\n')
                        trans_lines = translated_text.split('\n')
                        # Si el número de líneas no coincide, intentar ajustar
                        if len(trans_lines) != len(orig_lines):
                            # Si solo hay una línea traducida pero varias originales, repartir el texto
                            if len(trans_lines) == 1 and len(orig_lines) > 1:
                                import textwrap
                                wrapped = textwrap.wrap(translated_text, width=max(10, int(len(translated_text)/len(orig_lines))))
                                while len(wrapped) < len(orig_lines):
                                    wrapped.append('')
                                trans_lines = wrapped[:len(orig_lines)]
                            else:
                                while len(trans_lines) < len(orig_lines):
                                    trans_lines.append('')
                                trans_lines = trans_lines[:len(orig_lines)]
                        translated_text_final = '\n'.join(trans_lines)
                        translated_parts.append(f"{header}\n{translated_text_final}")
            output_file = output_dir / f'translated_{lang_code}.srt'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(translated_parts))
            return output_file
        except Exception as e:
            print(f"❌  [ERROR] Falló la traducción de subtítulos a {lang_code}: {str(e)}")
            logger.error(f"Subtitle translation error ({lang_code}): {str(e)}")
            raise

    def _save_original_subtitles(self, subtitles: str, lang: str = 'es') -> None:
        """Saves original subtitles to file with correct language code"""
        original_file = self.output_dir / 'subtitles' / f'original_{lang}.srt'
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

    def _translate_descriptions(self, description: str) -> Dict[str, str]:
        """Traduce la descripción a todos los idiomas objetivo"""
        results = {}
        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            future_to_lang = {
                executor.submit(
                    self.client.translation_strategy.translate,
                    description,
                    lang_code
                ): (lang_name, lang_code)
                for lang_name, lang_code in config.TARGET_LANGUAGES.items()
            }
            for future in as_completed(future_to_lang):
                lang_name, lang_code = future_to_lang[future]
                try:
                    results[lang_code] = future.result()
                except Exception as e:
                    logger.error(f"Failed to translate description to {lang_name}: {str(e)}")
        # Guardar descripciones traducidas
        output_file = self.output_dir / 'translated_descriptions.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        return results

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

    def upload_translations_custom(self, video_id: str, titles: Optional[Dict], subtitles: Optional[Dict], descriptions: Optional[Dict]):
        """Sube las traducciones seleccionadas a YouTube"""
        if not self.service:
            logger.error("YouTube API service is not authenticated (self.service is None)")
            raise YouTubeServiceError("Not authenticated with YouTube API")
        try:
            if titles:
                self._update_video_titles(video_id, titles, descriptions)
            if subtitles:
                self._upload_subtitles(video_id, subtitles)
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            raise YouTubeServiceError(f"YouTube API error: {e.error_details}")
        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            raise YouTubeServiceError(f"Failed to upload translations: {str(e)}")

    def _update_video_titles(self, video_id: str, titles: Dict, descriptions: Optional[Dict] = None) -> None:
        """Actualiza títulos y descripciones en varios idiomas, conservando los ya existentes salvo que el usuario decida sobrescribirlos."""
        if not self.service:
            logger.error("YouTube API service is not authenticated (self.service is None)")
            raise YouTubeServiceError("Not authenticated with YouTube API")
        video_response = self.service.videos().list(
            part="snippet,localizations",
            id=video_id
        ).execute()
        items = video_response.get('items', [])
        if not items:
            raise YouTubeServiceError(f"No se encontró el video con id {video_id}")
        snippet = items[0]['snippet']
        original_title = snippet.get('title', '')[:100]
        category_id = str(snippet.get('categoryId', '22'))
        description = snippet.get('description', '')
        # Detectar el idioma original del video (si está disponible)
        default_language = snippet.get('defaultLanguage', None)
        if not default_language:
            default_language = 'es'
        # Obtener localizaciones existentes
        existing_localizations = items[0].get('localizations', {})
        # Construir nuevas localizaciones combinando existentes y nuevas
        localizations = existing_localizations.copy()
        for lang_name, translation in (titles or {}).items():
            code = translation.get('code')
            title_trad = translation.get('title', '').strip()[:100]
            if code and code != 'es' and title_trad and title_trad != original_title:
                # Si ya existe, preguntar si sobrescribir
                if code in localizations:
                    print(f"Ya existe una localización para el idioma {code} (título: '{localizations[code].get('title','')}').")
                    resp = input(f"¿Quieres sobrescribir el título/descripcion en {code}? (s/n): ").strip().lower()
                    if resp != 's':
                        continue
                loc = {'title': title_trad}
                if descriptions and code in descriptions:
                    loc['description'] = descriptions[code]
                localizations[code] = loc
        snippet_update = {
            'title': original_title,
            'categoryId': category_id,
            'defaultLanguage': default_language,
        }
        if description:
            snippet_update['description'] = description
        body = {
            "id": video_id,
            "snippet": snippet_update,
            "localizations": localizations
        }
        print("Cuerpo final que se enviará a la API (con truncado, descripción y localizations):")
        print(json.dumps(body, ensure_ascii=False, indent=2))
        try:
            response = self.service.videos().update(
                part="snippet,localizations",
                body=body
            ).execute()
            print("Respuesta de la API:")
            print(json.dumps(response, ensure_ascii=False, indent=2))
            if 'localizations' in response:
                print("\nTítulos y descripciones localizados subidos:")
                for code, loc in response['localizations'].items():
                    title = loc.get('title', '')
                    desc = loc.get('description', '')
                    print(f"  - [{code}] Título: {title}")
                    if desc:
                        print(f"    Descripción: {desc}")
            else:
                print("No se detectaron localizaciones subidas en la respuesta de la API.")
        except HttpError as e:
            print("Error al actualizar con localizations:")
            print(e)
            print(getattr(e, 'content', ''))
            raise YouTubeServiceError(f"YouTube API error: {e}")

    def _upload_subtitles(self, video_id: str, subtitles: Dict) -> None:
        """Uploads all subtitles (including Spanish) with the language name as track name (no date/time)."""
        if not self.service:
            logger.error("YouTube API service is not authenticated (self.service is None)")
            raise YouTubeServiceError("Not authenticated with YouTube API")
        lang_code_to_name = {v: k for k, v in config.TARGET_LANGUAGES.items()}
        lang_code_to_name['es'] = 'Español'
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
            cap_id = None
            for cap in existing_captions:
                snippet = cap.get('snippet', {})
                if snippet.get('language') == lang_code and snippet.get('name') == track_name:
                    cap_id = cap.get('id')
                    break
            if cap_id:
                resp = input(f"Ya existe una pista de subtítulos para {track_name} ({lang_code}). ¿Quieres sobrescribirla? (s/n): ").strip().lower()
                if resp != 's':
                    print(f"Omitiendo subida de subtítulos para {track_name} ({lang_code})")
                    logger.info(f"Omitiendo subida de subtítulos para {track_name} ({lang_code})")
                    continue
                # Eliminar pista existente
                try:
                    self.service.captions().delete(id=cap_id).execute()
                    print(f"Pista de subtítulos existente para {track_name} ({lang_code}) eliminada.")
                except Exception as e:
                    print(f"No se pudo eliminar la pista existente: {e}")
                    logger.error(f"No se pudo eliminar la pista existente: {e}")
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

class YouTubeTranslatorApp:
    def __init__(self):
        self.translation_strategy = GoogleTranslateStrategy()
        self.youtube_client = YouTubeClient(self.translation_strategy)
        self.youtube_manager = YouTubeManager()
        self.source_lang = 'auto'

    def translate_from_manual_srt(self):
        print("\nTraducir y (opcionalmente) subir subtítulos a partir de un archivo SRT revisado")
        folder_name = input("Introduce el nombre de la carpeta en 'translations/' donde está el SRT revisado: ").strip()
        output_dir = Path('translations') / folder_name
        subs_dir = output_dir / 'subtitles'
        if not subs_dir.exists():
            print("La carpeta de subtítulos no existe. Descarga primero los subtítulos automáticos y revísalos.")
            return
        # Preguntar idioma base
        source_lang = input("Introduce el código del idioma base del vídeo (por ejemplo, es, en, fr) o deja vacío para autodetectar: ").strip().lower() or 'auto'
        # Validar código de idioma base
        valid_langs = set([v.lower() for v in config.TARGET_LANGUAGES.values()])
        if source_lang != 'auto' and source_lang not in valid_langs:
            print(f"⚠️  [ADVERTENCIA] El código '{source_lang}' no está en los idiomas de destino configurados. Si es correcto, continúa; si no, revisa la lista de códigos soportados en la documentación.")
        self.source_lang = source_lang
        srt_file = subs_dir / f'original_{self.source_lang}.srt'
        if not srt_file.exists():
            # Buscar archivos originales disponibles
            disponibles = list(subs_dir.glob('original_*.srt'))
            if not disponibles:
                print(f"No se encontró ningún archivo original_*.srt en {subs_dir}. Asegúrate de haberlo revisado y guardado.")
                return
            print(f"No se encontró el archivo {srt_file}.")
            print("Archivos originales disponibles en la carpeta:")
            for idx, f in enumerate(disponibles, 1):
                print(f"  {idx}. {f.name}")
            sel = input("Selecciona el número del archivo a usar como base (o pulsa Enter para cancelar): ").strip()
            if not sel.isdigit() or int(sel) < 1 or int(sel) > len(disponibles):
                print("Operación cancelada.")
                return
            srt_file = disponibles[int(sel)-1]
            # Extraer el nuevo source_lang del nombre de archivo
            import re
            m = re.match(r'original_([a-zA-Z\-]+)\.srt', srt_file.name)
            if m:
                self.source_lang = m.group(1).lower()
            else:
                print("No se pudo determinar el idioma base del archivo seleccionado. Usa el valor introducido.")
        # Leer SRT revisado
        with open(srt_file, encoding='utf-8') as f:
            srt_content = f.read()
        print(f"Traduciendo subtítulos revisados a los idiomas configurados desde '{self.source_lang}'...")
        processor = TranslationProcessor(self.youtube_client, output_dir, self.source_lang)
        translated_subs = processor._translate_subtitles(srt_content, self.source_lang)
        print("Traducción de subtítulos completada. Archivos generados:")
        for lang, path in translated_subs.items():
            print(f"  - {lang}: {path}")
        print("\nIntroduce el título original del vídeo (en el idioma base, tal como debe aparecer en YouTube):")
        original_title = input("Título original: ").strip()
        if not original_title:
            print("El título no puede estar vacío. Se omite la traducción de título.")
            translated_titles = None
        else:
            print("Traduciendo título a los idiomas configurados...")
            processor.source_lang = self.source_lang
            translated_titles = processor._translate_titles(original_title)
            print("Traducción de título completada.")
            print("\nTítulos traducidos generados:")
            for lang, data in (translated_titles or {}).items():
                print(f"  - {lang} [{data.get('code','')}] : {data.get('title','')}")
        if translated_titles:
            processor._save_translated_titles(original_title, translated_titles)
        print("\n¿Qué deseas subir a YouTube?")
        print("1. Solo títulos/descripciones")
        print("2. Solo subtítulos")
        print("3. Ambos (títulos/descripciones y subtítulos)")
        print("0. No subir nada ahora\n")
        choice = input("Selecciona una opción (0-3): ").strip()
        if choice == '0':
            print("Puedes subir los subtítulos y títulos más tarde usando la opción de subir desde carpeta existente.")
            return
        upload_titles = choice in ['1', '3']
        upload_subs = choice in ['2', '3']
        if upload_titles or upload_subs:
            url = input("Introduce la URL o el ID del vídeo de YouTube: ").strip()
            if not self.youtube_manager.service:
                print("\nAutenticando con YouTube...")
                self.youtube_manager.authenticate()
            video_id = None
            if url:
                import re
                m = re.search(r'(?:v=|youtu\.be/)([\w-]+)', url)
                if m:
                    video_id = m.group(1)
                else:
                    video_id = url
            if not video_id:
                print("No se pudo extraer el ID del vídeo.")
                return
            print("\nSubiendo a YouTube...")
            self.youtube_manager.upload_translations_custom(
                video_id,
                translated_titles if upload_titles else None,
                translated_subs if upload_subs else None,
                None
            )
            print("\n¡Subida completada con éxito!")

    def upload_from_existing_folder(self):
        print("\nSubir traducciones desde carpeta existente")
        folder_name = input("Introduce el nombre de la carpeta en 'translations/' con las traducciones listas para subir: ").strip()
        output_dir = Path('translations') / folder_name
        if not output_dir.exists():
            print(f"La carpeta {output_dir} no existe.")
            return
        # Cargar títulos
        titles_path = output_dir / 'translated_titles.json'
        titles = None
        if titles_path.exists():
            with open(titles_path, encoding='utf-8') as f:
                data = json.load(f)
                titles = data.get('translations')
        # Cargar descripciones
        desc_path = output_dir / 'translated_descriptions.json'
        descriptions = None
        if desc_path.exists():
            with open(desc_path, encoding='utf-8') as f:
                descriptions = json.load(f)
        # Cargar subtítulos
        subs_dir = output_dir / 'subtitles'
        subtitles = {}
        if subs_dir.exists():
            for file in subs_dir.iterdir():
                if file.name.startswith('translated_') and file.suffix == '.srt':
                    lang_code = file.stem.split('_', 1)[-1]
                    subtitles[lang_code] = file
                elif file.name.startswith('original_') and file.suffix == '.srt':
                    lang_code = file.stem.split('_', 1)[-1]
                    subtitles[lang_code] = file
        if not any([titles, descriptions, subtitles]):
            print("\nNo se encontraron archivos de traducción válidos en la carpeta.")
            return
        # Mostrar resumen
        print("\nResumen de archivos encontrados:")
        if titles:
            print("- Títulos traducidos:", ', '.join([f"{k} [{v.get('code','')}]" for k,v in titles.items()]))
        if descriptions:
            print("- Descripciones traducidas:", ', '.join(descriptions.keys()))
        if subtitles:
            print("- Subtítulos:", ', '.join(subtitles.keys()))
        # Elegir qué subir
        print("\n¿Qué deseas subir a YouTube?")
        print("1. Solo títulos/descripciones")
        print("2. Solo subtítulos")
        print("3. Ambos (títulos/descripciones y subtítulos)")
        print("0. Cancelar\n")
        sub_choice = input("Selecciona una opción (0-3): ").strip()
        if sub_choice == '0':
            print("Operación cancelada.")
            return
        upload_titles = sub_choice in ['1', '3']
        upload_subs = sub_choice in ['2', '3']
        url = input("Introduce la URL o el ID del vídeo de YouTube: ").strip()
        if not self.youtube_manager.service:
            print("\nAutenticando con YouTube...")
            self.youtube_manager.authenticate()
        # Obtener video_id
        video_id = None
        if url:
            import re
            m = re.search(r'(?:v=|youtu\.be/)([\w-]+)', url)
            if m:
                video_id = m.group(1)
            else:
                video_id = url  # Si ya es el ID
        if not video_id:
            print("No se pudo extraer el ID del vídeo.")
            return
        print("\nSubiendo a YouTube...")
        self.youtube_manager.upload_translations_custom(
            video_id,
            titles if upload_titles else None,
            subtitles if upload_subs else None,
            descriptions if upload_titles else None
        )
        print("\n¡Subida completada con éxito!")

    def change_base_language(self):
        print(f"\nIdioma base actual: {self.source_lang}")
        new_lang = input("Introduce el nuevo código de idioma base (por ejemplo, es, en, fr): ").strip().lower()
        # Permitir cualquier código, pero advertir si no está en la lista de Google Translate
        from googletrans import LANGUAGES
        if new_lang not in LANGUAGES and new_lang not in LANGUAGES.values():
            print(f"⚠️  [ADVERTENCIA] El código '{new_lang}' no está en la lista de idiomas soportados por Google Translate. Si es correcto, continúa; si no, revisa la lista de códigos soportados en la documentación.")
        self.source_lang = new_lang
        print(f"Idioma base cambiado a: {self.source_lang}")

if __name__ == "__main__":
    print("\n===== YouTube Translator Tool =====\n")
    app = YouTubeTranslatorApp()
    while True:
        print(f"\nMenú principal (idioma base actual: {app.source_lang}):\n")
        print("1. Traducir vídeo completo (título, subtítulos, descripción)")
        print("2. Autenticarse con YouTube")
        print("3. Subir traducciones desde carpeta existente")
        print("4. Descargar títulos, descripciones y subtítulos automáticos disponibles para revisar manualmente")
        print("5. Traducir y (opcionalmente) subir subtítulos a partir de un archivo SRT revisado")
        print("6. Salir")
        print("7. Cambiar/definir idioma base\n")
        choice = input("Selecciona una opción (1-7): ").strip()
        # En todas las llamadas a get_video_info, pasar el idioma base detectado o definido por el usuario
        # Opción 1: Traducir vídeo completo
        if choice == '1':
            print("\n=== Traducir vídeo completo (título, subtítulos, descripción) ===\n")
            url = input("Introduce la URL del vídeo de YouTube: ").strip()
            folder_name = input("Introduce el nombre de la carpeta para guardar las traducciones: ").strip()
            output_dir = Path('translations') / folder_name
            os.makedirs(output_dir, exist_ok=True)
            print("\n¿Qué deseas traducir?\n")
            print("1. Título, subtítulos y descripción")
            print("2. Solo título y subtítulos")
            print("3. Solo subtítulos")
            print("4. Solo título")
            print("5. Solo descripción")
            print("0. Cancelar\n")
            opt = input("Selecciona una opción (0-5): ").strip()
            if opt == '0':
                print("Operación cancelada.")
                continue
            # Obtener idioma base detectado
            try:
                video_info = app.youtube_client.get_video_info(url, preferred_lang=app.source_lang)
                detected_lang = video_info.get('original_language', app.source_lang)
                print(f"\n🌐 Idioma base detectado: {detected_lang}")
                resp = input("¿Es correcto este idioma base? (s/n): ").strip().lower()
                if resp != 's':
                    detected_lang = input("Introduce el código de idioma base correcto (por ejemplo, es, en, fr): ").strip().lower() or detected_lang
                app.source_lang = detected_lang
            except Exception as e:
                print(f"\n❌ Error al obtener información del vídeo: {e}")
                continue
            translate_title = opt in ['1', '2', '4']
            translate_subs = opt in ['1', '2', '3']
            translate_desc = opt in ['1', '5']
            processor = TranslationProcessor(app.youtube_client, output_dir, app.source_lang)
            try:
                result = processor.process_video_custom(url, translate_title, translate_subs, translate_desc)
                print("\n✅ Traducción completada. Archivos generados en:", output_dir)
                print("\nPuedes subir los resultados usando la opción 3 del menú.")
            except Exception as e:
                print(f"\n❌ Error al procesar el vídeo: {e}")
        # Opción 4: Descargar títulos, descripciones y subtítulos automáticos para revisión manual
        elif choice == '4':
            print("\n=== Descargar títulos, descripciones y subtítulos automáticos para revisión manual ===")
            url = input("Introduce la URL del vídeo de YouTube: ").strip()
            folder_name = input("Introduce el nombre de la carpeta para guardar la información base: ").strip()
            output_dir = Path('translations') / folder_name
            os.makedirs(output_dir / 'subtitles', exist_ok=True)
            try:
                video_info = app.youtube_client.get_video_info(url, preferred_lang=app.source_lang)
                lang = video_info.get('original_language', app.source_lang)
                print(f"\n🌐 Idioma base detectado: {lang}")
                resp = input("¿Es correcto este idioma base? (s/n): ").strip().lower()
                if resp != 's':
                    lang = input("Introduce el código de idioma base correcto (por ejemplo, es, en, fr): ").strip().lower() or lang
                # Guardar subtítulos
                subs = video_info['subtitles']
                srt_path = output_dir / 'subtitles' / f'original_{lang}.srt'
                with open(srt_path, 'w', encoding='utf-8') as f:
                    f.write(subs)
                print(f"\nSubtítulos automáticos descargados y guardados en: {srt_path}")
                # Guardar título
                title = video_info.get('original_title', '')
                titles_path = output_dir / 'original_title.txt'
                with open(titles_path, 'w', encoding='utf-8') as f:
                    f.write(title)
                print(f"\nTítulo original guardado en: {titles_path}")
                # Guardar descripción
                description = video_info.get('description', '')
                desc_path = output_dir / 'original_description.txt'
                with open(desc_path, 'w', encoding='utf-8') as f:
                    f.write(description)
                print(f"\nDescripción original guardada en: {desc_path}")
            except Exception as e:
                print(f"\n❌ Error al descargar información base: {e}")
        elif choice == '5':
            app.translate_from_manual_srt()
        elif choice == '6':
            print("Saliendo...")
            break
        elif choice == '7':
            try:
                app.change_base_language()
            except Exception as e:
                print(f"\n❌ Error al cambiar el idioma base: {e}")
        elif choice == '3':
            app.upload_from_existing_folder()
        else:
            print("\nOpción no válida. Intenta de nuevo.")
