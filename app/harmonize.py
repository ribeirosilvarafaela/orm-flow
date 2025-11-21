from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from PIL import Image


@dataclass
class ChordSuggestion:
    pagina: int
    acordes: list[str]


class Harmonizer:
    """Gera sugestões de acordes a partir de características visuais da página."""

    chord_pool: Sequence[str] = (
        "C", "Dm", "Em", "F", "G", "Am", "Bm(b5)",
        "C7", "Dm7", "Em7", "Fmaj7", "G7", "Am7", "Bdim",
    )

    def infer_chords_from_image(self, image_path: Path, max_chords: int = 6) -> list[str]:
        image = Image.open(image_path).convert("L")
        histogram = image.histogram()
        energy = sum(i * count for i, count in enumerate(histogram))
        spread = sum(count for count in histogram if count > 0)
        base_index = int((energy + spread) % len(self.chord_pool))

        chords: list[str] = []
        step = max(1, len(self.chord_pool) // max_chords)
        for i in range(max_chords):
            idx = (base_index + i * step) % len(self.chord_pool)
            chords.append(self.chord_pool[idx])
        return chords
