import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload
from yt_dlp import YoutubeDL

def print_banner():
    print("""
██╗   ██╗████████╗██████╗  █████╗ ███╗   ██╗███████╗██╗      █████╗ ████████╗ ██████╗ ██████╗ 
╚██╗ ██╔╝╚══██╔══╝██╔══██╗██╔══██╗████╗  ██║██╔════╝██║     ██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗
 ╚████╔╝    ██║   ██████╔╝███████║██╔██╗ ██║███████╗██║     ███████║   ██║   ██║   ██║██████╔╝
  ╚██╔╝     ██║   ██╔══██╗██╔══██║██║╚██╗██║╚════██║██║     ██╔══██║   ██║   ██║   ██║██╔══██╗
   ██║      ██║   ██║  ██║██║  ██║██║ ╚████║███████║███████╗██║  ██║   ██║   ╚██████╔╝██║  ██║
   ╚═╝      ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝

        |   2025   |   V: 0.71   |   adhunt3rs   |   Hold your Unicorn   |
----------------------------------------------------------------------------------------------""")

print_banner()

LANGUAGES = {
    'es': {
        'main_title': "===== YouTube Translator & Uploader Tool =====",
        'main_menu': "\nMenú principal (idioma base actual: {lang}):\n\n"
                      "1. Traducir vídeo completo (título, subtítulos, descripción)\n"
                      "2. Descargar títulos, descripciones y subtítulos automáticos disponibles para revisar manualmente\n"
                      "3. Traducir y (opcionalmente) subir subtítulos a partir de un archivo SRT revisado\n"
                      "4. Subir traducciones desde carpeta existente\n"
                      "5. Autenticarse con YouTube\n"
                      "6. Cambiar/definir idioma del vídeo base\n"
                      "7. Elegir idioma de la interfaz\n"
                      "8. Salir\n",
        'choose_option': "Selecciona una opción (1-8): ",
        'interface_lang_changed': "\nIdioma de la interfaz cambiado a: {lang}\n",
        'select_interface_lang': "Select interface language:\n1. Spanish\n2. English\nOption: ",
        'invalid_option': "\nOpción no válida.\n",
        'exit': "\nSaliendo...\n",
        'operation_cancelled': "\nOperación cancelada.\n",
        'detected_base_lang': "\n🌐 Idioma base detectado: {lang}\n",
        'error_getting_video_info': "\n❌ Error al obtener información del vídeo: {error}\n",
        'translation_completed': "\n✅ Traducción completada. Archivos generados en: {output_dir}\n",
        'can_upload_results': "\nPuedes subir los resultados usando la opción 3 del menú.\n",
        'error_processing_video': "\n❌ Error al procesar el vídeo: {error}\n",
        'download_titles_desc_subs': "\n=== Descargar títulos, descripciones y subtítulos automáticos para revisión manual ===\n",
        'subs_downloaded': "\nSubtítulos automáticos descargados y guardados en: {srt_path}\n",
        'title_saved': "\nTítulo original guardado en: {titles_path}\n",
        'desc_saved': "\nDescripción original guardada en: {desc_path}\n",
        'error_downloading_base_info': "\n❌ Error al descargar información base: {error}\n",
        'error_changing_base_lang': "\n❌ Error al cambiar el idioma base: {error}\n",
        'invalid_option_retry': "\nOpción no válida. Intenta de nuevo.\n",
        'manual_srt_title': "\n=== Traducir y (opcionalmente) subir subtítulos a partir de un archivo SRT revisado ===\n",
        'subs_folder_not_found': "\nLa carpeta de subtítulos no existe. Descarga primero los subtítulos automáticos y revísalos.\n",
        'warn_base_lang_not_in_targets': "\n⚠️  [ADVERTENCIA] El código '{code}' no está en los idiomas de destino configurados. Si es correcto, continúa; si no, revisa la lista de códigos soportados en la documentación.\n",
        'no_original_srt_found': "\nNo se encontró ningún archivo original_*.srt en {subs_dir}. Asegúrate de haberlo revisado y guardado.\n",
        'file_not_found': "\nNo se encontró el archivo {srt_file}.\n",
        'available_original_files': "\nArchivos originales disponibles en la carpeta:\n",
        'translating_reviewed_subs': "\nTraduciendo subtítulos revisados a los idiomas configurados desde '{lang}'...\n",
        'subs_translation_done': "\nTraducción de subtítulos completada. Archivos generados:\n",
        'input_original_title': "\nIntroduce el título original del vídeo (en el idioma base, tal como debe aparecer en YouTube):\n",
        'title_empty_skip': "\nEl título no puede estar vacío. Se omite la traducción de título.\n",
        'translating_title': "\nTraduciendo título a los idiomas configurados...\n",
        'title_translation_done': "\nTraducción de título completada.\n",
        'generated_titles': "\nTítulos traducidos generados:\n",
        'what_upload_youtube': "\n¿Qué deseas subir a YouTube?\n",
        'upload_option_1': "1. Solo títulos/descripciones",
        'upload_option_2': "2. Solo subtítulos",
        'upload_option_3': "3. Ambos (títulos/descripciones y subtítulos)",
        'upload_option_0': "0. No subir nada ahora\n",
        'choose_upload_option': "Selecciona una opción (0-3): ",
        'can_upload_later': "\nPuedes subir los subtítulos y títulos más tarde usando la opción de subir desde carpeta existente.\n",
        'input_youtube_url_or_id': "Introduce la URL o el ID del vídeo de YouTube: ",
        'authenticating_youtube': "\nAutenticando con YouTube...\n",
        'upload_success': "\n¡Subida completada con éxito!\n",
        'upload_from_folder_title': "\nSubir traducciones desde carpeta existente\n",
        'input_folder_upload': "Introduce el nombre de la carpeta en 'translations/' con las traducciones listas para subir: ",
        'folder_not_found': "La carpeta {output_dir} no existe.",
        'no_valid_files_found': "\nNo se encontraron archivos de traducción válidos en la carpeta.\n",
        'summary_found_files': "\nResumen de archivos encontrados:\n",
        'found_titles': "- Títulos traducidos: {titles}\n",
        'found_descriptions': "- Descripciones traducidas: {descriptions}\n",
        'found_subtitles': "- Subtítulos: {subtitles}\n",
        'current_base_lang': "\nIdioma base actual: {lang}\n",
        'input_new_base_lang': "Introduce el nuevo código de idioma base (por ejemplo, es, en, fr): ",
        'warn_base_lang_not_supported': "\n⚠️  [ADVERTENCIA] El código '{code}' no está en la lista de idiomas soportados por Google Translate. Si es correcto, continúa; si no, revisa la lista de códigos soportados en la documentación.\n",
        'base_lang_changed': "\nIdioma base cambiado a: {lang}\n",
        'translator_using_googletrans': "\n[Traductor] Usando googletrans para {target_lang} (desde {source_lang})\n",
        'translator_using_fallback': "\n[Traductor] Usando fallback (API pública) para {target_lang} (desde {source_lang})\n",
        'translator_failed': "\n[Traductor] No se pudo traducir para {target_lang}, devolviendo original.\n",
        'translator_title_warn': "\n⚠️  [ADVERTENCIA] No se pudo traducir el título al idioma {lang_name} ({lang_code}) o la traducción es igual al original.\n",
        'translator_title_error': "\n❌  [ERROR] Falló la traducción del título a {lang_name} ({lang_code}): {error}\n",
        'translator_sub_warn': "\n⚠️  [ADVERTENCIA] No se pudo traducir un bloque al idioma {lang_code} o la traducción es igual al original.\n",
        'translator_sub_error': "\n❌  [ERROR] Falló la traducción de subtítulos a {lang_code}: {error}\n",
        'api_body_to_send': "\nCuerpo final que se enviará a la API (con truncado, descripción y localizations):\n",
        'api_response': "\nRespuesta de la API:\n",
        'api_uploaded_localizations': "\nTítulos y descripciones localizados subidos:\n",
        'api_uploaded_none': "\nNo se detectaron localizaciones subidas en la respuesta de la API.\n",
        'api_update_error': "\nError al actualizar con localizations:\n",
        'api_subtitle_exists': "\nYa existe una pista de subtítulos para {track_name} ({lang_code}). ¿Quieres sobrescribirla? (s/n): ",
        'api_subtitle_skip': "\nOmitiendo subida de subtítulos para {track_name} ({lang_code})\n",
        'api_subtitle_deleted': "\nPista de subtítulos existente para {track_name} ({lang_code}) eliminada.\n",
        'api_subtitle_uploading': "\nSubiendo subtítulos para {track_name} ({lang_code}): {file_path}\n",
        'api_subtitle_uploaded': "\nSubtítulos subidos correctamente para {track_name} ({lang_code})\n",
        'api_subtitle_upload_error': "\nError al subir subtítulos para {track_name} ({lang_code}): {error}\n",
        'api_get_subtitles_error': "\nNo se pudieron obtener las pistas de subtítulos existentes: {error}\n",
        'api_no_video_found': "\nNo se encontró el video con id {video_id}\n",
        'api_localization_exists': "\nYa existe una localización para el idioma {code} (título: '{title}').\n",
        'api_overwrite_localization': "¿Quieres sobrescribir el título/descripcion en {code}? (s/n): ",
        'input_folder_manual': "Introduce el nombre de la carpeta en 'translations/' con los subtítulos revisados:",
        'input_base_lang_or_auto': "Introduce el código de idioma base (por ejemplo, es, en, fr) o 'auto': ",
        'input_folder_name': "Introduce el nombre de la carpeta en 'translations/' para guardar los resultados:",
        'input_folder_name_base': "Introduce el nombre de la carpeta base en 'translations/':",
        'select_file_number': "Selecciona el número de archivo:",
        'input_title': "Introduce el título del vídeo:",
        'is_base_lang_correct': "¿Es correcto el idioma base detectado ({lang})? (s/n): ",
        'input_correct_base_lang': "Introduce el código correcto de idioma base (por ejemplo, es, en, fr): ",
        'no_auto_subtitles_found': "\nNo se encontraron subtítulos automáticos en el idioma base ni en ningún otro idioma disponible.\n",
        'no_description_found': "\nNo se encontró ninguna descripción para traducir.\n",
        'unsupported_base_lang_confirm': "El código '{code}' no está en la lista de idiomas soportados. ¿Deseas continuar? (s/n): ",
    },
    'en': {
        'main_title': "===== YouTube Translator & Uploader Tool =====",
        'main_menu': "\nMain menu (current base language: {lang}):\n\n"
                      "1. Translate full video (title, subtitles, description)\n"
                      "2. Download available titles, descriptions, and auto subtitles for manual review\n"
                      "3. Translate and (optionally) upload subtitles from a reviewed SRT file\n"
                      "4. Upload translations from existing folder\n"
                      "5. Authenticate with YouTube\n"
                      "6. Change/set base video language\n"
                      "7. Select interface language\n"
                      "8. Exit\n",
        'choose_option': "Choose an option (1-8): ",
        'interface_lang_changed': "\nInterface language changed to: {lang}\n",
        'select_interface_lang': "Select interface language:\n1. Spanish\n2. English\nOption: ",
        'invalid_option': "\nInvalid option.\n",
        'exit': "\nExiting...\n",
        'operation_cancelled': "\nOperation cancelled.\n",
        'detected_base_lang': "\n🌐 Detected base language: {lang}\n",
        'error_getting_video_info': "\n❌ Error getting video info: {error}\n",
        'translation_completed': "\n✅ Translation completed. Files generated in: {output_dir}\n",
        'can_upload_results': "\nYou can upload the results using option 3 in the menu.\n",
        'error_processing_video': "\n❌ Error processing video: {error}\n",
        'download_titles_desc_subs': "\n=== Download titles, descriptions and auto subtitles for manual review ===\n",
        'subs_downloaded': "\nAuto subtitles downloaded and saved in: {srt_path}\n",
        'title_saved': "\nOriginal title saved in: {titles_path}\n",
        'desc_saved': "\nOriginal description saved in: {desc_path}\n",
        'error_downloading_base_info': "\n❌ Error downloading base info: {error}\n",
        'error_changing_base_lang': "\n❌ Error changing base language: {error}\n",
        'invalid_option_retry': "\nInvalid option. Try again.\n",
        'manual_srt_title': "\n=== Translate and (optionally) upload subtitles from a reviewed SRT file ===\n",
        'subs_folder_not_found': "\nThe subtitles folder does not exist. Download the auto subtitles first and review them.\n",
        'warn_base_lang_not_in_targets': "\n⚠️  [WARNING] The code '{code}' is not in the configured target languages. If correct, continue; if not, check the supported codes in the documentation.\n",
        'no_original_srt_found': "\nNo original_*.srt file found in {subs_dir}. Make sure you have reviewed and saved it.\n",
        'file_not_found': "\nFile not found: {srt_file}.\n",
        'available_original_files': "\nOriginal files available in the folder:\n",
        'translating_reviewed_subs': "\nTranslating reviewed subtitles to configured languages from '{lang}'...\n",
        'subs_translation_done': "\nSubtitles translation completed. Files generated:\n",
        'input_original_title': "\nEnter the original video title (in the base language, as it should appear on YouTube):\n",
        'title_empty_skip': "\nTitle cannot be empty. Skipping title translation.\n",
        'translating_title': "\nTranslating title to configured languages...\n",
        'title_translation_done': "\nTitle translation completed.\n",
        'generated_titles': "\nGenerated translated titles:\n",
        'what_upload_youtube': "\nWhat do you want to upload to YouTube?\n",
        'upload_option_1': "1. Only titles/descriptions",
        'upload_option_2': "2. Only subtitles",
        'upload_option_3': "3. Both (titles/descriptions and subtitles)",
        'upload_option_0': "0. Do not upload now\n",
        'choose_upload_option': "Choose an option (0-3): ",
        'can_upload_later': "\nYou can upload subtitles and titles later using the upload from existing folder option.\n",
        'input_youtube_url_or_id': "Enter the YouTube video URL or ID: ",
        'authenticating_youtube': "\nAuthenticating with YouTube...\n",
        'upload_success': "\nUpload completed successfully!\n",
        'upload_from_folder_title': "\nUpload translations from existing folder\n",
        'input_folder_upload': "Enter the folder name in 'translations/' with the translations ready to upload: ",
        'folder_not_found': "Folder {output_dir} does not exist.",
        'no_valid_files_found': "\nNo valid translation files found in the folder.\n",
        'summary_found_files': "\nSummary of found files:\n",
        'found_titles': "- Translated titles: {titles}\n",
        'found_descriptions': "- Translated descriptions: {descriptions}\n",
        'found_subtitles': "- Subtitles: {subtitles}\n",
        'current_base_lang': "\nCurrent base language: {lang}\n",
        'input_new_base_lang': "Enter the new base language code (e.g., es, en, fr): ",
        'warn_base_lang_not_supported': "\n⚠️  [WARNING] The code '{code}' is not in the list of languages supported by Google Translate. If correct, continue; if not, check the supported codes in the documentation.\n",
        'base_lang_changed': "\nBase language changed to: {lang}\n",
        'translator_using_googletrans': "\n[Translator] Using googletrans for {target_lang} (from {source_lang})\n",
        'translator_using_fallback': "\n[Translator] Using fallback (public API) for {target_lang} (from {source_lang})\n",
        'translator_failed': "\n[Translator] Could not translate for {target_lang}, returning original.\n",
        'translator_title_warn': "\n⚠️  [WARNING] Could not translate the title to {lang_name} ({lang_code}) or translation is same as original.\n",
        'translator_title_error': "\n❌  [ERROR] Failed to translate title to {lang_name} ({lang_code}): {error}\n",
        'translator_sub_warn': "\n⚠️  [WARNING] Could not translate a block to {lang_code} or translation is same as original.\n",
        'translator_sub_error': "\n❌  [ERROR] Failed to translate subtitles to {lang_code}: {error}\n",
        'api_body_to_send': "\nBody to be sent to the API (truncated, description and localizations):\n",
        'api_response': "\nAPI response:\n",
        'api_uploaded_localizations': "\nLocalized titles and descriptions uploaded:\n",
        'api_uploaded_none': "\nNo uploaded localizations detected in the API response.\n",
        'api_update_error': "\nError updating with localizations:\n",
        'api_subtitle_exists': "\nA subtitle track already exists for {track_name} ({lang_code}). Overwrite? (y/n): ",
        'api_subtitle_skip': "\nSkipping upload of subtitles for {track_name} ({lang_code})\n",
        'api_subtitle_deleted': "\nExisting subtitle track for {track_name} ({lang_code}) deleted.\n",
        'api_subtitle_uploading': "\nUploading subtitles for {track_name} ({lang_code}): {file_path}\n",
        'api_subtitle_uploaded': "\nSubtitles uploaded successfully for {track_name} ({lang_code})\n",
        'api_subtitle_upload_error': "\nError uploading subtitles for {track_name} ({lang_code}): {error}\n",
        'api_get_subtitles_error': "\nCould not get existing subtitle tracks: {error}\n",
        'api_no_video_found': "\nNo video found with id {video_id}\n",
        'api_localization_exists': "\nA localization already exists for language {code} (title: '{title}').\n",
        'api_overwrite_localization': "Do you want to overwrite the title/description in {code}? (y/n): ",
        'input_folder_manual': "Enter the folder name in 'translations/' with the reviewed subtitles:",
        'input_base_lang_or_auto': "Enter the base language code (e.g., es, en, fr) or 'auto': ",
        'input_folder_name': "Enter the folder name in 'translations/' to save the results:",
        'input_folder_name_base': "Enter the base folder name in 'translations/':",
        'select_file_number': "Select the file number:",
        'input_title': "Enter the video title:",
        'is_base_lang_correct': "Is the detected base language correct ({lang})? (y/n): ",
        'input_correct_base_lang': "Enter the correct base language code (e.g., es, en, fr): ",
        'no_auto_subtitles_found': "\nNo automatic subtitles found in the base language or any other available language.\n",
        'no_description_found': "\nNo description found to translate.\n",
        'unsupported_base_lang_confirm': "The code '{code}' is not in the supported language list. Do you want to continue? (y/n): ",
    }
}

current_interface_lang = 'es'

# (Punto 6) Encapsular variable de idioma de interfaz para mayor robustez
class InterfaceConfig:
    def __init__(self, default_lang='es'):
        self._lang = default_lang
    @property
    def lang(self):
        return self._lang
    @lang.setter
    def lang(self, value):
        if value in LANGUAGES:
            self._lang = value
        else:
            self._lang = 'es'

interface_config = InterfaceConfig('es')

def tr(key, **kwargs):
    lang = getattr(interface_config, 'lang', 'es')
    msg = LANGUAGES.get(lang, LANGUAGES['es']).get(key)
    if msg is None:
        return key
    return msg.format(**kwargs)

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
                print(tr('translator_using_googletrans', target_lang=target_lang, source_lang=source_lang))
                self.cache[cache_key] = translated
                return translated
        except Exception as e:
            logger.warning(f"googletrans failed: {str(e)}")
        # Fallback a requests directo si googletrans falla
        try:
            translated = self._translate_with_fallback(text, target_lang, source_lang)
            if translated:
                print(tr('translator_using_fallback', target_lang=target_lang, source_lang=source_lang))
                self.cache[cache_key] = translated
                return translated
        except Exception as e:
            logger.error(f"Fallback translation failed: {str(e)}")
        print(tr('translator_failed', target_lang=target_lang))
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
        # Captura de error mejorada (punto 3)
        raise YouTubeServiceError(tr('no_auto_subtitles_found'))

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
        try:
            translated = self.client.translation_strategy.translate(title, lang_code, self.source_lang)
            if not translated or translated.strip() == "" or translated.strip() == title.strip():
                print(tr('translator_title_warn', lang_name=lang_name, lang_code=lang_code))
            return {'code': lang_code, 'title': translated}
        except Exception as e:
            print(tr('translator_title_error', lang_name=lang_name, lang_code=lang_code, error=str(e)))
            logger.error(f"Title translation error ({lang_name}): {str(e)}")
            raise

    def _translate_subtitles(self, subtitles: str, lang: str = 'es') -> Dict[str, Path]:
        """Translates subtitles to all target languages y añade original manual del idioma base."""
        results = {}
        subs_dir = self.output_dir / 'subtitles'
        os.makedirs(subs_dir, exist_ok=True)
        # Guardar siempre el archivo original antes de traducir (punto 4)
        original_path = subs_dir / f'original_{lang}.srt'
        with open(original_path, 'w', encoding='utf-8') as f:
            f.write(subtitles)
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
                            print(tr('translator_sub_warn', lang_code=lang_code))
                        # Mantener el mismo número de líneas que el bloque original para evitar desincronización
                        orig_lines = text_block.split('\n')
                        trans_lines = translated_text.split('\n')
                        if len(trans_lines) != len(orig_lines):
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
            print(tr('translator_sub_error', lang_code=lang_code, error=str(e)))
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
        if not description.strip():
            print(tr('no_description_found'))
            return {}
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
                if code in localizations:
                    # Fix 3: typo en key 'title,' -> 'title'
                    print(tr('api_localization_exists', code=code, title=localizations[code].get('title')))
                    # Fix 2: validación de respuesta según idioma
                    resp = input(tr('api_overwrite_localization', code=code)).strip().lower()
                    yes = 's' if globals().get('current_interface_lang', 'es') == 'es' else 'y'
                    if resp != yes:
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
        print(tr('api_body_to_send'))
        print(json.dumps(body, ensure_ascii=False, indent=2))
        try:
            response = self.service.videos().update(
                part="snippet,localizations",
                body=body
            ).execute()
            print(tr('api_response'))
            print(json.dumps(response, ensure_ascii=False, indent=2))
            if 'localizations' in response:
                print(tr('api_uploaded_localizations'))
                for code, loc in response['localizations'].items():
                    title = loc.get('title', '')
                    desc = loc.get('description', '')
                    print(f"  - [{code}] Título: {title}")
                    if desc:
                        print(f"    Descripción: {desc}")
            else:
                print(tr('api_uploaded_none'))
        except HttpError as e:
            print(tr('api_update_error'))
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
            cap_id = None
            for cap in existing_captions:
                snippet = cap.get('snippet', {})
                if snippet.get('language') == lang_code and snippet.get('name') == track_name:
                    cap_id = cap.get('id')
            if cap_id:
                resp = input(tr('api_subtitle_exists', track_name=track_name, lang_code=lang_code)).strip().lower()
                yes = 's' if globals().get('current_interface_lang', 'es') == 'es' else 'y'
                if resp != yes:
                    print(tr('api_subtitle_skip', track_name=track_name, lang_code=lang_code))
                    continue
                # Intentar borrar la pista existente
                try:
                    self.service.captions().delete(id=cap_id).execute()
                    print(tr('api_subtitle_deleted', track_name=track_name, lang_code=lang_code))
                except Exception as e:
                    logger.warning(f"No se pudo eliminar la pista existente: {str(e)}")
            print(tr('api_subtitle_uploading', track_name=track_name, lang_code=lang_code, file_path=file_path))
            try:
                media = MediaFileUpload(str(file_path), mimetype='application/octet-stream')
                self.service.captions().insert(
                    part="snippet",
                    body={
                        'snippet': {
                            'videoId': video_id,
                            'language': lang_code,
                            'name': track_name,
                            'isDraft': False
                        }
                    },
                    media_body=media
                ).execute()
                print(tr('api_subtitle_uploaded', track_name=track_name, lang_code=lang_code))
            except Exception as e:
                print(tr('api_subtitle_upload_error', track_name=track_name, lang_code=lang_code, error=str(e)))
                logger.error(f"Error uploading subtitles for {track_name} ({lang_code}): {str(e)}")
                continue

class YouTubeTranslatorApp:
    def __init__(self):
        self.translation_strategy = GoogleTranslateStrategy()
        self.youtube_client = YouTubeClient(self.translation_strategy)
        self.youtube_manager = YouTubeManager()
        self.source_lang = 'auto'

    def translate_from_manual_srt(self):
        print(tr('manual_srt_title'))
        folder_name = input(tr('input_folder_manual')).strip()
        output_dir = Path('translations') / folder_name
        subs_dir = output_dir / 'subtitles'
        if not subs_dir.exists():
            print(tr('subs_folder_not_found'))
            return
        # Preguntar idioma base
        source_lang = input(tr('input_base_lang_or_auto')).strip().lower() or 'auto'
        valid_langs = set([v.lower() for v in config.TARGET_LANGUAGES.values()])
        if source_lang != 'auto' and source_lang not in valid_langs:
            print(tr('warn_base_lang_not_in_targets', code=source_lang))
        self.source_lang = source_lang
        srt_file = subs_dir / f'original_{self.source_lang}.srt'
        if not srt_file.exists():
            disponibles = list(subs_dir.glob('original_*.srt'))
            if not disponibles:
                print(tr('no_original_srt_found', subs_dir=subs_dir))
                return
            print(tr('file_not_found', srt_file=srt_file))
            print(tr('available_original_files'))
            for idx, f in enumerate(disponibles, 1):
                print(f"  {idx}. {f.name}")
            sel = input(tr('select_file_number')).strip()
            if not sel.isdigit() or int(sel) < 1 or int(sel) > len(disponibles):
                print(tr('operation_cancelled'))
                return
            srt_file = disponibles[int(sel)-1]
            m = re.match(r'original_([a-zA-Z\-]+)\.srt', srt_file.name)
            if m:
                self.source_lang = m.group(1).lower()
        with open(srt_file, encoding='utf-8') as f:
            srt_content = f.read()
        print(tr('translating_reviewed_subs', lang=self.source_lang))
        processor = TranslationProcessor(self.youtube_client, output_dir, self.source_lang)
        translated_subs = processor._translate_subtitles(srt_content, self.source_lang)
        print(tr('subs_translation_done'))
        for lang, path in translated_subs.items():
            print(f"  - {lang}: {path}")
        print(tr('input_original_title'))
        original_title = input(tr('input_title')).strip()
        if not original_title:
            print(tr('title_empty_skip'))
            translated_titles = None
        else:
            print(tr('translating_title'))
            processor.source_lang = self.source_lang
            translated_titles = processor._translate_titles(original_title)
            print(tr('title_translation_done'))
            print(tr('generated_titles'))
            for lang, data in (translated_titles or {}).items():
                print(f"  - {lang}: {data.get('title','')}")
        if translated_titles:
            processor._save_translated_titles(original_title, translated_titles)
        print(tr('what_upload_youtube'))
        print(tr('upload_option_1'))
        print(tr('upload_option_2'))
        print(tr('upload_option_3'))
        print(tr('upload_option_0'))
        choice = input(tr('choose_upload_option')).strip()
        if choice == '0':
            print(tr('can_upload_later'))
            return
        upload_titles = choice in ['1', '3']
        upload_subs = choice in ['2', '3']
        if upload_titles or upload_subs:
            url = input(tr('input_youtube_url_or_id')).strip()
            if not self.youtube_manager.service:
                print(tr('authenticating_youtube'))
                self.youtube_manager.authenticate()
            self.youtube_manager.upload_translations_custom(
                url,
                translated_titles if upload_titles else None,
                translated_subs if upload_subs else None,
                None
            )
            print(tr('upload_success'))

    def upload_from_existing_folder(self):
        print(tr('upload_from_folder_title'))
        folder_name = input(tr('input_folder_upload')).strip()
        output_dir = Path('translations') / folder_name
        if not output_dir.exists():
            print(tr('folder_not_found', output_dir=output_dir))
            return
        titles_path = output_dir / 'translated_titles.json'
        titles = None
        if titles_path.exists():
            with open(titles_path, encoding='utf-8') as f:
                titles = json.load(f).get('translations')
        desc_path = output_dir / 'translated_descriptions.json'
        descriptions = None
        if desc_path.exists():
            with open(desc_path, encoding='utf-8') as f:
                descriptions = json.load(f)
        subs_dir = output_dir / 'subtitles'
        subtitles = {}
        if subs_dir.exists():
            for file in subs_dir.glob('translated_*.srt'):
                lang_code = file.stem.split('_', 1)[-1]
                subtitles[lang_code] = file
            for file in subs_dir.glob('original_*.srt'):
                lang_code = file.stem.split('_', 1)[-1]
                subtitles[lang_code] = file
        if not any([titles, descriptions, subtitles]):
            print(tr('no_valid_files_found'))
            return
        print(tr('summary_found_files'))
        if titles:
            print(tr('found_titles', titles=', '.join([f"{k} [{v.get('code','')}]" for k,v in titles.items()])))
        if descriptions:
            print(tr('found_descriptions', descriptions=', '.join(descriptions.keys())))
        if subtitles:
            print(tr('found_subtitles', subtitles=', '.join(subtitles.keys())))
        print(tr('what_upload_youtube'))
        print(tr('upload_option_1'))
        print(tr('upload_option_2'))
        print(tr('upload_option_3'))
        print(tr('upload_option_0'))
        sub_choice = input(tr('choose_upload_option')).strip()
        if sub_choice == '0':
            print(tr('operation_cancelled'))
            return
        upload_titles = sub_choice in ['1', '3']
        upload_subs = sub_choice in ['2', '3']
        url = input(tr('input_youtube_url_or_id')).strip()
        try:
            video_id = extract_video_id(url)
        except Exception as e:
            print(f"\n{e}\n")
            print(tr('operation_cancelled'))
            return
        if not self.youtube_manager.service:
            print(tr('authenticating_youtube'))
            self.youtube_manager.authenticate()
        self.youtube_manager.upload_translations_custom(
            video_id,
            titles if upload_titles else None,
            subtitles if upload_subs else None,
            descriptions if upload_titles else None
        )
        print(tr('upload_success'))

    def change_base_language(self):
        print(tr('current_base_lang', lang=self.source_lang))
        new_lang = input(tr('input_new_base_lang')).strip().lower()
        supported_langs = set([v.lower() for v in config.TARGET_LANGUAGES.values()])
        if new_lang not in supported_langs:
            resp = input(tr('unsupported_base_lang_confirm', code=new_lang)).strip().lower()
            yes = 's' if globals().get('current_interface_lang', 'es') == 'es' else 'y'
            if resp != yes:
                print(tr('operation_cancelled'))
                return
        self.source_lang = new_lang
        print(tr('base_lang_changed', lang=self.source_lang))

def extract_video_id(url_or_id: str) -> str:
    """Extrae el ID de un video de YouTube a partir de una URL o ID directa."""
    # Si ya es un ID (11 caracteres, letras/números, no contiene '/')
    if re.match(r'^[\w-]{11}$', url_or_id):
        return url_or_id
    # Extrae el ID de una URL estándar de YouTube
    match = re.search(r'(?:v=|youtu\.be/)([0-9A-Za-z_-]{11})', url_or_id)
    if match:
        return match.group(1)
    raise ValueError(f"No se pudo extraer el ID del vídeo de la entrada: {url_or_id}")

if __name__ == "__main__":
    print(tr('main_title'))
    app = YouTubeTranslatorApp()
    while True:
        print(tr('main_menu', lang=app.source_lang))
        choice = input(tr('choose_option')).strip()
        if choice == '8':
            print(tr('exit'))
            break
        elif choice == '7':
            print(tr('select_interface_lang'))
            lang_opt = input().strip()
            if lang_opt == '1':
                interface_config.lang = 'es'
                print(tr('interface_lang_changed', lang='Español'))
            elif lang_opt == '2':
                interface_config.lang = 'en'
                print(tr('interface_lang_changed', lang='English'))
            else:
                print(tr('invalid_option'))
            continue
        elif choice == '6':
            try:
                app.change_base_language()
            except Exception as e:
                print(tr('error_changing_base_lang', error=e))
        elif choice == '5':
            try:
                print(tr('authenticating_youtube'))
                app.youtube_manager.authenticate()
            except Exception as e:
                print(tr('error_processing_video', error=e))
        elif choice == '4':
            app.upload_from_existing_folder()
        elif choice == '3':
            app.translate_from_manual_srt()
        elif choice == '2':
            # Descargar títulos, descripciones y subtítulos automáticos para revisión manual
            print(tr('download_titles_desc_subs'))
            url = input(tr('input_youtube_url_or_id')).strip()  # <-- CORREGIDO: antes tr('input_youtube_url')
            folder_name = input(tr('input_folder_name_base')).strip()
            output_dir = Path('translations') / folder_name
            os.makedirs(output_dir, exist_ok=True)
            try:
                video_info = app.youtube_client.get_video_info(url, preferred_lang=app.source_lang)
                # Guardar subtítulos automáticos
                subs = video_info.get('subtitles', '')
                srt_path = output_dir / 'subtitles' / f"original_{video_info.get('original_language', app.source_lang)}.srt"
                os.makedirs(srt_path.parent, exist_ok=True)
                with open(srt_path, 'w', encoding='utf-8') as f:
                    f.write(subs)
                print(tr('subs_downloaded', srt_path=srt_path))
                # Guardar título
                title = video_info.get('original_title', '')
                titles_path = output_dir / 'original_title.txt'
                with open(titles_path, 'w', encoding='utf-8') as f:
                    f.write(title)
                print(tr('title_saved', titles_path=titles_path))
                # Guardar descripción
                description = video_info.get('description', '')
                desc_path = output_dir / 'original_description.txt'
                with open(desc_path, 'w', encoding='utf-8') as f:
                    f.write(description)
                print(tr('desc_saved', desc_path=desc_path))
            except Exception as e:
                print(tr('error_downloading_base_info', error=e))
        elif choice == '1':
            print(tr('translate_full_title'))
            url = input(tr('input_youtube_url')).strip()
            folder_name = input(tr('input_folder_name')).strip()
            output_dir = Path('translations') / folder_name
            os.makedirs(output_dir, exist_ok=True)
            print(tr('what_to_translate'))
            print(tr('option_1'))
            print(tr('option_2'))
            print(tr('option_3'))
            print(tr('option_4'))
            print(tr('option_5'))
            print(tr('option_0'))
            opt = input(tr('choose_what_to_translate')).strip()
            if opt == '0':
                print(tr('operation_cancelled'))
                continue
            # Obtener idioma base detectado
            try:
                video_info = app.youtube_client.get_video_info(url, preferred_lang=app.source_lang)
                detected_lang = video_info.get('original_language', app.source_lang)
                print(tr('detected_base_lang', lang=detected_lang))
                resp = input(tr('is_base_lang_correct')).strip().lower()
                if resp != 's':
                    detected_lang = input(tr('input_correct_base_lang')).strip().lower() or detected_lang
                app.source_lang = detected_lang
            except Exception as e:
                print(tr('error_getting_video_info', error=e))
                continue
            translate_title = opt in ['1', '2', '4']
            translate_subs = opt in ['1', '2', '3']
            translate_desc = opt in ['1', '5']
            processor = TranslationProcessor(app.youtube_client, output_dir, app.source_lang)
            try:
                result = processor.process_video_custom(url, translate_title, translate_subs, translate_desc)
                print(tr('translation_completed', output_dir=output_dir))
                print(tr('can_upload_results'))
            except Exception as e:
                print(tr('error_processing_video', error=e))
        else:
            print(tr('invalid_option_retry'))
