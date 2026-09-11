#!/usr/bin/env python3
"""
markitdown-wrapper.py - Conversión de documentos a Markdown para análisis por Claude

Convierte PDF, DOCX, XLSX, PPTX, HTML, CSV, JSON, ZIP y otros formatos a Markdown
limpio para análisis de texto, ahorrando tokens vs LLM vision.

Uso:
    python markitdown-wrapper.py <ruta_archivo>
    python markitdown-wrapper.py <ruta_archivo> --chunk-size 50000
    python markitdown-wrapper.py <ruta_archivo> --pages 1-10
    python markitdown-wrapper.py <ruta_archivo> --info
    python markitdown-wrapper.py <ruta_archivo> --output resultado.md

Deteccion de calidad:
    Si el PDF es escaneado (sin capa de texto), el script lo detecta y avisa.
    En ese caso, se recomienda usar LLM vision.
"""

import sys
import os
import re
import argparse
from pathlib import Path


def parse_page_range(page_range_str: str, total_pages: int) -> list[int]:
    """Parsea un rango como '1-10,15,20-25' a lista de indices 0-based."""
    pages = set()
    for part in page_range_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            start = max(1, int(start.strip()))
            end = min(total_pages, int(end.strip()))
            pages.update(range(start - 1, end))
        else:
            n = int(part.strip())
            if 1 <= n <= total_pages:
                pages.add(n - 1)
    return sorted(pages)


def get_text_density(text: str, page_count: int) -> float:
    """Calcula chars promedio por pagina. < 100 indica PDF escaneado."""
    if not text or page_count == 0:
        return 0.0
    clean = re.sub(r"\s+", " ", text).strip()
    return len(clean) / page_count


def detect_quality(text: str, page_count: int) -> dict:
    """Evalua la calidad de la extraccion de texto."""
    density = get_text_density(text, page_count)
    char_count = len(text.strip())
    word_count = len(text.split()) if text.strip() else 0

    if density < 50:
        quality = "ESCANEADO"
        recommendation = "PDF sin capa de texto. Usar LLM vision para análisis confiable."
    elif density < 300:
        quality = "PARCIAL"
        recommendation = "Texto extraido pero posiblemente incompleto (formularios, columnas, tablas)."
    elif density < 800:
        quality = "BUENA"
        recommendation = "Texto extraido correctamente. Analisis por texto es confiable."
    else:
        quality = "OPTIMA"
        recommendation = "Documento nativo con texto completo. Ideal para análisis por texto."

    return {
        "quality": quality,
        "density": round(density, 1),
        "char_count": char_count,
        "word_count": word_count,
        "recommendation": recommendation,
    }


def extract_pdf_with_fallback(filepath: str, page_range: list[int] | None = None) -> tuple[str, int, str]:
    """
    Extrae texto de PDF usando multiples estrategias:
    1. markitdown (pdfminer.six) - texto corrido
    2. pdfplumber - mejor para tablas, extrae por pagina si se indica rango
    Retorna (texto_markdown, paginas_totales, estrategia_usada)
    """
    total_pages = 0
    estrategia = "markitdown"

    # Estrategia 1: markitdown (optima para documentos de texto corrido)
    try:
        from markitdown import MarkItDown
        md = MarkItDown(enable_plugins=False)
        result = md.convert(filepath)
        text = result.text_content or ""

        # Intentar obtener pagina count via pdfminer
        try:
            from pdfminer.high_level import extract_pages
            total_pages = sum(1 for _ in extract_pages(filepath))
        except Exception:
            total_pages = max(1, len(text) // 2000)

        if text.strip() and get_text_density(text, total_pages) >= 50:
            # Si hay rango de paginas, extraer solo esas via pdfplumber
            if page_range is not None:
                try:
                    import pdfplumber
                    with pdfplumber.open(filepath) as pdf:
                        total_pages = len(pdf.pages)
                        selected = [pdf.pages[i] for i in page_range if i < len(pdf.pages)]
                        chunks = []
                        for i, page in zip(page_range, selected):
                            page_text = page.extract_text() or ""
                            # Extraer tablas
                            tables = page.extract_tables()
                            table_md = ""
                            for table in tables:
                                if table:
                                    header = table[0]
                                    rows = table[1:]
                                    if header:
                                        table_md += "\n| " + " | ".join(str(c or "") for c in header) + " |\n"
                                        table_md += "| " + " | ".join("---" for _ in header) + " |\n"
                                        for row in rows:
                                            table_md += "| " + " | ".join(str(c or "") for c in row) + " |\n"
                            chunks.append(f"\n\n---\n## Pagina {i + 1}\n\n{page_text}{table_md}")
                        return "\n".join(chunks), total_pages, "markitdown+pdfplumber-paginas"
                except Exception:
                    pass

            return text, total_pages, estrategia
    except Exception as e:
        print(f"[ADVERTENCIA] markitdown fallo: {e}", file=sys.stderr)

    # Estrategia 2: pdfplumber (mejor para tablas, mas robusto con PDFs complejos)
    try:
        import pdfplumber
        estrategia = "pdfplumber"
        with pdfplumber.open(filepath) as pdf:
            total_pages = len(pdf.pages)
            pages_to_process = page_range if page_range is not None else list(range(total_pages))
            chunks = []
            for i in pages_to_process:
                if i >= total_pages:
                    continue
                page = pdf.pages[i]
                page_text = page.extract_text() or ""
                tables = page.extract_tables()
                table_md = ""
                for table in tables:
                    if table:
                        header = table[0]
                        rows = table[1:]
                        if header:
                            table_md += "\n| " + " | ".join(str(c or "") for c in header) + " |\n"
                            table_md += "| " + " | ".join("---" for _ in header) + " |\n"
                            for row in rows:
                                table_md += "| " + " | ".join(str(c or "") for c in row) + " |\n"
                chunks.append(f"\n\n---\n## Pagina {i + 1}\n\n{page_text}{table_md}")
            return "\n".join(chunks), total_pages, estrategia
    except Exception as e:
        print(f"[ADVERTENCIA] pdfplumber fallo: {e}", file=sys.stderr)

    return "", total_pages, "sin_texto"


def convert_file(filepath: str, page_range_str: str | None = None) -> tuple[str, dict]:
    """
    Convierte cualquier archivo soportado a Markdown.
    Retorna (markdown_texto, metadata_dict).
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {filepath}")

    ext = path.suffix.lower()
    metadata = {
        "archivo": path.name,
        "extension": ext,
        "tamano_kb": round(path.stat().st_size / 1024, 1),
        "estrategia": "markitdown",
        "paginas": 0,
        "calidad": {},
    }

    # PDFs: logica especial con fallback y deteccion de calidad
    if ext == ".pdf":
        page_range = None
        if page_range_str:
            # Necesitamos total_pages para parsear el rango; hacemos lectura rapida
            try:
                import pdfplumber
                with pdfplumber.open(filepath) as pdf:
                    total_pages_pre = len(pdf.pages)
                page_range = parse_page_range(page_range_str, total_pages_pre)
            except Exception:
                pass

        text, total_pages, estrategia = extract_pdf_with_fallback(filepath, page_range)
        metadata["paginas"] = total_pages
        metadata["estrategia"] = estrategia
        metadata["calidad"] = detect_quality(text, max(1, total_pages))
        if page_range:
            metadata["paginas_extraidas"] = len(page_range)
            metadata["rango"] = page_range_str
        return text, metadata

    # Otros formatos: markitdown nativo
    try:
        from markitdown import MarkItDown
        md = MarkItDown(enable_plugins=False)
        result = md.convert(filepath)
        text = result.text_content or ""
        metadata["estrategia"] = "markitdown"
        metadata["calidad"] = detect_quality(text, 1)
        return text, metadata
    except Exception as e:
        raise RuntimeError(f"No se pudo convertir {filepath}: {e}") from e


def chunk_text(text: str, max_chars: int) -> list[str]:
    """Divide texto en chunks respetando saltos de parrafo."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        if end >= len(text):
            chunks.append(text[start:])
            break
        # Buscar ultimo parrafo doble antes del limite
        cut = text.rfind("\n\n", start, end)
        if cut == -1 or cut == start:
            cut = text.rfind("\n", start, end)
        if cut == -1 or cut == start:
            cut = end
        chunks.append(text[start:cut])
        start = cut
    return chunks


def print_info(metadata: dict) -> None:
    """Imprime resumen del documento sin el contenido."""
    q = metadata.get("calidad", {})
    print(f"\nArchivo:      {metadata['archivo']}")
    print(f"Tamano:       {metadata['tamano_kb']} KB")
    print(f"Extension:    {metadata['extension']}")
    print(f"Estrategia:   {metadata['estrategia']}")
    if metadata.get("paginas"):
        print(f"Paginas:      {metadata['paginas']}", end="")
        if metadata.get("paginas_extraidas"):
            print(f" (extraidas: {metadata['paginas_extraidas']} | rango: {metadata.get('rango', '')})", end="")
        print()
    if q:
        print(f"Calidad:      {q.get('quality', '?')} ({q.get('density', 0)} chars/pag)")
        print(f"Chars totales: {q.get('char_count', 0):,}")
        print(f"Palabras:     {q.get('word_count', 0):,}")
        print(f"Recomendacion: {q.get('recommendation', '')}")


def main():
    parser = argparse.ArgumentParser(
        description="Convierte documentos a Markdown para análisis por Claude.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("filepath", help="Ruta al archivo a convertir")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=0,
        metavar="N",
        help="Divide la salida en chunks de N chars. 0 = sin division (default)",
    )
    parser.add_argument(
        "--pages",
        type=str,
        default=None,
        metavar="RANGO",
        help="Paginas a extraer (solo PDF). Ej: '1-10', '1,3,5-8'",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Solo muestra metadatos sin el contenido",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        metavar="ARCHIVO",
        help="Guarda el resultado en archivo .md",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Omite el encabezado de metadatos en la salida",
    )

    args = parser.parse_args()

    try:
        text, metadata = convert_file(args.filepath, args.pages)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    # Modo solo info
    if args.info:
        print_info(metadata)
        sys.exit(0)

    # Construir encabezado de metadatos
    header_lines = []
    if not args.no_header:
        q = metadata.get("calidad", {})
        quality = q.get("quality", "?")
        header_lines.append(f"<!-- MARKITDOWN: {metadata['archivo']} | {metadata['extension']} | {metadata['tamano_kb']}KB | estrategia={metadata['estrategia']}")
        if metadata.get("paginas"):
            pag_info = str(metadata["paginas"])
            if metadata.get("paginas_extraidas"):
                pag_info += f" total ({metadata['paginas_extraidas']} extraidas, rango={metadata.get('rango', '')})"
            header_lines.append(f"     paginas={pag_info}")
        if q:
            header_lines.append(f"     calidad={quality} density={q.get('density', 0)} chars={q.get('char_count', 0):,} palabras={q.get('word_count', 0):,}")
            header_lines.append(f"     nota={q.get('recommendation', '')} -->")
        else:
            header_lines.append("-->")

        # Advertencia prominente si es escaneado
        if quality == "ESCANEADO":
            header_lines.append("\n> [!WARNING]")
            header_lines.append("> **PDF ESCANEADO** - sin capa de texto extraible.")
            header_lines.append("> El contenido a continuacion puede estar vacio o incompleto.")
            header_lines.append("> Usar LLM vision para análisis confiable.\n")
        elif quality == "PARCIAL":
            header_lines.append("\n> [!NOTE]")
            header_lines.append("> **Extraccion parcial** - el texto puede estar incompleto.")
            header_lines.append("> Verificar que el contenido critico este presente.\n")

    header = "\n".join(header_lines)

    # Modo con chunks
    if args.chunk_size and args.chunk_size > 0:
        chunks = chunk_text(text, args.chunk_size)
        total_chunks = len(chunks)
        output_parts = []
        for i, chunk in enumerate(chunks, 1):
            part = f"{header}\n\n# Chunk {i}/{total_chunks}\n\n{chunk}" if i == 1 else f"# Chunk {i}/{total_chunks}\n\n{chunk}"
            output_parts.append(part)
        full_output = "\n\n---\n\n".join(output_parts)
    else:
        full_output = f"{header}\n\n{text}" if header else text

    # Guardar a archivo si se pidio
    if args.output:
        out_path = Path(args.output)
        out_path.write_text(full_output, encoding="utf-8")
        print_info(metadata)
        print(f"\nGuardado en: {out_path.resolve()}")
        print(f"Tamano salida: {round(out_path.stat().st_size / 1024, 1)} KB")
    else:
        # Salida a stdout (Claude lo lee directamente via Bash)
        print(full_output)
        if not args.no_header:
            print_info(metadata)


if __name__ == "__main__":
    main()
