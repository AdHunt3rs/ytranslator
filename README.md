---

# YouTube Translator Tool — Guía de uso

## ¿Qué es este script?

Este script automatiza la traducción de títulos y subtítulos de videos de YouTube **desde ESPAÑOL** a los idiomas que elijas (configurados en `TARGET_LANGUAGES` dentro del script), y permite subir tanto los títulos traducidos como los subtítulos generados manualmente a tu canal de YouTube mediante la API oficial.

---

## Requisitos previos

- **Python 3.8 o superior**
- **Acceso a la API de YouTube** (requiere crear un proyecto en Google Cloud y descargar el archivo `client_secrets.json`)
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
   ```cmd
   python -m venv venv
   ```
3. Activa el entorno virtual en CMD:
   ```cmd
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
   ```cmd
   pip install -r requirements.txt
   ```
5. **Para salir del entorno virtual:**
   ```cmd
   deactivate
   ```

---

## Configuración de credenciales

1. **Crea un proyecto en Google Cloud**  
   Ve a [Google Cloud Console](https://console.cloud.google.com/), crea un proyecto y habilita la API de YouTube Data v3.

2. **Crea credenciales OAuth 2.0**  
   - Tipo de aplicación: **Escritorio**
   - Descarga el archivo y renómbralo a `client_secrets.json`
   - Colócalo en la misma carpeta que el script

---

## Configuración del script

1. **Idiomas de destino:**  
   Edita el diccionario `TARGET_LANGUAGES` en el script para elegir los idiomas a traducir. Ejemplo:

   ```python
   TARGET_LANGUAGES: Dict[str, str] = {
       'Inglés': 'en',
       'Italiano': 'it',
       # Agrega más si lo deseas
   }
   ```

2. **Opciones avanzadas:**  
   Puedes cambiar el número de hilos (`MAX_WORKERS`) o el directorio de salida (`DEFAULT_OUTPUT_DIR`) en la configuración.

---

## Uso paso a paso

1. **Ejecuta el script:**

   ```powershell
   python ytranslator.py
   ```

2. **Sigue el menú interactivo:**
   - Opción 1: Traducir video
   - Opción 2: Autenticarse con YouTube
   - Opción 3: Salir

3. **Para traducir y subir:**
   - Selecciona `1`
   - Introduce la URL del video de YouTube
   - Especifica el directorio de salida (o deja el valor por defecto)
   - Indica si deseas subir los resultados a YouTube (`y` para sí, `n` para no)

---

## Autenticación

La primera vez que subas títulos o subtítulos, el script abrirá una ventana del navegador para que autorices el acceso a tu cuenta de Google.  
**Debes autenticarte con la cuenta propietaria del canal de YouTube.**  
Se generará un archivo `token.json` que permite el acceso futuro sin repetir el proceso.

---

## ¿Qué hace el script?

1. Descarga los subtítulos automáticos en español del video.
2. Traduce el título y los subtítulos a los idiomas configurados.
3. Guarda los archivos traducidos en la carpeta de salida.
4. Sube los títulos traducidos como localizaciones del video (sin modificar el título original en español).
5. Sube los subtítulos traducidos como pistas manuales, con el nombre del idioma (ejemplo: "Inglés", "Español").
6. Sube también los subtítulos en español como pista manual, para asegurar su presencia aunque ya existan automáticos.

---

## Archivos generados

- `translated_titles.json`: Títulos traducidos.
- `subtitles/original_es.srt`: Subtítulos originales en español.
- `subtitles/translated_{lang}.srt`: Subtítulos traducidos a cada idioma.

---

## Notas y recomendaciones

- **No modifica el título original en español:** Solo añade traducciones en otros idiomas.
- **No fusiona título y subtítulo:** YouTube los gestiona como elementos separados.
- **Si subes varias veces una pista de subtítulos con el mismo nombre e idioma, YouTube dará error 409:** Borra la pista anterior si necesitas reemplazarla.
- **El script solo puede modificar videos de los que seas propietario** (no funciona con permisos de editor).
- **La calidad de la traducción depende de Google Translate:** Si necesitas traducción profesional, edita los subtítulos antes o integra otra API.

---

## Solución de problemas

- **Error 403/400 al subir:** Asegúrate de ser el propietario del video y de estar autenticado correctamente.
- **Error 409 al subir subtítulos:** Borra la pista anterior en YouTube Studio antes de volver a subir.
- **Traducción de baja calidad:** Edita los subtítulos originales antes de traducir o considera integrar una API de traducción profesional.

---

## Guía para autenticación por el dueño del canal

1. El dueño debe tener Python 3.8+ y el archivo `client_secrets.json`.
2. Ejecuta el script y selecciona la opción de autenticación.
3. Se abrirá el navegador para autorizar el acceso.
4. Se generará el archivo `token.json`.
5. Si otra persona va a operar el script, debe colocar el `token.json` en la misma carpeta que el script y el `client_secrets.json`.

**Seguridad:**  
El archivo `token.json` da acceso a la cuenta de YouTube para las acciones permitidas por la API. El dueño puede revocar el acceso en https://myaccount.google.com/permissions.

---

## Desinstalación y limpieza

1. **Eliminar el entorno virtual (si usaste uno):**
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
   - Carpetas de salida como `mio/`, `translations/`, etc.

4. **Revocar permisos de Google (opcional):**
   - Ve a https://myaccount.google.com/permissions y elimina el acceso de la app.

---

¿Dudas o problemas?  
Consulta el log `LOG_ytranslator.log` o contacta con el desarrollador.
