---
name: transcribir
description: >
  Transcribe audio o video a texto usando openai-whisper, corriendo localmente
  (con aceleración GPU si está disponible). Si el input es una URL (ej. video de
  YouTube), descarga el audio primero con yt-dlp. Usar cuando el usuario diga
  "transcribe este audio", "pasa a texto esta reunión", "transcribe el video de",
  "genera el acta de audio de", "necesito la transcripción de", "convierte este
  podcast/video a texto". No usar para resumir o interpretar el contenido ya
  transcrito (eso es tarea normal del modelo sobre el .txt resultante), ni para
  traducción de idiomas distinta de la transcripción misma (whisper traduce a
  ingles con --task translate si se necesita, indicarlo explícitamente).
model: haiku
disable-model-invocation: false
allowed-tools: Read Bash
---

# Transcribir - audio/video a texto con whisper

Transcribe: **$ARGUMENTS**

Wrapper: `scripts/transcribir.py` (incluido en esta skill). Motor: `openai-whisper`, corre 100% local.

---

## Delegación (modelo económico vs modelo de razonamiento)

- **Ejecución del script:** correr `transcribir.py` con los argumentos correctos es mecánico - si tu configuración permite delegar a un modelo más económico/rápido, hazlo cuando la tarea sea solo "transcribe este archivo/URL y dime cuando esté listo".
- **Escalar a un modelo de mayor razonamiento cuando:**
  - El resultado se va a usar para redactar un acta formal (requiere revisión de nombres propios, siglas y formato).
  - Hay que interpretar o resumir el contenido transcrito, no solo generarlo.
  - La transcripción sale con errores evidentes (idioma mal detectado, texto incoherente) y hay que ajustar `--modelo` o `--idioma` con criterio.

## Paso 1 - Ejecutar la transcripción

```bash
# Archivo local
python scripts/transcribir.py "<ruta_archivo>" --modelo medium --idioma es

# URL (descarga audio con yt-dlp primero)
python scripts/transcribir.py "<url>" --modelo medium --idioma es

# Subtitulos (SRT) en vez de texto plano
python scripts/transcribir.py "<ruta_o_url>" --formato srt
```

Modelos disponibles (`--modelo`): `tiny`/`base`/`small`/`medium`/`large`/`turbo`. Default `medium` - buen balance para reuniones/capacitaciones. Usar `large` solo si `medium` da resultados pobres (más VRAM, más lento).

## Paso 2 - Verificar el resultado

- Confirmar que el archivo de salida (`.txt`/`.srt`) se generó en el directorio esperado (el script lo imprime al final).
- Leer una muestra del texto para detectar señales de idioma mal detectado o audio de mala calidad (texto sin sentido, repeticiones anómalas) antes de entregarlo como listo.

## Privacidad - regla sin excepciones

Las transcripciones de reuniones, llamadas o capacitaciones pueden contener **datos personales** de terceros (nombres, situaciones laborales, opiniones).

- **Nunca** pegar el contenido completo de una transcripción identificable en un sistema de memoria persistente del agente.
- El archivo de salida queda en el directorio que indique quien ejecuta la tarea. El agente no genera otras copias, pero los respaldos o la sincronización de ese directorio pueden duplicarlo.
- Si se necesita registrar que se hizo una transcripción, documentar solo metadatos (fecha, tema, ruta del archivo de salida), nunca el contenido.

---

## Troubleshooting

**`FileNotFoundError: whisper` o `yt-dlp` no encontrado** - Verificar que el entorno Python tiene `openai-whisper` instalado (`pip show openai-whisper`) y que `yt-dlp`/`ffmpeg` están en PATH.

**Transcripción muy lenta** - Verificar aceleración GPU: `python -c "import torch; print(torch.cuda.is_available())"`. Si devuelve `False`, whisper corre en CPU (mucho más lento, especialmente con `--modelo large`).

**Idioma mal detectado / texto sin sentido** - Forzar `--idioma es` (o el que corresponda) explícitamente en vez de dejar autodetección, especialmente en audios cortos o con ruido de fondo.

**Input es una URL de un sitio no soportado por yt-dlp** - Verificar contra la lista de sitios soportados (`yt-dlp --list-extractors`) antes de asumir que es un bug del script `transcribir.py`.

## Requisitos

```bash
pip install openai-whisper yt-dlp
# ffmpeg debe estar instalado y en PATH
```
