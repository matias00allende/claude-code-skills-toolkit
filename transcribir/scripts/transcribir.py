"""
Transcribe audio/video a texto usando openai-whisper.
Si el input es una URL, descarga el audio primero con yt-dlp.

Uso:
    python transcribir.py <archivo_o_url> [--modelo medium] [--idioma es] [--formato txt]

Requisitos: whisper (pip install openai-whisper), ffmpeg en PATH, yt-dlp (solo si el input es URL).
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

MODELOS_VALIDOS = ("tiny", "base", "small", "medium", "large", "turbo")
FORMATOS_VALIDOS = ("txt", "srt", "vtt", "json", "all")


def es_url(texto: str) -> bool:
    return texto.startswith("http://") or texto.startswith("https://")


def descargar_audio(url: str, destino: Path) -> Path:
    salida = destino / "audio_descargado.%(ext)s"
    subprocess.run(
        ["yt-dlp", "-x", "--audio-format", "mp3", "-o", str(salida), url],
        check=True,
    )
    archivos = list(destino.glob("audio_descargado.*"))
    if not archivos:
        raise RuntimeError("yt-dlp no genero el archivo de audio esperado")
    return archivos[0]


def transcribir(archivo: Path, modelo: str, idioma: str, formato: str, salida_dir: Path) -> None:
    comando = [
        "whisper",
        str(archivo),
        "--model", modelo,
        "--output_format", formato,
        "--output_dir", str(salida_dir),
    ]
    if idioma:
        comando += ["--language", idioma]
    subprocess.run(comando, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe audio/video a texto con whisper")
    parser.add_argument("entrada", help="Ruta de archivo de audio/video, o URL (yt-dlp)")
    parser.add_argument("--modelo", default="medium", choices=MODELOS_VALIDOS)
    parser.add_argument("--idioma", default="es", help="Codigo de idioma, ej. es, en. Vacio = autodeteccion")
    parser.add_argument("--formato", default="txt", choices=FORMATOS_VALIDOS)
    parser.add_argument("--salida", default=None, help="Directorio de salida (default: junto al archivo de entrada)")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        if es_url(args.entrada):
            print(f"Descargando audio de: {args.entrada}")
            archivo = descargar_audio(args.entrada, Path(tmp))
            salida_dir = Path(args.salida) if args.salida else Path.cwd()
        else:
            archivo = Path(args.entrada).resolve()
            if not archivo.exists():
                sys.exit(f"Archivo no encontrado: {archivo}")
            salida_dir = Path(args.salida) if args.salida else archivo.parent

        salida_dir.mkdir(parents=True, exist_ok=True)
        print(f"Transcribiendo {archivo.name} con modelo '{args.modelo}'...")
        transcribir(archivo, args.modelo, args.idioma, args.formato, salida_dir)
        print(f"Listo. Salida en: {salida_dir}")


if __name__ == "__main__":
    main()
