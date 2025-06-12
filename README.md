# Y T R A N S L A T O R
 ▀  adhunt3rs   |   2025   |   V: 0.7  ▀

# YouTube Translator Tool — Guía de uso

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
       'Italiano': 'it',
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
   - Opción 1: Traducir vídeo
   - Opción 2: Autenticarse con YouTube
   - Opción 3: Subir traducciones desde carpeta existente
   - Opción 4: Descargar títulos, descripciones y subtítulos automáticos para revisión manual
   - Opción 5: Traducir y (opcionalmente) subir subtítulos a partir de un archivo SRT revisado
   - Opción 6: Salir

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
