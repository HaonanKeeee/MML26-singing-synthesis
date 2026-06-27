"""Pitch imperfection, vibrato, and transition helpers.

These are audio-expression layers only. They must not change the TSV label.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .score_io import Note
from .voice_presets import VoicePreset


@dataclass(frozen=True)
class NoteExpression:
    """Per-note expressive pitch settings."""

    detune_cents: float
    drift_end_cents: float
    vibrato_rate_hz: float
    vibrato_depth_cents: float
    vibrato_delay_s: float
    transition_type: str
    transition_depth_cents: float
    transition_duration_s: float

    def to_dict(self) -> dict[str, float | str]:
        return asdict(self)


def sample_note_expression(
    note: Note,
    previous_note: Note | None,
    pitch_policy: str,
    vibrato_policy: str,
    transition_policy: str,
    voice: VoicePreset,
    rng: np.random.Generator,
) -> NoteExpression:
    """Sample safe note-level pitch expression."""

    detune_cents = _sample_detune(pitch_policy, voice.pitch_stability, rng)
    drift_end_cents = float(rng.normal(0.0, 2.0 / max(0.3, voice.pitch_stability)))
    vibrato_rate_hz, vibrato_depth_cents, vibrato_delay_s = _sample_vibrato(
        note.duration, vibrato_policy, rng
    )
    transition_type, transition_depth_cents, transition_duration_s = _sample_transition(
        note, previous_note, transition_policy, rng
    )

    return NoteExpression(
        detune_cents=float(detune_cents),
        drift_end_cents=float(drift_end_cents),
        vibrato_rate_hz=float(vibrato_rate_hz),
        vibrato_depth_cents=float(vibrato_depth_cents),
        vibrato_delay_s=float(vibrato_delay_s),
        transition_type=transition_type,
        transition_depth_cents=float(transition_depth_cents),
        transition_duration_s=float(transition_duration_s),
    )


def build_cents_curve(
    duration_s: float,
    sample_rate: int,
    expression: NoteExpression,
) -> np.ndarray:
    """Build a cents curve centered around the labeled pitch."""

    n_samples = max(1, int(round(duration_s * sample_rate)))
    t = np.arange(n_samples, dtype=np.float64) / sample_rate
    cents = np.full(n_samples, expression.detune_cents, dtype=np.float64)

    if n_samples > 1:
        cents += np.linspace(0.0, expression.drift_end_cents, n_samples)

    trans_n = min(n_samples, int(round(expression.transition_duration_s * sample_rate)))
    if trans_n > 1 and expression.transition_type != "none":
        start_offset = _transition_start_cents(expression)
        curve = np.linspace(start_offset, 0.0, trans_n)
        cents[:trans_n] += curve

    if expression.vibrato_depth_cents > 0.0 and duration_s > expression.vibrato_delay_s:
        start = int(round(expression.vibrato_delay_s * sample_rate))
        vib_t = t[start:] - expression.vibrato_delay_s
        fade_n = min(len(vib_t), int(round(0.08 * sample_rate)))
        fade = np.ones_like(vib_t)
        if fade_n > 1:
            fade[:fade_n] = np.linspace(0.0, 1.0, fade_n)
        cents[start:] += (
            expression.vibrato_depth_cents
            * fade
            * np.sin(2.0 * np.pi * expression.vibrato_rate_hz * vib_t)
        )

    return cents.astype(np.float32)


def _sample_detune(policy: str, stability: float, rng: np.random.Generator) -> float:
    if policy == "intune":
        limit = 8.0
    elif policy == "mild_detune":
        limit = 25.0
    else:
        limit = 40.0
    return float(np.clip(rng.normal(0.0, limit / 2.5 / max(0.3, stability)), -limit, limit))


def _sample_vibrato(
    duration_s: float,
    policy: str,
    rng: np.random.Generator,
) -> tuple[float, float, float]:
    if duration_s < 0.35 or policy == "none":
        return 0.0, 0.0, 0.0

    if policy == "light":
        probability, low, high = 0.45, 5.0, 15.0
    elif policy == "normal":
        probability, low, high = 0.65, 10.0, 35.0
    else:
        probability, low, high = 0.75, 25.0, 50.0

    if rng.random() > probability:
        return 0.0, 0.0, 0.0
    rate = float(rng.uniform(4.2, 6.8))
    depth = float(rng.uniform(low, high))
    delay = float(min(duration_s * 0.45, rng.uniform(0.12, 0.28)))
    return rate, depth, delay


def _sample_transition(
    note: Note,
    previous_note: Note | None,
    policy: str,
    rng: np.random.Generator,
) -> tuple[str, float, float]:
    if policy == "none" or note.duration <= 0.25:
        return "none", 0.0, 0.0

    if policy == "light_scoop":
        probability, depth_max, dur_max = 0.18, 20.0, 0.050
    elif policy == "pop_scoop":
        probability, depth_max, dur_max = 0.35, 35.0, 0.060
    else:
        probability, depth_max, dur_max = 0.45, 50.0, 0.080

    if rng.random() > probability:
        return "none", 0.0, 0.0

    if previous_note is not None and note.pitch < previous_note.pitch:
        event = "high_to_target_fall_in"
    elif previous_note is not None and note.pitch > previous_note.pitch:
        event = "low_to_target_scoop"
    else:
        event = str(rng.choice(["low_to_target_scoop", "high_to_target_fall_in"]))

    if previous_note is not None and note.onset - previous_note.offset < 0.08 and rng.random() < 0.25:
        event = "short_portamento_from_previous_note"

    duration = min(dur_max, note.duration * 0.15)
    depth = float(rng.uniform(8.0, depth_max))
    return event, depth, duration


def _transition_start_cents(expression: NoteExpression) -> float:
    if expression.transition_type in ("low_to_target_scoop", "short_portamento_from_previous_note"):
        return -abs(expression.transition_depth_cents)
    if expression.transition_type == "high_to_target_fall_in":
        return abs(expression.transition_depth_cents)
    if expression.transition_type == "tiny_turn_around_target":
        return -0.5 * abs(expression.transition_depth_cents)
    return 0.0

