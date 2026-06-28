"""Pitch imperfection, vibrato, and transition helpers.

These are audio-expression layers only. They must not change the TSV label.
The planner works at whole-WAV scope first, then assigns note-level details, so
global safety limits such as "at most 10% noticeable detune notes" are enforced
before rendering.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .score_io import Note
from .voice_presets import VoicePreset


NOTICEABLE_DETUNE_MAX_NOTE_FRACTION = 0.10
NOTICEABLE_DETUNE_MAX_DURATION_FRACTION = 0.08
VIBRATO_MIN_NOTE_DURATION_S = 3.00
TRANSITION_MIN_NOTE_DURATION_S = 0.50
TRANSITION_TARGET_ELIGIBLE_FRACTION = 0.60
TRANSITION_MAX_ELIGIBLE_FRACTION = 0.60
TRANSITION_AUDIBLE_DELAY_MAX_S = 0.090
TRANSITION_AUDIBLE_DELAY_FRACTION = 0.18


@dataclass(frozen=True)
class NoteExpression:
    """Per-note expressive pitch settings."""

    detune_cents: float
    detune_type: str
    drift_end_cents: float
    vibrato_rate_hz: float
    vibrato_depth_cents: float
    vibrato_delay_s: float
    transition_type: str
    transition_start_cents: float
    transition_depth_cents: float
    transition_duration_s: float
    transition_shape: str

    def to_dict(self) -> dict[str, float | str]:
        return asdict(self)


@dataclass(frozen=True)
class TransitionSpec:
    """A planned label-preserving pitch approach into a target note."""

    transition_type: str
    start_cents: float
    duration_s: float
    shape: str


def plan_note_expressions(
    notes: list[Note],
    pitch_policy: str,
    vibrato_policy: str,
    transition_policy: str,
    voice: VoicePreset,
    rng: np.random.Generator,
    protected_indices: set[int] | None = None,
) -> tuple[list[NoteExpression], dict[str, float | int | str]]:
    """Plan all note-level pitch expression for one rendered WAV.

    The important constraint is that risky events are selected with whole-WAV
    budgets. Tiny micro-variation is allowed on every note, but noticeable
    stable detune and pitch transitions are capped by note count and duration.
    """

    protected_indices = protected_indices or set()
    noticeable_detune_indices = _select_noticeable_detune_indices(
        notes,
        pitch_policy,
        rng,
        protected_indices,
    )
    transition_specs = _plan_transition_specs(
        notes=notes,
        transition_policy=transition_policy,
        blocked_indices=noticeable_detune_indices | protected_indices,
        rng=rng,
    )

    expressions: list[NoteExpression] = []
    for index, note in enumerate(notes):
        protected = index in protected_indices
        detune_type = "protected" if protected else "noticeable" if index in noticeable_detune_indices else "micro"
        detune_cents = (
            0.0
            if protected
            else _sample_detune(
                pitch_policy=_safe_pitch_policy(pitch_policy),
                stability=voice.pitch_stability,
                noticeable=detune_type == "noticeable",
                rng=rng,
            )
        )
        drift_end_cents = (
            0.0
            if protected or _safe_pitch_policy(pitch_policy) == "intune"
            else float(rng.normal(0.0, 2.0 / max(0.3, voice.pitch_stability)))
        )

        transition = transition_specs.get(index, TransitionSpec("none", 0.0, 0.0, "none"))
        conservative_vibrato = detune_type == "noticeable" or transition.duration_s >= 0.14
        vibrato_rate_hz, vibrato_depth_cents, vibrato_delay_s = _sample_vibrato(
            duration_s=note.duration,
            policy=vibrato_policy,
            conservative=conservative_vibrato,
            rng=rng,
        )

        expressions.append(
            NoteExpression(
                detune_cents=float(detune_cents),
                detune_type=detune_type,
                drift_end_cents=float(drift_end_cents),
                vibrato_rate_hz=float(vibrato_rate_hz),
                vibrato_depth_cents=float(vibrato_depth_cents),
                vibrato_delay_s=float(vibrato_delay_s),
                transition_type=transition.transition_type,
                transition_start_cents=float(transition.start_cents),
                transition_depth_cents=float(abs(transition.start_cents)),
                transition_duration_s=float(transition.duration_s),
                transition_shape=transition.shape,
            )
        )

    return expressions, summarize_expression_plan(notes, expressions, protected_indices)


def sample_note_expression(
    note: Note,
    previous_note: Note | None,
    pitch_policy: str,
    vibrato_policy: str,
    transition_policy: str,
    voice: VoicePreset,
    rng: np.random.Generator,
) -> NoteExpression:
    """Sample one note expression for compatibility with older callers.

    Rendering should prefer `plan_note_expressions()` because it can enforce
    whole-WAV event budgets. This wrapper keeps the public helper usable for
    ad-hoc debugging.
    """

    notes = [previous_note, note] if previous_note is not None else [note]
    expressions, _ = plan_note_expressions(
        notes=[candidate for candidate in notes if candidate is not None],
        pitch_policy=pitch_policy,
        vibrato_policy=vibrato_policy,
        transition_policy=transition_policy,
        voice=voice,
        rng=rng,
    )
    return expressions[-1]


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
        delay_s = min(
            TRANSITION_AUDIBLE_DELAY_MAX_S,
            duration_s * TRANSITION_AUDIBLE_DELAY_FRACTION,
        )
        transition_start = min(
            max(0, n_samples - trans_n),
            int(round(delay_s * sample_rate)),
        )
        transition_end = min(n_samples, transition_start + trans_n)
        cents[:transition_start] += expression.transition_start_cents
        trans_n = transition_end - transition_start
        x = np.linspace(0.0, 1.0, trans_n, dtype=np.float64)
        smooth = x * x * (3.0 - 2.0 * x)
        cents[transition_start:transition_end] += expression.transition_start_cents * (
            1.0 - smooth
        )

    if expression.vibrato_depth_cents > 0.0 and duration_s > expression.vibrato_delay_s:
        start = int(round(expression.vibrato_delay_s * sample_rate))
        vib_t = t[start:] - expression.vibrato_delay_s
        fade_n = min(len(vib_t), int(round(0.20 * sample_rate)))
        fade = np.ones_like(vib_t)
        if fade_n > 1:
            fade[:fade_n] = np.linspace(0.0, 1.0, fade_n)
        cents[start:] += (
            expression.vibrato_depth_cents
            * fade
            * np.sin(2.0 * np.pi * expression.vibrato_rate_hz * vib_t)
        )

    return cents.astype(np.float32)


def summarize_expression_plan(
    notes: list[Note],
    expressions: list[NoteExpression],
    protected_indices: set[int] | None = None,
) -> dict[str, float | int | str]:
    """Summarize the risky note-expression budget used by this WAV."""

    protected_indices = protected_indices or set()
    total_notes = len(notes)
    total_duration_s = float(sum(note.duration for note in notes))
    noticeable_count = sum(expression.detune_type == "noticeable" for expression in expressions)
    noticeable_duration_s = float(
        sum(
            note.duration
            for note, expression in zip(notes, expressions)
            if expression.detune_type == "noticeable"
        )
    )
    transition_count = sum(expression.transition_type != "none" for expression in expressions)
    transition_duration_s = float(
        sum(expression.transition_duration_s for expression in expressions)
    )
    eligible_transition_count = sum(
        note.duration >= TRANSITION_MIN_NOTE_DURATION_S
        and index not in protected_indices
        and expressions[index].detune_type != "noticeable"
        for index, note in enumerate(notes)
    )
    vibrato_count = sum(expression.vibrato_depth_cents > 0.0 for expression in expressions)
    eligible_vibrato_count = sum(note.duration >= VIBRATO_MIN_NOTE_DURATION_S for note in notes)

    return {
        "total_notes": total_notes,
        "total_note_duration_s": total_duration_s,
        "noticeable_detune_count": noticeable_count,
        "noticeable_detune_note_fraction": _safe_fraction(noticeable_count, total_notes),
        "noticeable_detune_duration_s": noticeable_duration_s,
        "noticeable_detune_duration_fraction": _safe_fraction(
            noticeable_duration_s, total_duration_s
        ),
        "transition_count": transition_count,
        "transition_note_fraction": _safe_fraction(transition_count, total_notes),
        "transition_duration_s": transition_duration_s,
        "eligible_transition_count": eligible_transition_count,
        "transition_eligible_fraction": _safe_fraction(
            transition_count,
            eligible_transition_count,
        ),
        "transition_target_eligible_fraction": TRANSITION_TARGET_ELIGIBLE_FRACTION,
        "transition_min_note_duration_s": TRANSITION_MIN_NOTE_DURATION_S,
        "transition_curve": "smoothstep",
        "vibrato_count": vibrato_count,
        "vibrato_note_fraction": _safe_fraction(vibrato_count, total_notes),
        "eligible_vibrato_count": eligible_vibrato_count,
        "vibrato_min_note_duration_s": VIBRATO_MIN_NOTE_DURATION_S,
        "extra_unlabeled_melisma": "disabled",
        "protected_continuation_note_count": len(protected_indices),
        "decorative_transitions_on_continuations": False,
        "noticeable_detune_on_continuations": False,
    }


def _safe_pitch_policy(pitch_policy: str) -> str:
    """Return a known pitch policy name, preserving strict behavior locally."""

    if pitch_policy in ("intune", "mild_detune", "expressive_detune"):
        return pitch_policy
    return "intune"


def _select_noticeable_detune_indices(
    notes: list[Note],
    pitch_policy: str,
    rng: np.random.Generator,
    protected_indices: set[int],
) -> set[int]:
    """Select a capped set of notes that may have audible stable detune."""

    if not notes:
        return set()

    target_fraction = {
        "intune": 0.00,
        "mild_detune": 0.06,
        "expressive_detune": 0.10,
    }.get(pitch_policy, 0.02)
    max_count = int(np.floor(len(notes) * NOTICEABLE_DETUNE_MAX_NOTE_FRACTION))
    desired_count = int(round(len(notes) * target_fraction))
    desired_count = min(max_count, desired_count)
    if desired_count <= 0:
        return set()

    total_duration = float(sum(note.duration for note in notes))
    duration_cap = total_duration * NOTICEABLE_DETUNE_MAX_DURATION_FRACTION
    selected: set[int] = set()
    used_duration = 0.0

    candidate_indices = [
        int(index)
        for index in rng.permutation(len(notes))
        if int(index) not in protected_indices
    ]
    for index in candidate_indices:
        candidate_duration = notes[index].duration
        if used_duration + candidate_duration > duration_cap:
            continue
        selected.add(index)
        used_duration += candidate_duration
        if len(selected) >= desired_count:
            break

    return selected


def _plan_transition_specs(
    notes: list[Note],
    transition_policy: str,
    blocked_indices: set[int],
    rng: np.random.Generator,
) -> dict[int, TransitionSpec]:
    """Select long-note pitch approaches with whole-WAV safety caps."""

    if transition_policy == "none" or not notes:
        return {}

    eligible = [
        index
        for index, note in enumerate(notes)
        if note.duration >= TRANSITION_MIN_NOTE_DURATION_S and index not in blocked_indices
    ]
    if not eligible:
        return {}

    max_by_eligible = int(round(len(eligible) * TRANSITION_MAX_ELIGIBLE_FRACTION))
    desired_count = int(round(len(eligible) * TRANSITION_TARGET_ELIGIBLE_FRACTION))
    desired_count = min(max_by_eligible, desired_count)
    if desired_count <= 0:
        return {}

    weights = np.array([notes[index].duration for index in eligible], dtype=np.float64)
    selected = _weighted_sample_without_replacement(eligible, weights, len(eligible), rng)
    specs: dict[int, TransitionSpec] = {}
    for index in selected:
        spec = _sample_transition_for_note(index, notes, transition_policy, rng)
        if spec.transition_type != "none":
            specs[index] = spec
        if len(specs) >= desired_count:
            break
    return specs


def _sample_transition_for_note(
    index: int,
    notes: list[Note],
    transition_policy: str,
    rng: np.random.Generator,
) -> TransitionSpec:
    note = notes[index]
    previous_note = notes[index - 1] if index > 0 else None
    connected_to_previous = (
        previous_note is not None and 0.0 <= note.onset - previous_note.offset < 0.12
    )

    transition_type = _sample_transition_type(note, previous_note, connected_to_previous, rng)
    duration_s, duration_class = _sample_transition_duration(note.duration, rng)
    start_cents = _sample_transition_start_cents(
        transition_type=transition_type,
        duration_class=duration_class,
        note=note,
        previous_note=previous_note,
        transition_policy=transition_policy,
        rng=rng,
    )
    if abs(start_cents) < 1e-6:
        transition_type = str(rng.choice(["low_to_target_scoop", "high_to_target_fall_in"], p=[0.90, 0.10]))
        start_cents = _sample_transition_start_cents(
            transition_type=transition_type,
            duration_class=duration_class,
            note=note,
            previous_note=previous_note,
            transition_policy=transition_policy,
            rng=rng,
        )
    return TransitionSpec(
        transition_type=transition_type,
        start_cents=float(start_cents),
        duration_s=float(duration_s),
        shape="smoothstep",
    )


def _sample_transition_type(
    note: Note,
    previous_note: Note | None,
    connected_to_previous: bool,
    rng: np.random.Generator,
) -> str:
    """Choose transition direction with a strong below-to-target bias."""

    labels = ["low_to_target_scoop", "high_to_target_fall_in"]
    weights = [0.90, 0.10]

    weights_array = np.array(weights, dtype=np.float64)
    weights_array /= weights_array.sum()
    return str(rng.choice(labels, p=weights_array))


def _sample_transition_duration(
    note_duration_s: float,
    rng: np.random.Generator,
) -> tuple[float, str]:
    """Sample transition duration as a note-length-proportional value."""

    labels = ["short", "medium", "long"]
    weights = np.array([0.50, 0.40, 0.10], dtype=np.float64)
    if note_duration_s < 2.50:
        weights[2] = 0.0
        weights /= weights.sum()

    duration_class = str(rng.choice(labels, p=weights))
    if duration_class == "short":
        fraction = float(rng.uniform(0.08, 0.12))
        lower, upper = 0.060, 0.120
    elif duration_class == "medium":
        fraction = float(rng.uniform(0.12, 0.18))
        lower, upper = 0.110, 0.190
    else:
        fraction = float(rng.uniform(0.18, 0.24))
        lower, upper = 0.180, 0.280

    duration_s = float(np.clip(note_duration_s * fraction, lower, upper))
    duration_s = min(duration_s, note_duration_s * 0.30)
    return duration_s, duration_class


def _sample_transition_start_cents(
    transition_type: str,
    duration_class: str,
    note: Note,
    previous_note: Note | None,
    transition_policy: str,
    rng: np.random.Generator,
) -> float:
    if transition_type == "short_portamento_from_previous_note":
        if previous_note is None:
            return 0.0
        return -100.0 if previous_note.pitch < note.pitch else 100.0
    if transition_type == "low_to_target_scoop":
        return -100.0
    if transition_type == "high_to_target_fall_in":
        return 100.0
    return 0.0


def _sample_detune(
    pitch_policy: str,
    stability: float,
    noticeable: bool,
    rng: np.random.Generator,
) -> float:
    """Sample stable pitch-center detune in cents."""

    stability = max(0.3, stability)
    if not noticeable:
        if pitch_policy == "intune":
            return 0.0
        limit = {"intune": 6.0, "mild_detune": 8.0, "expressive_detune": 10.0}.get(
            pitch_policy, 6.0
        )
        return float(np.clip(rng.normal(0.0, limit / 3.0 / stability), -limit, limit))

    bands = [(10.0, 25.0, 0.70), (25.0, 40.0, 0.25), (40.0, 50.0, 0.05)]
    if pitch_policy == "intune":
        bands = [(8.0, 18.0, 0.80), (18.0, 25.0, 0.20)]
    weights = np.array([band[2] for band in bands], dtype=np.float64)
    weights /= weights.sum()
    band_index = int(rng.choice(len(bands), p=weights))
    low, high, _ = bands[band_index]
    sign = -1.0 if rng.random() < 0.5 else 1.0
    return float(np.clip(sign * rng.uniform(low, high) / stability, -50.0, 50.0))


def _sample_vibrato(
    duration_s: float,
    policy: str,
    conservative: bool,
    rng: np.random.Generator,
) -> tuple[float, float, float]:
    if duration_s < VIBRATO_MIN_NOTE_DURATION_S or policy == "none":
        return 0.0, 0.0, 0.0

    if policy == "light":
        probability, low, high = 0.45, 10.0, 16.0
    elif policy == "normal":
        probability, low, high = 0.65, 12.0, 25.0
    else:
        probability, low, high = 0.75, 18.0, 35.0

    if conservative:
        high = min(high, 7.0)
        low = min(low, high * 0.5)

    rate = float(rng.uniform(4.80, 5.80))
    depth = float(rng.uniform(low, high))
    delay = float(min(duration_s * 0.70, rng.uniform(0.80, 1.20)))
    return rate, depth, delay


def _weighted_sample_without_replacement(
    candidates: list[int],
    weights: np.ndarray,
    count: int,
    rng: np.random.Generator,
) -> list[int]:
    if count <= 0 or not candidates:
        return []
    weights = weights.astype(np.float64)
    if float(weights.sum()) <= 0.0:
        weights = np.ones_like(weights)
    probabilities = weights / weights.sum()
    count = min(count, len(candidates))
    return [
        int(value)
        for value in rng.choice(candidates, size=count, replace=False, p=probabilities)
    ]


def _safe_fraction(numerator: float | int, denominator: float | int) -> float:
    denominator = float(denominator)
    if denominator <= 0.0:
        return 0.0
    return float(numerator) / denominator
