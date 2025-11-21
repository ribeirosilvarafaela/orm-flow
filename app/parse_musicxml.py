from pathlib import Path

from music21 import chord, converter, note, stream


def extract_notes_to_txt(musicxml_path: Path) -> list[str]:
    s: stream.Score = converter.parse(str(musicxml_path))
    lines: list[str] = []
    for part_idx, part in enumerate(s.parts):
        for m_idx, measure in enumerate(part.getElementsByClass("Measure"), start=1):
            for el in measure.notesAndRests:
                if isinstance(el, note.Note):
                    lines.append(
                        f"part={part_idx + 1} measure={m_idx} note={el.pitch.nameWithOctave} dur={el.quarterLength}"
                    )
                elif isinstance(el, chord.Chord):
                    names = ".".join(n.nameWithOctave for n in el.notes)
                    lines.append(
                        f"part={part_idx + 1} measure={m_idx} chord={names} dur={el.quarterLength}"
                    )
    return lines
