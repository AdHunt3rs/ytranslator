# Y T R A N S L A T O R
 ▀  adhunt3rs   |   2025   |   V: 0.71  ▀

<details>
<summary>ENGLISH VERSION HERE (click to expand)</summary>
# YouTube Translator & Uploader Tool — User Guide

## What is this script?

This script automates the translation and upload of YouTube video titles, subtitles, and descriptions **from any source language** to the languages you choose. The video's base language is auto-detected if possible, or you can set it manually. It allows you to upload the translated titles, subtitles, and descriptions to the YouTube video using the official API.

## What does the script do?

1. Downloads the automatic subtitles, title, and description in the **base language detected or set by the user** for the video.
2. Translates the title, subtitles, and/or description to the configured languages (according to your selection). The description is always translated to all selected languages from the original in the base language.
3. Saves the translated files in the corresponding folder under `translations/`.
4. Uploads the translated titles and descriptions as video localizations (without modifying the original title or description in the base language).
5. Uploads the translated subtitles as manual tracks, with the language name (e.g., "English", "Spanish").
6. Also uploads the subtitles in the base language as a manual track, to ensure their presence even if automatic ones already exist.

> **Note:** You can translate from any language supported by Google Translate. The base language is auto-detected, but you can correct it manually if needed.

---

## Prerequisites

- **Python 3.8 or higher**

- **Access to the YouTube API** (requires creating a project in Google Cloud and downloading the `client_secrets.json` file)

- **Video visibility:**
  - The video you want to upload translated titles and subtitles to must be **public** or **unlisted** on YouTube.
  - **It will NOT work with PRIVATE videos**: the YouTube API does not allow modifying titles or subtitles of private videos. If the video is private, first set it to public or unlisted, perform the upload, and then you can set it back to private if you wish.

- **Python dependencies:**
  - `googletrans==4.0.0rc1`
  - `yt-dlp`
  - `requests`
  - `google-auth`
  - `google-auth-oauthlib`
  - `google-api-python-client`

---

## Creating and activating a virtual environment (recommended)

1. **Open the CMD console as administrator** in the project folder (right-click > "Run as administrator").

2. Run to create the virtual environment:
   ```powershell
   python -m venv venv
   ```
3. Activate the virtual environment in CMD:
   ```powershell
   .\venv\Scripts\activate
   ```
   If using PowerShell:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   On Linux/Mac:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install the dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. **When finished with the script, to exit the virtual environment:**
   ```powershell
   deactivate
   ```

---

## Credentials setup

To allow the script to upload translations to YouTube, you need two files:

- **client_secrets.json:** OAuth 2.0 credentials file generated in Google Cloud (type "Desktop").
- **token.json:** File containing the authorized access to the YouTube account of the channel where translations will be uploaded.

### - If you are the owner of the YouTube channel where you will upload translations

1. **Create a project in Google Cloud**  
   Go to [Google Cloud Console](https://console.cloud.google.com/), create a project and enable the YouTube Data API v3. (You will need to navigate through the Google Cloud Console panels)

2. **Create OAuth 2.0 credentials**  
   - Application type: **Desktop**
   - Download the file and rename it to `client_secrets.json`
   - Place it in the same folder as the script

3. **Generate the `token.json` file**  
   - Run the script and select option 2 from the menu (authentication).
   - A browser window will open to log in and authorize access to your YouTube channel.
   - After accepting, the `token.json` file will be generated in the same folder.

Done! You can now use the script normally.

### - If you are NOT the owner of the channel (you operate on behalf of someone else to upload translations)

1. **The channel owner must generate both login files:**
   Following the steps above, they must do the process as if they were going to operate the script themselves.
   - `client_secrets.json` (must be associated with a project with the YouTube API enabled, as explained above)
   - `token.json` (generated after authenticating with their YouTube account using the script)

2. **The channel owner sends you the `token.json` file.**

3. **Place both files in the script folder:**
   - `client_secrets.json` (if you have already used the script, you should have it; it can be yours or the owner's if they send it to you, but it just needs to be associated with a project with the YouTube API enabled)
   - `token.json` (the one sent by the owner, this is the important file)

4. **You can now operate the script and upload translations to the owner's channel, acting on their behalf.**

> **Security note:** The `token.json` file gives access to the channel owner's YouTube account for the actions allowed by the API. The owner can revoke this access at any time from https://myaccount.google.com/permissions

---

## Target language configuration

1. **Target languages:**  
   Edit the `TARGET_LANGUAGES` dictionary in the script to choose the languages to translate to. 
   (To edit the code, any code editor is recommended. You can also run the script from there.)

   Example:

   ```python
   TARGET_LANGUAGES: Dict[str, str] = {
       'English': 'en',
       'Portuguese': 'pt',
       # Add more if you wish
   }
   ```
   The script already has **several languages listed but commented out**. You just need to comment or uncomment the lines of the languages you need (by adding or removing the `#` at the start of the line). You can also add other languages by including them in the correct format.

2. **Video base language:**  
   The script will try to auto-detect the video's base language (title, description, and subtitles). If it cannot detect it, it will ask you to specify it manually (for example: `es` for Spanish, `en` for English, etc). You can translate from any language supported by Google Translate.

3. **Advanced options:**  
   - `MAX_WORKERS`: controls the **number of threads** used to translate in parallel. A higher value speeds up translation if you have a good connection, but may increase the risk of blocks or quota limits on the API. If you have quota issues or too many translation errors, use a low value (e.g., 1 or 2) (`MAX_WORKERS: int = 3` by default).

---

## Step-by-step usage

1. **Run the script:**

   ```powershell
   python ytranslator.py
   ```

2. **Follow the interactive menu:**
   - Option 1: Translate full video (title, subtitles, description)
   - Option 2: Download available automatic titles, descriptions, and subtitles for manual review
   - Option 3: Translate and (optionally) upload subtitles from a reviewed SRT file
   - Option 4: Upload translations from an existing folder
   - Option 5: Authenticate with YouTube
   - Option 6: Change/set base video language
   - Option 7: Choose interface language
   - Option 8: Exit

> **Note:** When choosing the interface language, the options always appear as “1. Spanish” and “2. English”, regardless of the current language.

---

## Supported language codes
<details><summary>See list of common languages and codes (click to expand)</summary>
The script uses Google Translate language codes. You can check the full list of supported codes here:

- [Official list of Google Translate language codes (googletrans docs)](https://py-googletrans.readthedocs.io/en/latest/#googletrans-languages)
- [Quick reference table (Wikipedia)](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)

| Language      | Code    |
|-------------- |---------|
| Spanish       | es      |
| English       | en      |
| Italian       | it      |
| French        | fr      |
| German        | de      |
| Portuguese    | pt      |
| Russian       | ru      |
| Chinese (simp.)| zh-CN  |
| Chinese (trad.)| zh-TW  |
| Japanese      | ja      |
| Korean        | ko      |
| Arabic        | ar      |
| Hindi         | hi      |
| Turkish       | tr      |
| Polish        | pl      |
| Portuguese    | pt      |
| Dutch         | nl      |
| Swedish       | sv      |
| Greek         | el      |
| Czech         | cs      |
| Hungarian     | hu      |
| Romanian      | ro      |
| Danish        | da      |
| Norwegian     | no      |
| Finnish       | fi      |
| Hebrew        | iw      |
| Ukrainian     | uk      |
| Catalan       | ca      |
| Bulgarian     | bg      |
| Croatian      | hr      |
| Slovak        | sk      |
| Slovenian     | sl      |
| Estonian      | et      |
| Latvian       | lv      |
| Lithuanian    | lt      |
| Serbian       | sr      |
| Thai          | th      |
| Vietnamese    | vi      |
| Indonesian    | id      |
| Malay         | ms      |
| Filipino      | tl      |
| Persian       | fa      |
| Bengali       | bn      |
| Swahili       | sw      |

You can add or remove languages in the script's `TARGET_LANGUAGES` dictionary as needed.
</details>

---

## YouTube API quota usage

<details><summary>Details about YouTube Data API v3 quotas (click to expand)</summary>

The YouTube API has a quota system limited per project. Currently, each Google Cloud project has a limit of **10,000 quota units per day** (you can check and manage your quota in the [Google Cloud Console](https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas)).

- **When is quota consumed?**
  - **When retrieving video data** (e.g., to extract the original description if not available in the download): each API query (`videos.list` method) consumes **1 unit** per request.
  - **When uploading translated titles, descriptions, or subtitles** (`videos.update` and `captions.insert` methods): each upload consumes **50 units** per request.
  - **When authenticating** (first login): minimal consumption.

- **When is quota NOT consumed?**
  - **During translation**: translation of titles, subtitles, and descriptions is done locally using Google Translate (not the official Google Cloud API), so **it does not consume YouTube API quota**.
  - **When downloading automatic subtitles**: `yt-dlp` is used, not the YouTube API, so no quota is consumed.

**Recommendation:**
- If you have many videos or need to upload many translations, monitor your daily quota to avoid blocks.
- Uploading titles/descriptions/subtitles for many languages can consume several hundred units for a single video.
</details>

---

## Folder structure and generated files
<details><summary>What files does this script create? (click to expand)</summary>

- The script creates a log file `LOG_ytranslator.log` in the script's root folder.
- All translations and files related to a video are saved in `translations/FOLDER_NAME/`.
- Generated files:
  - `translated_titles.json`: Translated titles (if you choose to translate the title)
  - `translated_descriptions.json`: Translated descriptions (if you choose to translate the description; the original description in the base language is translated to all selected languages)
  - `subtitles/original_LANGUAGE.srt`: Original subtitles in the detected or set base language (e.g., `original_es.srt` for Spanish, `original_en.srt` for English, etc.)
  - `subtitles/translated_{lang}.srt`: Subtitles translated to each language (if you choose to translate subtitles)
  - `original_title.txt`: Original title in the detected or set base language
  - `original_description.txt`: Original description in the detected or set base language
> **You can edit the generated `.txt` and `.srt` files before translating or uploading, if you want to review or improve the content manually.**
</details>

---

## Troubleshooting

<details>
<summary>Troubleshooting (click to expand)</summary>

- **Error 403/400 when uploading:** Make sure you are the video owner and properly authenticated.
- **Error 409 when uploading subtitles:** Delete the previous track in YouTube Studio before uploading again.
- **Low translation quality:** Edit the original subtitles before translating or consider integrating a professional translation API.
</details>

<details>
<summary>Notes and recommendations (click to expand)</summary>

- **Does not modify the original title or description in Spanish:** Only adds translations in other languages.
- **Does not merge title and subtitle:** YouTube manages them as separate elements.
- **If you upload a subtitle track with the same name and language multiple times, YouTube will give error 409:** Delete the previous track if you need to replace it.
- **The script can only modify videos you own** (does not work with editor permissions).
- **Translation quality depends on Google Translate:** If you need professional translation, edit the original subtitles before translating or consider integrating another API.
</details>

---

## Uninstallation and cleanup

<details>
<summary>Uninstallation and cleanup (click to expand)</summary>

1. **Delete the virtual environment (if you used one):**
   - In Windows CMD:
     ```powershell
     rmdir /s /q venv
     ```
   - In PowerShell:
     ```powershell
     Remove-Item -Recurse -Force .\venv
     ```
   - In Linux/Mac:
     ```bash
     rm -rf venv
     ```

2. **Uninstall global dependencies (if installed without a virtual environment):**
   ```powershell
   pip uninstall googletrans yt-dlp requests google-auth google-auth-oauthlib google-api-python-client
   ```
   Or:
   ```powershell
   pip uninstall -r requirements.txt
   ```

3. **Delete project files and folders:**
   - `ytranslator.py`
   - `client_secrets.json`
   - `token.json`
   - `requirements.txt`
   - `LOG_ytranslator.log`
   - Output folders like `translations/`, etc.

4. **Revoke Google permissions (optional):**
   - Go to https://myaccount.google.com/permissions and remove the app's access.

</details>

---

## Questions or problems?  
Check the `LOG_ytranslator.log` in the script folder or contact me.

---

---

---

</details>

# YouTube Translator & Uploader Tool — Guía de uso

## ¿Qué es este script?

Este script automatiza la traducción y subida de títulos, subtítulos y descripciones de vídeos de YouTube **desde cualquier idioma base** a los idiomas que elijas. El idioma base del vídeo se autodetecta si es posible, o puedes elegirlo manualmente. Permite subir los títulos, subtítulos y descripciones traducidos al video de YouTube mediante la API oficial.

## ¿Qué hace el script?

1. Descarga los subtítulos automáticos, el título y la descripción en el **idioma base detectado o definido por el usuario** para el vídeo.
2. Traduce el título, los subtítulos y/o la descripción a los idiomas configurados (según lo que elijas). La descripción siempre se traduce a todos los idiomas seleccionados a partir de la original en el idioma base.
3. Guarda los archivos traducidos en la carpeta correspondiente bajo `translations/`.
4. Sube los títulos y descripciones traducidos como localizaciones del vídeo (sin modificar el título ni la descripción original en el idioma base).
5. Sube los subtítulos traducidos como pistas manuales, con el nombre del idioma (ejemplo: "Inglés", "Español").
6. Sube también los subtítulos en el idioma base como pista manual, para asegurar su presencia aunque ya existan automáticos.

> **Nota:** Puedes traducir desde cualquier idioma soportado por Google Translate. El idioma base se autodetecta, pero puedes corregirlo manualmente si es necesario.

---

## Requisitos previos

- **Python 3.8 o superior**

- **Acceso a la API de YouTube** (requiere crear un proyecto en Google Cloud y descargar el archivo `client_secrets.json`)

- **Visibilidad del vídeo:**
  - El vídeo al que quieras subir los títulos y subtítulos traducidos debe estar en modo **público** o en modo **oculto** en YouTube.

  - **NO funcionará con vídeos en modo PRIVADO**: la API de YouTube no permite modificar títulos ni subtítulos de vídeos privados. Si el vídeo está en privado, primero ponlo como público o en oculto, realiza la subida, y luego puedes volver a cambiarlo a privado si lo deseas.

- **Dependencias Python**:
  - `googletrans==4.0.0rc1`
  - `yt-dlp`
  - `requests`
  - `google-auth`
  - `google-auth-oauthlib`
  - `google-api-python-client`

---

## Crear y activar un entorno virtual (recomendado)

1. **Abre la consola CMD en modo administrador** en la carpeta del proyecto (clic derecho > "Ejecutar como administrador").

2. Ejecuta para crear el entorno virtual:
   ```powershell
   python -m venv venv
   ```
3. Activa el entorno virtual en CMD:
   ```powershell
   .\venv\Scripts\activate
   ```
   Si usas PowerShell:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   En Linux/Mac:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Instala las dependencias:
   ```powershell
   pip install -r requirements.txt
   ```
5. **Cuando termines con el script, para salir del entorno virtual:**
   ```powershell
   deactivate
   ```

---

## Configuración de credenciales

Para que el script pueda subir traducciones a YouTube, necesitas dos archivos:

- **client_secrets.json:** Archivo de credenciales OAuth 2.0 generado en Google Cloud (tipo "Escritorio").
- **token.json:** Archivo que contiene el acceso autorizado a la cuenta de YouTube del canal donde se subirán las traducciones.

### - Si eres el dueño del canal de Youtube donde vas a subir las traducciones

1. **Crea un proyecto en Google Cloud**  
   Ve a [Google Cloud Console](https://console.cloud.google.com/), crea un proyecto y habilita la API de YouTube Data v3. (Vas a tener que buscar por los paneles de google cloud console)

2. **Crea credenciales OAuth 2.0**  
   - Tipo de aplicación: **Escritorio**
   - Descarga el archivo y renómbralo a `client_secrets.json`
   - Colócalo en la misma carpeta que el script

3. **Genera el archivo `token.json`**  
   - Ejecuta el script y selecciona la opción 2 del menú (autenticación).
   - Se abrirá una ventana del navegador para iniciar sesión y autorizar el acceso a tu canal de YouTube.
   - Tras aceptar, se generará el archivo `token.json` en la misma carpeta.

¡Listo! Ya puedes usar el script normalmente.

### - Si NO eres el dueño del canal (operas en nombre de otra persona para subir las traducciones)

1. **El dueño del canal debe generar ambos archivos de login:**
 Siguiendo los pasos de la sección anterior, debe hacer el proceso como si fuera a operar él mismo el script.
   - `client_secrets.json` (debe estar asociado a un proyecto con la API de YouTube habilitada, antes expliqué como crearlo y descargarlo, vas a tener que buscar por los paneles de google cloud console).
   - `token.json` (se genera tras autenticarse con su cuenta de YouTube usando el script).

2. **El dueño del canal te envía el archivo `token.json`.**

3. **Colocas ambos archivos en la carpeta del script:**
   - `client_secrets.json` (si ya has usado el script, deberías tenerlo, puede ser tuyo o el del dueño si te lo envía, aunque no es necesario. Sólo debe estar asociado a un proyecto con la API de Youtube habilitada.)
   - `token.json` (el que te envió el dueño, este es el archivo importante)

4. **Ahora puedes operar el script y subir traducciones al canal del dueño, actuando en su nombre.**

> **Nota de seguridad:** El archivo `token.json` da acceso a la cuenta de YouTube del dueño del canal para las acciones permitidas por la API. El dueño puede revocar este acceso en cualquier momento desde https://myaccount.google.com/permissions

---

## Configuración de idomas de destino

1. **Idiomas de destino:**  
   Edita el diccionario `TARGET_LANGUAGES` en el script para elegir los idiomas a traducir. 
   (Para editar el código, recomiendo usar cualquier editor de código. Así también podrás ejecutar el script desde ahí mismo)

   Ejemplo:

   ```python
   TARGET_LANGUAGES: Dict[str, str] = {
       'Inglés': 'en',
       'Portugués': 'pt',
       # Agrega más si lo deseas
   }
   ```
   En el script ya hay **varios idiomas listados pero comentados**. Solo tienes que comentar o descomentar las líneas de los idiomas que necesites (poniendo o quitando el símbolo `#` al inicio de la línea). También puedes añadir otros idiomas incluyéndolos en el formato adecuado.

2. **Idioma base del vídeo:**  
   El script intentará autodetectar el idioma base del vídeo (título, descripción y subtítulos). Si no puede detectarlo, te pedirá que lo indiques manualmente (por ejemplo: `es` para español, `en` para inglés, etc). Puedes traducir desde cualquier idioma soportado por Google Translate.

3. **Opciones avanzadas:**  
   - `MAX_WORKERS`: controla el **número de hilos** que se usan para traducir en paralelo. Un valor mayor acelera la traducción si tienes buena conexión, pero puede aumentar el riesgo de bloqueos o límites de cuota en la API. Si tienes problemas de cuota o demasiados errores al traducir, usa un valor bajo (por ejemplo, 1 o 2) (`MAX_WORKERS: int = 3` por defecto).

---

## Uso paso a paso

1. **Ejecuta el script:**

   ```powershell
   python ytranslator.py
   ```

2. **Sigue el menú interactivo:**
   - Opción 1: Traducir vídeo completo (título, subtítulos, descripción)
   - Opción 2: Descargar títulos, descripciones y subtítulos automáticos disponibles para revisar manualmente
   - Opción 3: Traducir y (opcionalmente) subir subtítulos a partir de un archivo SRT revisado
   - Opción 4: Subir traducciones desde carpeta existente
   - Opción 5: Autenticarse con YouTube
   - Opción 6: Cambiar/definir idioma del vídeo base
   - Opción 7: Elegir idioma de la interfaz
   - Opción 8: Salir

> **Nota:** Al elegir el idioma de la interfaz, las opciones siempre aparecen como “1. Spanish” y “2. English”, independientemente del idioma actual.

---

## Códigos de idioma soportados
<details><summary>Ver lista de idiomas y códigos comunes (clic para desplegar)</summary>
El script utiliza los códigos de idioma de Google Translate. Puedes consultar la lista completa de códigos soportados aquí:

- [Lista oficial de códigos de idioma de Google Translate (documentación de googletrans)](https://py-googletrans.readthedocs.io/en/latest/#googletrans-languages)
- [Tabla rápida de referencia (Wikipedia)](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)




| Idioma        | Código  |
|-------------- |---------|
| Español       | es      |
| Inglés        | en      |
| Italiano      | it      |
| Francés       | fr      |
| Alemán        | de      |
| Portugués     | pt      |
| Ruso          | ru      |
| Chino (simpl.)| zh-CN   |
| Chino (trad.) | zh-TW   |
| Japonés       | ja      |
| Coreano       | ko      |
| Árabe         | ar      |
| Hindi         | hi      |
| Turco         | tr      |
| Polaco        | pl      |
| Portugués     | pt      |
| Neerlandés    | nl      |
| Sueco         | sv      |
| Griego        | el      |
| Checo         | cs      |
| Húngaro       | hu      |
| Rumano        | ro      |
| Danés         | da      |
| Noruego       | no      |
| Finés         | fi      |
| Hebreo        | iw      |
| Ucraniano     | uk      |
| Catalán       | ca      |
| Búlgaro       | bg      |
| Croata        | hr      |
| Eslovaco      | sk      |
| Esloveno      | sl      |
| Estonio       | et      |
| Letón         | lv      |
| Lituano       | lt      |
| Serbio        | sr      |
| Tailandés     | th      |
| Vietnamita    | vi      |
| Indonesio     | id      |
| Malayo        | ms      |
| Filipino      | tl      |
| Persa         | fa      |
| Bengalí       | bn      |
| Swahili       | sw      |



Puedes añadir o quitar idiomas en el diccionario `TARGET_LANGUAGES` del script según tus necesidades.
</details>

---

## Uso de cuotas de la API de YouTube

<details><summary>Detalles sobre las cuotas de Youtube Data API v3 (click para desplegar)</summary>

La API de YouTube tiene un sistema de cuotas limitado por proyecto. Actualmente, cada proyecto de Google Cloud tiene un límite de **10,000 unidades de cuota al día** (puedes consultar y gestionar tu cuota en la [consola de Google Cloud](https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas)).

- **¿Cuándo se consumen cuotas?**
  - **Al obtener datos del vídeo** (por ejemplo, para extraer la descripción original si no está disponible en la descarga): cada consulta a la API (método `videos.list`) consume **1 unidad** por petición.
  - **Al subir títulos, descripciones o subtítulos traducidos** (método `videos.update` y `captions.insert`): cada subida consume **50 unidades** por petición.
  - **Al autenticarte** (primer login): consumo mínimo.

- **¿Cuándo NO se consumen cuotas?**
  - **Durante la traducción**: la traducción de títulos, subtítulos y descripciones se realiza localmente usando Google Translate (no la API oficial de Google Cloud), por lo que **no consume cuota de la API de YouTube**.
  - **Al descargar subtítulos automáticos**: se usa `yt-dlp` y no la API de YouTube, por lo que no consume cuota.

**Recomendación:**
- Si tienes muchos vídeos o necesitas subir muchas traducciones, vigila tu cuota diaria para evitar bloqueos.
- Subir títulos/descripciones/subtítulos para muchos idiomas puede consumir varias centenas de unidades en un solo vídeo.
</details>

---

## Estructura de carpetas y archivos generados
<details><summary>Qué archivos crea este script (click para desplegar)</summary>

- El script crea un archivo de log `LOG_ytranslator.log` en la carpeta raíz del script.
- Todas las traducciones y archivos relacionados con un vídeo se guardan en `translations/NOMBRE_CARPETA/`.
- Archivos generados:
  - `translated_titles.json`: Títulos traducidos (si se elige traducir título)
  - `translated_descriptions.json`: Descripciones traducidas (si se elige traducir descripción; se traduce la descripción original en el idioma base a todos los idiomas seleccionados)
  - `subtitles/original_IDIOMA.srt`: Subtítulos originales en el idioma base detectado o definido (por ejemplo, `original_es.srt` para español, `original_en.srt` para inglés, etc.)
  - `subtitles/translated_{lang}.srt`: Subtítulos traducidos a cada idioma (si se elige traducir subtítulos)
  - `original_title.txt`: Título original en el idioma base detectado o definido
  - `original_description.txt`: Descripción original en el idioma base detectado o definido
> **Puedes editar los archivos `.txt` y `.srt` generados antes de traducir o subir, si deseas revisar o mejorar el contenido manualmente.**
</details>

---

## Solución de problemas

<details>
<summary>Solución de problemas (clic para desplegar)</summary>

- **Error 403/400 al subir:** Asegúrate de ser el propietario del vídeo y de estar autenticado correctamente.
- **Error 409 al subir subtítulos:** Borra la pista anterior en YouTube Studio antes de volver a subir.
- **Traducción de baja calidad:** Edita los subtítulos originales antes de traducir o considera integrar una API de traducción profesional.
</details>

<details>
<summary>Notas y recomendaciones (clic para desplegar)</summary>

- **No modifica el título ni la descripción original en español:** Solo añade traducciones en otros idiomas.
- **No fusiona título y subtítulo:** YouTube los gestiona como elementos separados.
- **Si subes varias veces una pista de subtítulos con el mismo nombre e idioma, YouTube dará error 409:** Borra la pista anterior si necesitas reemplazarla.
- **El script solo puede modificar vídeos de los que seas propietario** (no funciona con permisos de editor).
- **La calidad de la traducción depende de Google Translate:** Si necesitas traducción profesional, edita los subtítulos originales antes de traducir o considera integrar otra API.
</details>

---

## Desinstalación y limpieza

<details>
<summary>Desinstalación y limpieza (clic para desplegar)</summary>

1. **Eliminar el entorno virtual (si usaste uno):**
   - En CMD de Windows:
     ```powershell
     rmdir /s /q venv
     ```
   - En PowerShell:
     ```powershell
     Remove-Item -Recurse -Force .\venv
     ```
   - En Linux/Mac:
     ```bash
     rm -rf venv
     ```

2. **Desinstalar dependencias globales (si las instalaste sin entorno virtual):**
   ```powershell
   pip uninstall googletrans yt-dlp requests google-auth google-auth-oauthlib google-api-python-client
   ```
   O bien:
   ```powershell
   pip uninstall -r requirements.txt
   ```

3. **Borrar archivos y carpetas del proyecto:**
   - `ytranslator.py`
   - `client_secrets.json`
   - `token.json`
   - `requirements.txt`
   - `LOG_ytranslator.log`
   - Carpetas de salida como `translations/`, etc.

4. **Revocar permisos de Google (opcional):**
   - Ve a https://myaccount.google.com/permissions y elimina el acceso de la app.

</details>

---

## ¿Dudas o problemas?  
Consulta el log `LOG_ytranslator.log` en la carpeta donde está el script o contacta conmigo.

---
