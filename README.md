# Y T R A N S L A T O R
 ▀  adhunt3rs   |   2025   |   V: 0.7  ▀

# YouTube Translator Tool — Guía de uso

## Cambios importantes (junio 2025)

- **Selección de idioma base flexible:** Ahora el script autodetecta el idioma base del vídeo (si es posible) o te permite elegirlo manualmente. Puedes traducir desde cualquier idioma soportado por Google Translate, no solo desde español.
- **Conservación de localizaciones existentes:** Al subir títulos y descripciones traducidos, el script conserva todos los idiomas ya presentes en el vídeo. Si intentas añadir una traducción para un idioma que ya existe, el script te preguntará si quieres sobrescribir el título y/o descripción de ese idioma.
- **Nunca se pierden localizaciones previas:** Solo se actualizan los idiomas que elijas y confirmes, el resto permanece intacto.
- **Traducción y subida selectiva desde SRT revisado:** Puedes elegir si subir solo títulos/descripciones, solo subtítulos, o ambos. El script pregunta antes de sobrescribir cualquier pista o localización existente.
- **Previsualización de títulos traducidos:** Antes de subir, el script muestra por consola los títulos generados para que puedas revisarlos.
- **Control total sobre la subida:** Tras traducir, puedes decidir si subir o no los resultados, y se te pedirá la URL/ID del vídeo si decides subir.
- **Menú interactivo ampliado:** Nuevas opciones para descargar solo subtítulos, traducir/subir desde SRT revisado, y subir desde carpeta existente.
- **Organización en carpetas:** Todos los archivos generados se guardan bajo `translations/NOMBRE_CARPETA/` para cada vídeo.
- **Logs y advertencias mejorados:** El script informa de cada paso, errores y advertencias relevantes.

---

## Aclaraciones importantes sobre el flujo de subida

- **Después de traducir:** El script siempre te preguntará si deseas subir los resultados a YouTube. Puedes cancelar en ese momento y conservar solo los archivos generados en la carpeta correspondiente.
- **Si decides subir:** Se te pedirá la URL o el ID del vídeo de YouTube al que quieres subir las traducciones (puedes copiarla directamente desde YouTube).
- **Previsualización antes de subir:** Los títulos traducidos generados se mostrarán por consola antes de la subida, para que puedas revisarlos y confirmar si deseas continuar.
- **Control total:** Puedes elegir subir solo títulos/descripciones, solo subtítulos, o ambos (especialmente al trabajar desde un SRT revisado).
- **Sobrescritura controlada:** Si ya existen localizaciones o pistas de subtítulos para un idioma, el script te preguntará si deseas sobrescribirlas.

---

# YouTube Translator Tool — Guía de uso

## ¿Qué es este script?

Este script automatiza la traducción de títulos, subtítulos y descripciones de vídeos de YouTube **desde cualquier idioma base** a los idiomas que elijas (configurados en `TARGET_LANGUAGES` dentro del script). El idioma base se autodetecta si es posible, o puedes elegirlo manualmente. Permite subir tanto los títulos, subtítulos y descripciones traducidos a tu canal de YouTube mediante la API oficial.

> **Nota:** Ya no es obligatorio que el idioma base sea español. Puedes traducir desde cualquier idioma soportado por Google Translate.

---

## Códigos de idioma soportados

El script utiliza los códigos de idioma de Google Translate. Puedes consultar la lista completa de códigos soportados aquí:

- [Lista oficial de códigos de idioma de Google Translate (documentación de googletrans)](https://py-googletrans.readthedocs.io/en/latest/#googletrans-languages)
- [Tabla rápida de referencia (Wikipedia)](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)

<details>
<summary>Ver lista de idiomas y códigos comunes (clic para desplegar)</summary>

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

</details>

Puedes añadir o quitar idiomas en el diccionario `TARGET_LANGUAGES` del script según tus necesidades.

---

## Uso de cuotas de la API de YouTube

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

---

## Requisitos previos

- **Python 3.8 o superior**
- **Acceso a la API de YouTube** (requiere crear un proyecto en Google Cloud y descargar el archivo `client_secrets.json`)
- **Visibilidad del vídeo:**
  - El vídeo al que quieras subir los títulos y subtítulos traducidos debe estar en modo **público** o **oculto/no listado** en YouTube.
  - **No funcionará con vídeos en modo privado**: la API de YouTube no permite modificar títulos ni subtítulos de vídeos privados. Si el vídeo está en privado, primero ponlo como público o no listado, realiza la subida, y luego puedes volver a cambiarlo a privado si lo deseas.
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
5. **Para salir del entorno virtual:**
   ```powershell
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
   En el script ya hay **varios idiomas listados pero comentados**. Solo tienes que comentar o descomentar las líneas de los idiomas que necesites (poniendo o quitando el símbolo `#` al inicio de la línea). También puedes añadir otros idiomas incluyéndolos en el formato adecuado.

2. **Idioma base del vídeo:**  
   El script intentará autodetectar el idioma base del vídeo (título, descripción y subtítulos). Si no puede detectarlo, te pedirá que lo indiques manualmente (por ejemplo: `es` para español, `en` para inglés, etc). Puedes traducir desde cualquier idioma soportado por Google Translate.

3. **Opciones avanzadas:**  
   - `MAX_WORKERS`: controla el **número de hilos** que se usan para traducir en paralelo. Un valor mayor acelera la traducción si tienes buena conexión, pero puede aumentar el riesgo de bloqueos o límites de cuota en la API. Si tienes problemas de cuota, usa un valor bajo (por ejemplo, 2 o 3).

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

3. **Para traducir y subir:**
   - Selecciona `1`
   - Introduce la URL del vídeo de YouTube
   - El script autodetectará el idioma base o te pedirá que lo indiques
   - Elige qué deseas traducir: título, subtítulos, descripción, o cualquier combinación de ellos
   - Introduce un nombre de carpeta (obligatorio) para guardar los resultados bajo la carpeta `translations/` (por ejemplo: `video_matematicas_2025`)
   - Indica si deseas subir los resultados a YouTube (`y` para sí, `n` para no)

**Importante:** Cada vídeo debe tener su propia carpeta bajo `translations/` para mantener organizadas las traducciones. Si la carpeta ya existe, el script la reutilizará.

4. **Para descargar títulos, descripciones y subtítulos automáticos en el idioma base:**
   - Selecciona `4`
   - Introduce la URL del vídeo de YouTube
   - Indica el nombre de la carpeta para guardar los subtítulos
   - Se guardarán el archivo `original_{lang}.srt` en la subcarpeta `subtitles/`, el título en `original_title.txt` y la descripción en `original_description.txt` para su revisión manual.

5. **Para traducir y (opcionalmente) subir subtítulos a partir de un archivo SRT revisado:**
   - Selecciona `5`
   - Indica la carpeta donde está el archivo `original_IDIOMA.srt` revisado
   - Elige si deseas subir los subtítulos traducidos a YouTube en ese momento

---

## Estructura de carpetas y archivos generados

- Todas las traducciones y archivos relacionados con un vídeo se guardan en `translations/NOMBRE_CARPETA/`.
- Archivos generados:
  - `translated_titles.json`: Títulos traducidos (si se elige traducir título)
  - `translated_descriptions.json`: Descripciones traducidas (si se elige traducir descripción; se traduce la descripción original en el idioma base a todos los idiomas seleccionados)
  - `subtitles/original_IDIOMA.srt`: Subtítulos originales en el idioma base (por ejemplo, `original_es.srt` para español)
  - `subtitles/translated_{lang}.srt`: Subtítulos traducidos a cada idioma (si se elige traducir subtítulos)

---

## ¿Qué hace el script?

1. Descarga los subtítulos automáticos en el idioma base del vídeo.
2. Traduce el título, los subtítulos y/o la descripción a los idiomas configurados (según lo que elijas). La descripción siempre se traduce a todos los idiomas seleccionados a partir de la original en el idioma base.
3. Guarda los archivos traducidos en la carpeta correspondiente bajo `translations/`.
4. Sube los títulos y descripciones traducidos como localizaciones del vídeo (sin modificar el título ni la descripción original en el idioma base).
5. Sube los subtítulos traducidos como pistas manuales, con el nombre del idioma (ejemplo: "Inglés", "Español").
6. Sube también los subtítulos en el idioma base como pista manual, para asegurar su presencia aunque ya existan automáticos.

---

## ¿Cómo se gestionan las traducciones y por qué?

El script **no modifica el título ni la descripción original en el idioma base** del vídeo en YouTube. En su lugar, añade traducciones como "localizaciones" para cada idioma que elijas. Así, los usuarios verán el título, la descripción y los subtítulos en su idioma preferido si existe traducción, pero el contenido original siempre se conserva.

### Traducción de subtítulos: sincronización y coherencia
- **Traducción por bloques SRT completos:** Cada bloque de subtítulo (es decir, cada entrada numerada con su tiempo y texto) se traduce como una sola unidad, no línea por línea. Esto mejora la coherencia y el sentido de las frases traducidas.
- **Sincronización:** Tras la traducción, el script ajusta el texto traducido para que conserve el mismo número de líneas que el bloque original, repartiendo el texto si es necesario. Así se mantiene la sincronización y el formato del subtítulo, evitando desfases en la visualización.
- **Ventaja:** Este método evita errores de sentido y mantiene la correspondencia temporal de los subtítulos, a diferencia de la traducción línea a línea que puede romper frases o desincronizar el resultado.

### Traducción de títulos y descripciones
- El título y la descripción se traducen como textos completos a todos los idiomas configurados.
- **Importante:** Cuando el programa te pide que introduzcas el título que quieres traducir (por ejemplo, al trabajar desde un SRT revisado), este texto **solo se usa como base para las traducciones**. El título original del vídeo en YouTube **no se modifica nunca**; solo se añaden las traducciones como localizaciones adicionales.

### ¿Por qué funciona así?
- YouTube permite añadir múltiples localizaciones (títulos y descripciones) para un mismo vídeo, asociadas a diferentes idiomas.
- Esto garantiza que el vídeo sea más accesible internacionalmente, sin perder el contenido original.
- Si ya existe una traducción para un idioma, el script te preguntará si deseas sobrescribirla, evitando perder traducciones previas.
- Los subtítulos también se suben como pistas separadas para cada idioma, y puedes elegir si sobrescribir los existentes.

**Ventajas de este enfoque:**
- Conserva siempre el contenido original.
- Permite añadir o actualizar solo los idiomas que desees, sin afectar los demás.
- Puedes revisar y corregir las traducciones antes de subirlas.
- Si subes varias veces, solo se actualizan los idiomas que elijas y confirmes.

> **Nota:** Si decides no subir inmediatamente, puedes revisar los archivos generados en la carpeta `translations/NOMBRE_CARPETA/` y subirlos más tarde desde el menú del script.

---

## NUEVAS FUNCIONALIDADES (junio 2025)

### 1. Descargar solo subtítulos automáticos en español para revisión manual
- Desde el menú interactivo, elige la opción:
  **4. Descargar solo subtítulos automáticos en español para revisión manual**
- Introduce la URL del vídeo y el nombre de la carpeta.
- El archivo `original_es.srt` se guardará en `translations/NOMBRE_CARPETA/subtitles/`.
- Puedes abrir y editar este archivo manualmente para corregir errores antes de traducir o subir.

### 2. Traducir y (opcionalmente) subir subtítulos, títulos y descripciones a partir de un archivo SRT revisado
- Desde el menú interactivo, elige la opción:
  **5. Traducir y (opcionalmente) subir subtítulos a partir de un archivo SRT revisado**
- Indica la carpeta donde está el SRT revisado (`original_es.srt`).
- El script te pedirá el título original en español (tal como debe aparecer en YouTube).
- El script traducirá ese archivo y el título a todos los idiomas configurados y guardará los resultados en la misma carpeta.
- **Podrás elegir si subir solo títulos/descripciones, solo subtítulos, o ambos.**
- Si decides subir subtítulos y ya existe una pista para ese idioma, el script preguntará si deseas sobrescribirla (y eliminará la anterior si aceptas).
- Puedes elegir si subir los resultados a YouTube en ese momento, o hacerlo después usando la opción de subir desde carpeta existente.

### Menú interactivo actualizado

1. Traducir vídeo
2. Autenticarse con YouTube
3. Subir traducciones desde carpeta existente
4. Descargar títulos, descripciones y subtítulos automáticos para revisión manual
5. Traducir y (opcionalmente) subir subtítulos a partir de un archivo SRT revisado
6. Salir

### Flujo recomendado para revisión manual de subtítulos y título

1. Usa la opción 4 para descargar los subtítulos automáticos en español.
2. Revisa y corrige el archivo `original_es.srt` manualmente (puedes usar Aegisub, Subtitle Edit, Notepad++, etc).
3. Usa la opción 5 para traducir el archivo revisado **y el título** a los idiomas deseados y, si quieres, subirlos a YouTube.

### Subida de traducciones y respeto a idiomas existentes
- Al subir títulos, descripciones o subtítulos, el script detecta los idiomas ya presentes en el vídeo y **solo añade o sobrescribe los nuevos**.
- Si un idioma ya existe, el script pregunta si deseas sobrescribirlo.
- Así puedes añadir nuevos idiomas sin perder los que ya tenías en YouTube.

Esto permite máxima calidad y control sobre los subtítulos y títulos antes de traducir y publicar.

---

## Notas y recomendaciones

<details>
<summary>Notas y recomendaciones (clic para desplegar)</summary>

- **No modifica el título ni la descripción original en español:** Solo añade traducciones en otros idiomas.
- **No fusiona título y subtítulo:** YouTube los gestiona como elementos separados.
- **Si subes varias veces una pista de subtítulos con el mismo nombre e idioma, YouTube dará error 409:** Borra la pista anterior si necesitas reemplazarla.
- **El script solo puede modificar vídeos de los que seas propietario** (no funciona con permisos de editor).
- **La calidad de la traducción depende de Google Translate:** Si necesitas traducción profesional, edita los subtítulos originales antes de traducir o considera integrar otra API.

</details>

---

## Solución de problemas

<details>
<summary>Solución de problemas (clic para desplegar)</summary>

- **Error 403/400 al subir:** Asegúrate de ser el propietario del vídeo y de estar autenticado correctamente.
- **Error 409 al subir subtítulos:** Borra la pista anterior en YouTube Studio antes de volver a subir.
- **Traducción de baja calidad:** Edita los subtítulos originales antes de traducir o considera integrar una API de traducción profesional.

</details>

---

## Guía para autenticación por el dueño del canal

<details>
<summary>Guía para autenticación por el dueño del canal (clic para desplegar)</summary>

1. El dueño debe tener Python 3.8+ y el archivo `client_secrets.json`.
2. Ejecuta el script y selecciona la opción de autenticación.
3. Se abrirá el navegador para autorizar el acceso.
4. Se generará el archivo `token.json`.
5. Si otra persona va a operar el script, debe colocar el `token.json` en la misma carpeta que el script y el `client_secrets.json`.

**Seguridad:**  
El archivo `token.json` da acceso a la cuenta de YouTube para las acciones permitidas por la API. El dueño puede revocar el acceso en https://myaccount.google.com/permissions.

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

¿Dudas o problemas?  
Consulta el log `LOG_ytranslator.log` o contacta con el desarrollador.

---

### Nota importante sobre la opción 1

> **TIP:** Si quieres obtener todas las traducciones generadas (títulos, descripciones y subtítulos en todos los idiomas seleccionados) para revisarlas manualmente antes de subirlas a YouTube, utiliza la **opción 1** del menú principal. Cuando el script te pregunte si deseas subir los resultados a YouTube, responde **'n'** (no). Así se generará toda la carpeta del proyecto con los archivos traducidos, pero no se subirá nada automáticamente. Esto te permite revisar, corregir o modificar cualquier traducción antes de decidir qué subir.
>
> La **opción 4** solo descarga los subtítulos automáticos en español para revisión/corrección manual, pero no genera traducciones ni títulos/descripciones.

## Menú principal y funciones disponibles

El script ofrece un menú interactivo con las siguientes opciones:

1. **Traducir vídeo completo (título, subtítulos, descripción):** Traduce directamente desde un vídeo de YouTube y guarda los resultados en la carpeta indicada. Puedes elegir traducir solo título, solo subtítulos, solo descripción, o cualquier combinación. Si ocurre un error, se muestra un mensaje claro y no se detiene el programa.
2. **Autenticarse con YouTube:** Realiza la autenticación necesaria para poder subir traducciones. Si hay un error de autenticación, se muestra un mensaje claro.
3. **Subir traducciones desde carpeta existente:** Sube títulos, descripciones y subtítulos previamente traducidos y guardados en una carpeta. Si ocurre un error, se informa y el flujo continúa.
4. **Descargar títulos, descripciones y subtítulos automáticos para revisión manual:** Descarga los subtítulos automáticos, el título y la descripción originales del vídeo y los guarda en la carpeta indicada para revisión/corrección antes de traducir. Si ocurre un error, se muestra un mensaje claro.
5. **Traducir y (opcionalmente) subir subtítulos a partir de un archivo SRT revisado:** Permite traducir y subir subtítulos a partir de un archivo SRT que hayas revisado manualmente.
6. **Salir:** Finaliza el programa de forma segura.
7. **Cambiar/definir idioma base:** Permite cambiar el idioma base en cualquier momento. Si introduces un código no soportado, se muestra una advertencia pero puedes continuar.

---

## Ejemplo de uso de las nuevas funciones

### Opción 1: Traducir vídeo completo
- Selecciona la opción 1 en el menú.
- Introduce la URL del vídeo de YouTube y el nombre de la carpeta de destino.
- El script mostrará el idioma base detectado y te preguntará si es correcto. Si no lo es, podrás introducir el código de idioma base manualmente antes de continuar.
- Elige qué deseas traducir (título, subtítulos, descripción, o combinación).
- Los archivos traducidos se guardarán en la carpeta indicada.

### Opción 4: Descargar títulos, descripciones y subtítulos automáticos
- Selecciona la opción 4 en el menú.
- Introduce la URL del vídeo y el nombre de la carpeta de destino.
- El script mostrará el idioma base detectado y te preguntará si es correcto. Si no lo es, podrás introducir el código de idioma base manualmente antes de continuar.
- Se guardarán el archivo `original_{lang}.srt` en la subcarpeta `subtitles/`, el título en `original_title.txt` y la descripción en `original_description`.txt para su revisión manual.
---
