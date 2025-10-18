import subprocess
from pathlib import Path
from .settings import settings

def run_audiveris_on_images(images_dir: Path, output_dir: Path, audiveris_jar: str | None = None) -> Path:
    audiveris_jar = audiveris_jar or settings.AUDIVERIS_JAR
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "java", "-jar", audiveris_jar,
        "-batch", "-export",
        "-output", str(output_dir),
        str(images_dir)
    ]
    process = subprocess.run(cmd, capture_output=True, text=True)
    if process.returncode != 0:
        raise RuntimeError(f"Erro Audiveris:\n{process.stderr}")

    xmls = list(output_dir.glob("**/*.mxl")) + list(output_dir.glob("**/*.xml"))
    if not xmls:
        raise FileNotFoundError("Nenhum MusicXML gerado.")
    xmls.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return xmls[0]
