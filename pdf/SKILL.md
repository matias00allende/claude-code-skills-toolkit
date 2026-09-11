---
name: pdf
description: >
  Convierte y analiza documentos PDF, DOCX, XLSX, PPTX, HTML o CSV a Markdown
  usando un wrapper local sobre markitdown/pdfplumber, ahorrando 70-90% de tokens
  vs LLM vision. Usar cuando el usuario mencione un archivo PDF, DOCX, XLSX, PPTX,
  CSV o HTML para analizar, diga "lee el PDF", "analiza este documento", "extrae
  el contenido de", "lee el archivo", "abre el PDF", o comparta una ruta de
  archivo que no sea código fuente. No usar para leer archivos de código fuente
  (.py, .js, .ts, etc.), usar Read directamente en esos casos. NUNCA usar Read
  sobre un PDF.
model: haiku
disable-model-invocation: false
allowed-tools: Bash Read
---

# PDF - Análisis de documentos sin LLM vision

Convierte cualquier documento a Markdown usando `scripts/markitdown-wrapper.py` (incluido en esta skill).

## Por qué existe

Leer un PDF directamente con la herramienta de lectura de archivos de un agente de IA
suele devolver binario ilegible o forzar el uso de visión (LLM vision), que consume
muchísimos más tokens que analizar el texto ya extraído. Este wrapper extrae el texto
una sola vez, detecta si la extracción es confiable, y deja el resultado en Markdown
listo para analizar como texto normal.

## Paso 1: Inspección previa (SIEMPRE primero para PDFs)

```bash
python scripts/markitdown-wrapper.py "<ruta_archivo>" --info
```

Interpretar el campo `Calidad`:

| Calidad | Acción |
|---------|--------|
| `ESCANEADO` | Avisar: "PDF escaneado sin capa de texto. Usando LLM vision." Luego usar Read. |
| `PARCIAL` | Extraer y advertir que puede estar incompleto. |
| `BUENA` o `OPTIMA` | Extraer directamente, confiable. |

Si `Chars totales` > 200,000: planificar extracción por bloques de 30-50 páginas.

## Paso 2: Extracción

```bash
# Documento completo (menos de 200,000 chars)
python scripts/markitdown-wrapper.py "<ruta>"

# Páginas específicas (PDF grande)
python scripts/markitdown-wrapper.py "<ruta>.pdf" --pages "1-50"
python scripts/markitdown-wrapper.py "<ruta>.pdf" --pages "51-100"

# Dividir en chunks de tamaño fijo (documentos largos sin páginas, ej. HTML/CSV grandes)
python scripts/markitdown-wrapper.py "<ruta>" --chunk-size 80000

# Guardar para análisis largo o multi-sesión
python scripts/markitdown-wrapper.py "<ruta>" --output "salida.md"
# Luego leer con: Read "salida.md"
```

## Paso 3: Análisis

Analizar el Markdown resultante y responder al usuario. Para documentos largos,
extraer por bloques e ir acumulando hallazgos antes de responder.

## Cuándo SÍ usar LLM vision (Read directo)

- PDF calidad ESCANEADO (sin capa de texto)
- Imágenes, diagramas, planos, mapas que requieren interpretación visual
- El usuario pide analizar gráficos, layouts o elementos gráficos específicos

## Ahorro de tokens

| Método | PDF 100 páginas típico |
|--------|------------------------|
| LLM vision (Read) | 50,000-200,000 tokens |
| markitdown (texto) | 10,000-40,000 tokens |
| Ahorro | 70-90% |

## Requisitos

```bash
pip install markitdown pdfplumber pdfminer.six
```

## Troubleshooting

**UnicodeEncodeError al imprimir en consola:** Usar `--output` para guardar en archivo y luego Read.

**FileNotFoundError en --output:** El directorio de destino no existe. Crearlo antes de ejecutar.

**Calidad PARCIAL con texto ilegible:** Puede ser PDF con encoding no estándar. Intentar con `--pages` en bloques pequeños. Si persiste, usar LLM vision.

**Ruta con espacios:** Siempre encerrar entre comillas dobles.
