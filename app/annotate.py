from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont

ACCENT = (91, 127, 163)


def _load_font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size=size)
    except OSError:
        return ImageFont.load_default()


def annotate_score(image_path: Path, chords: Iterable[str], output_path: Path) -> Path:
    """Sobrepõe os acordes na parte superior da imagem da página."""

    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    band_height = max(80, int(height * 0.12))

    overlay = Image.new("RGBA", (width, band_height), (255, 255, 255, 235))
    draw = ImageDraw.Draw(overlay)

    chords_list = list(chords)
    font = _load_font(size=max(18, band_height // 4))
    margin = max(20, width // 20)
    spacing = (width - 2 * margin) / max(1, len(chords_list))
    for i, chord in enumerate(chords_list):
        x = margin + i * spacing
        y = band_height // 2
        text_bbox = draw.textbbox((x, y), chord, font=font, anchor="mm")
        padding = 8
        box = (
            text_bbox[0] - padding,
            text_bbox[1] - padding,
            text_bbox[2] + padding,
            text_bbox[3] + padding,
        )
        draw.rounded_rectangle(box, radius=10, outline=ACCENT, width=2, fill=(255, 255, 255, 255))
        draw.text((x, y), chord, fill=ACCENT, font=font, anchor="mm")

    image_with_overlay = Image.new("RGBA", (width, height + band_height), (255, 255, 255, 255))
    image_with_overlay.paste(overlay, (0, 0))
    image_with_overlay.paste(image, (0, band_height))

    rgb_image = image_with_overlay.convert("RGB")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rgb_image.save(output_path)
    return output_path
