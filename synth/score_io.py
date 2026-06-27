"""Score TSV loading, writing, and phrase grouping utilities.

The organizer scores contain only onset, offset, and MIDI pitch. Everything
about the sung voice must be generated while keeping these labels intact.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SCORE_HEADER = "# onset,offset,note"


@dataclass(frozen=True)
class Note:
    """One labeled note from a score TSV."""

    onset: float
    offset: float
    pitch: float

    @property
    def duration(self) -> float:
        return self.offset - self.onset


def load_score_tsv(path: str | Path) -> list[Note]:
    """Load a score TSV with or without a header.

    TODO: If future organizer files add extra columns, extend this parser to
    preserve those columns in metadata while still writing the three required
    training columns.
    """

    score_path = Path(path)
    notes: list[Note] = []
    for line_number, raw_line in enumerate(score_path.read_text().splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.replace(",", "\t").split()
        if len(parts) < 3:
            # Treat a non-numeric first row as a header. Anything else is a
            # malformed note row and should fail loudly.
            if line_number == 1:
                continue
            raise ValueError(f"Invalid TSV row in {score_path}:{line_number}: {raw_line!r}")

        try:
            onset, offset, pitch = (float(parts[0]), float(parts[1]), float(parts[2]))
        except ValueError:
            if line_number == 1:
                continue
            raise ValueError(f"Invalid numeric TSV row in {score_path}:{line_number}: {raw_line!r}")

        if offset <= onset:
            raise ValueError(
                f"Invalid note duration in {score_path}:{line_number}: "
                f"onset={onset}, offset={offset}"
            )
        if not (0 <= pitch <= 127):
            raise ValueError(f"Invalid MIDI pitch in {score_path}:{line_number}: {pitch}")
        notes.append(Note(onset=onset, offset=offset, pitch=pitch))

    if not notes:
        raise ValueError(f"No notes found in {score_path}")

    return sorted(notes, key=lambda note: (note.onset, note.offset, note.pitch))


def write_score_tsv(path: str | Path, notes: Iterable[Note]) -> None:
    """Write a score TSV in the format expected by the project dataloader."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [SCORE_HEADER]
    for note in notes:
        lines.append(f"{note.onset:.6f}\t{note.offset:.6f}\t{note.pitch:.6f}")
    output_path.write_text("\n".join(lines) + "\n")


def split_phrases(notes: list[Note], gap_threshold_s: float = 0.45) -> list[list[int]]:
    """Return note-index groups split by rests between notes.

    A phrase boundary is inferred when the rest after one note is long enough.
    This is only used for syllable and breath placement; it must not change the
    labels.
    """

    if not notes:
        return []

    phrases: list[list[int]] = [[0]]
    previous = notes[0]
    for index, note in enumerate(notes[1:], 1):
        if note.onset - previous.offset > gap_threshold_s:
            phrases.append([index])
        else:
            phrases[-1].append(index)
        previous = note
    return phrases


def last_offset(notes: Iterable[Note]) -> float:
    """Return the final note offset in seconds."""

    return max(note.offset for note in notes)

