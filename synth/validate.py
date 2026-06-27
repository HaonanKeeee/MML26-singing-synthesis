"""Validation helpers for generated synthetic samples."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf

from .score_io import SCORE_HEADER, load_score_tsv


@dataclass(frozen=True)
class ValidationIssue:
    sample: str
    severity: str
    message: str


def validate_sample(sample_dir: str | Path, expected_sample_rate: int = 16_000) -> list[ValidationIssue]:
    """Validate one generated sample directory."""

    sample_path = Path(sample_dir)
    issues: list[ValidationIssue] = []
    audio_path = sample_path / "audio.wav"
    score_path = sample_path / "score.tsv"

    if not audio_path.exists():
        issues.append(_issue(sample_path, "error", "Missing audio.wav"))
    if not score_path.exists():
        issues.append(_issue(sample_path, "error", "Missing score.tsv"))
    if issues:
        return issues

    try:
        info = sf.info(audio_path)
        audio, sample_rate = sf.read(audio_path, always_2d=False)
    except Exception as exc:
        return [_issue(sample_path, "error", f"Cannot read audio.wav: {exc}")]

    if sample_rate != expected_sample_rate:
        issues.append(_issue(sample_path, "error", f"Unexpected sample rate {sample_rate}"))
    if info.channels != 1:
        issues.append(_issue(sample_path, "warning", f"Expected mono audio, got {info.channels} channels"))

    audio_array = np.asarray(audio, dtype=np.float32)
    if audio_array.size == 0:
        issues.append(_issue(sample_path, "error", "Audio is empty"))
    elif float(np.max(np.abs(audio_array))) < 1e-4:
        issues.append(_issue(sample_path, "error", "Audio is nearly silent"))
    elif float(np.max(np.abs(audio_array))) > 0.999:
        issues.append(_issue(sample_path, "warning", "Audio peak is close to clipping"))

    first_line = score_path.read_text().splitlines()[0].strip() if score_path.read_text().strip() else ""
    if first_line != SCORE_HEADER:
        issues.append(_issue(sample_path, "error", f"score.tsv must start with {SCORE_HEADER!r}"))

    try:
        notes = load_score_tsv(score_path)
    except Exception as exc:
        return issues + [_issue(sample_path, "error", f"Cannot parse score.tsv: {exc}")]

    audio_duration = len(audio_array) / float(sample_rate) if sample_rate else 0.0
    last_offset = max(note.offset for note in notes)
    if audio_duration + 1e-3 < last_offset:
        issues.append(
            _issue(
                sample_path,
                "error",
                f"Audio duration {audio_duration:.3f}s is shorter than last offset {last_offset:.3f}s",
            )
        )

    return issues


def validate_dataset(dataset_dir: str | Path, expected_sample_rate: int = 16_000) -> list[ValidationIssue]:
    """Validate every direct child sample in a synthetic dataset directory."""

    root = Path(dataset_dir)
    if not root.exists():
        return [ValidationIssue(str(root), "error", "Dataset directory does not exist")]

    issues: list[ValidationIssue] = []
    for sample_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        issues.extend(validate_sample(sample_dir, expected_sample_rate))
    if not any(path.is_dir() for path in root.iterdir()):
        issues.append(ValidationIssue(str(root), "error", "Dataset directory contains no sample folders"))
    return issues


def _issue(sample_path: Path, severity: str, message: str) -> ValidationIssue:
    return ValidationIssue(str(sample_path), severity, message)

