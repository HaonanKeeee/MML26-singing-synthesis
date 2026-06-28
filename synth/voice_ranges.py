"""Pitch-range compatibility helpers for synthetic voice presets.

The score TSV files do not identify the original singer. These helpers only
decide whether a synthetic voice preset is plausible for the written MIDI range.
They are intentionally permissive because the dataset should still contain some
extended-range examples, but obviously impossible pairings should be skipped.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .score_io import Note


@dataclass(frozen=True)
class ScorePitchStats:
    """Compact pitch summary for one TSV score."""

    minimum: int
    maximum: int
    p05: float
    median: float
    p95: float
    mean: float
    duration_weighted_mean: float
    note_count: int

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)


@dataclass(frozen=True)
class VoiceRangeProfile:
    """Comfortable and allowed MIDI ranges for one synthetic voice family."""

    name: str
    comfortable_low: int
    comfortable_high: int
    allowed_low: int
    allowed_high: int


VOICE_RANGE_PROFILES = {
    "male_low": VoiceRangeProfile("male_low", 40, 64, 36, 67),
    "male_tenor": VoiceRangeProfile("male_tenor", 45, 72, 40, 76),
    "neutral": VoiceRangeProfile("neutral", 48, 76, 43, 80),
    "female_alto": VoiceRangeProfile("female_alto", 52, 76, 48, 80),
    "female_high": VoiceRangeProfile("female_high", 57, 83, 52, 86),
    "child": VoiceRangeProfile("child", 60, 81, 55, 84),
}


def score_pitch_stats(notes: list[Note]) -> ScorePitchStats:
    """Return robust pitch statistics used for voice-range filtering."""

    if not notes:
        raise ValueError("Cannot summarize pitch range for an empty score")

    pitches = np.array([int(round(note.pitch)) for note in notes], dtype=np.float64)
    durations = np.array([max(0.0, note.duration) for note in notes], dtype=np.float64)
    if float(np.sum(durations)) <= 0.0:
        duration_weighted_mean = float(np.mean(pitches))
    else:
        duration_weighted_mean = float(np.average(pitches, weights=durations))
    return ScorePitchStats(
        minimum=int(np.min(pitches)),
        maximum=int(np.max(pitches)),
        p05=float(np.percentile(pitches, 5)),
        median=float(np.percentile(pitches, 50)),
        p95=float(np.percentile(pitches, 95)),
        mean=float(np.mean(pitches)),
        duration_weighted_mean=duration_weighted_mean,
        note_count=int(len(pitches)),
    )


def recommended_gender_for_score(stats: ScorePitchStats) -> str:
    """Recommend `male` or `female` from the score's main sung tessitura.

    The decision uses robust high-percentile range plus duration-weighted center.
    This avoids one short outlier note deciding the singer while still keeping
    high-tessitura songs away from low male presets.
    """

    if stats.p95 >= 70.0 or stats.duration_weighted_mean >= 61.0:
        return "female"
    return "male"


def range_profile_for_voice(gender: str, age: str) -> VoiceRangeProfile:
    """Map the synthetic gender/age preset to a broad singing range profile."""

    if age == "child":
        return VOICE_RANGE_PROFILES["child"]
    if gender == "male":
        if age in ("young", "teen"):
            return VOICE_RANGE_PROFILES["male_tenor"]
        return VOICE_RANGE_PROFILES["male_low"]
    if gender == "female":
        if age in ("young", "teen"):
            return VOICE_RANGE_PROFILES["female_high"]
        return VOICE_RANGE_PROFILES["female_alto"]
    return VOICE_RANGE_PROFILES["neutral"]


def voice_range_status(stats: ScorePitchStats, gender: str, age: str) -> str:
    """Return `comfortable`, `extended`, or `incompatible` for one voice preset."""

    profile = range_profile_for_voice(gender, age)
    if profile.comfortable_low <= stats.p05 and stats.p95 <= profile.comfortable_high:
        return "comfortable"
    if profile.allowed_low <= stats.p05 and stats.p95 <= profile.allowed_high:
        return "extended"
    return "incompatible"


def is_voice_allowed_by_filter(
    stats: ScorePitchStats,
    gender: str,
    age: str,
    filter_mode: str,
) -> bool:
    """Return whether a voice preset should be generated for the filter mode."""

    if filter_mode == "off":
        return True
    status = voice_range_status(stats, gender, age)
    if filter_mode == "comfortable":
        return status == "comfortable"
    if filter_mode == "allowed":
        return status in ("comfortable", "extended")
    raise ValueError(f"Unsupported voice range filter: {filter_mode}")
