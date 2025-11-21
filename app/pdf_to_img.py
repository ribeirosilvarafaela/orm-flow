from pathlib import Path

from pdf2image import convert_from_path

from .settings import settings


def pdf_to_images(pdf_path: Path, out_dir: Path) -> list[Path]:
    """Convert a PDF score to page images."""
    out_dir.mkdir(parents=True, exist_ok=True)
    pages = convert_from_path(str(pdf_path), dpi=settings.OMR_DPI, fmt="png")
    paths: list[Path] = []
    for i, page in enumerate(pages[: settings.MAX_PAGES], start=1):
        path = out_dir / f"page_{i:03d}.png"
        page.save(path)
        paths.append(path)
    return paths
