"""Same-syllable multi-note grouping.

These groups model one sung syllable carried across several annotated TSV notes
(melisma-like singing). This is different from decorative scoop/fall-in inside a
single note: the pitch changes here are already in the TSV labels.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .score_io import Note


MIN_GROUP_NOTES = 3
CONNECTED_GAP_MAX_S = 0.200
MIN_GROUP_NOTE_DURATION_S = 0.180
MAX_ADJACENT_INTERVAL_SEMITONES = 2
GROUPS_ENABLED = False
GROUP_SELECTION_FRACTION = 0.00


@dataclass(frozen=True)
class SyllableGroupMark:
    """Per-note same-syllable grouping mark."""

    group_id: int | None
    group_position: int
    group_size: int
    syllable_role: str

    @property
    def is_continuation(self) -> bool:
        return self.syllable_role == "continuation"

    def to_dict(self) -> dict[str, int | str | None]:
        return asdict(self)


def plan_syllable_groups(
    notes: list[Note],
    rng: np.random.Generator,
    selection_fraction: float = GROUP_SELECTION_FRACTION,
) -> tuple[list[SyllableGroupMark], dict[str, float | int | bool]]:
    """Select a small subset of stepwise connected notes as one-syllable groups."""

    selection_fraction = float(np.clip(selection_fraction, 0.0, 1.0))
    marks = [
        SyllableGroupMark(
            group_id=None,
            group_position=0,
            group_size=1,
            syllable_role="single",
        )
        for _ in notes
    ]
    candidate_groups = _candidate_groups(notes)
    selected_groups = [] if not GROUPS_ENABLED else _select_groups(candidate_groups, rng, selection_fraction)

    for group_id, group in enumerate(selected_groups):
        group_size = len(group)
        for position, note_index in enumerate(group):
            marks[note_index] = SyllableGroupMark(
                group_id=group_id,
                group_position=position,
                group_size=group_size,
                syllable_role="start" if position == 0 else "continuation",
            )

    grouped_note_count = sum(mark.group_id is not None for mark in marks)
    continuation_count = sum(mark.is_continuation for mark in marks)
    summary = {
        "candidate_group_count": len(candidate_groups),
        "selected_group_count": len(selected_groups),
        "grouped_note_count": grouped_note_count,
        "continuation_note_count": continuation_count,
        "grouped_note_fraction": _safe_fraction(grouped_note_count, len(notes)),
        "selection_fraction": selection_fraction,
        "groups_enabled": GROUPS_ENABLED,
        "default_selection_fraction": GROUP_SELECTION_FRACTION,
        "min_group_notes": MIN_GROUP_NOTES,
        "connected_gap_max_s": CONNECTED_GAP_MAX_S,
        "min_group_note_duration_s": MIN_GROUP_NOTE_DURATION_S,
        "max_adjacent_interval_semitones": MAX_ADJACENT_INTERVAL_SEMITONES,
        "requires_monotonic_direction": True,
        "decorative_transitions_on_continuations": False,
    }
    return marks, summary


def continuation_indices(marks: list[SyllableGroupMark]) -> set[int]:
    """Return note indices that continue an already-started syllable."""

    return {index for index, mark in enumerate(marks) if mark.is_continuation}


def grouped_indices(marks: list[SyllableGroupMark]) -> set[int]:
    """Return every note index that belongs to a same-syllable group."""

    return {index for index, mark in enumerate(marks) if mark.group_id is not None}


def _candidate_groups(notes: list[Note]) -> list[list[int]]:
    groups: list[list[int]] = []
    for run in _connected_runs(notes):
        groups.extend(_monotonic_stepwise_groups_from_run(notes, run))
    return groups


def _connected_runs(notes: list[Note]) -> list[list[int]]:
    if len(notes) < 2:
        return []

    runs: list[list[int]] = []
    current = [0]
    for index in range(len(notes) - 1):
        gap = notes[index + 1].onset - notes[index].offset
        if gap <= CONNECTED_GAP_MAX_S:
            current.append(index + 1)
        else:
            if len(current) >= 2:
                runs.append(current)
            current = [index + 1]

    if len(current) >= 2:
        runs.append(current)
    return runs


def _monotonic_stepwise_groups_from_run(notes: list[Note], run: list[int]) -> list[list[int]]:
    groups: list[list[int]] = []
    current = [run[0]]
    current_sign: int | None = None

    for previous_index, note_index in zip(run, run[1:]):
        previous_pitch = int(round(notes[previous_index].pitch))
        pitch = int(round(notes[note_index].pitch))
        diff = pitch - previous_pitch
        sign = 1 if diff > 0 else -1 if diff < 0 else 0
        valid_step = sign != 0 and abs(diff) <= MAX_ADJACENT_INTERVAL_SEMITONES

        if valid_step and (current_sign is None or sign == current_sign):
            current.append(note_index)
            current_sign = sign
            continue

        if _is_valid_stepwise_group(notes, current):
            groups.append(current)
            current = [note_index]
            current_sign = None
            continue

        current = [previous_index, note_index] if valid_step else [note_index]
        current_sign = sign if valid_step else None

    if _is_valid_stepwise_group(notes, current):
        groups.append(current)
    return groups


def _is_valid_stepwise_group(notes: list[Note], group: list[int]) -> bool:
    if len(group) < MIN_GROUP_NOTES:
        return False
    if any(notes[index].duration < MIN_GROUP_NOTE_DURATION_S for index in group):
        return False

    pitches = [int(round(notes[index].pitch)) for index in group]
    diffs = [pitches[index + 1] - pitches[index] for index in range(len(pitches) - 1)]
    if any(diff == 0 for diff in diffs):
        return False
    if any(abs(diff) > MAX_ADJACENT_INTERVAL_SEMITONES for diff in diffs):
        return False

    first_sign = 1 if diffs[0] > 0 else -1
    return all((1 if diff > 0 else -1) == first_sign for diff in diffs)


def _select_groups(
    candidate_groups: list[list[int]],
    rng: np.random.Generator,
    selection_fraction: float,
) -> list[list[int]]:
    if not candidate_groups:
        return []

    if selection_fraction <= 0.0:
        return []

    target_count = int(round(len(candidate_groups) * selection_fraction))
    target_count = max(1, target_count)
    target_count = min(target_count, len(candidate_groups))

    selected_indices = rng.choice(
        len(candidate_groups),
        size=target_count,
        replace=False,
    )
    return [candidate_groups[int(index)] for index in sorted(selected_indices)]


def _safe_fraction(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return float(numerator) / float(denominator)
