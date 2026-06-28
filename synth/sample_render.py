"""Sample-based rendering using short TTS word units.

This renderer uses WORLD vocoder resynthesis so the selected word unit itself
follows the TSV target F0 curve. It must not add a separate pitched carrier
behind an unpitched spoken word.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

from .envelopes import note_envelope
from .ornaments import build_cents_curve, plan_note_expressions
from .pitch import midi_to_hz_with_cents
from .policies import GenerationPolicy
from .score_io import Note, split_phrases, write_score_tsv
from .syllable_groups import GROUP_SELECTION_FRACTION, grouped_indices, plan_syllable_groups
from .unit_bank import AudioUnit, AudioUnitBank
from .voice_presets import make_voice_preset


DEFAULT_SAMPLE_RATE = 16_000
WORLD_FRAME_PERIOD_MS = 5.0
DEFAULT_VOICED_START_FRACTION = 0.03
DEFAULT_VOICED_END_FRACTION = 0.98
NOTE_RELEASE_MIN_S = 0.006
NOTE_RELEASE_MAX_S = 0.024
NOTE_RELEASE_DURATION_FRACTION = 0.06
GROUP_RELEASE_MIN_S = 0.006
GROUP_RELEASE_MAX_S = 0.028
GROUP_RELEASE_DURATION_FRACTION = 0.07
GROUP_SEGMENT_CROSSFADE_S = 0.012
STABLE_VOWEL_MIN_S = 0.060
STABLE_VOWEL_MAX_S = 0.140
MELISMA_FRIENDLY_UNIT_KEYS = frozenset(
    {
        "a",
        "i",
        "la",
        "oh",
    }
)


@dataclass(frozen=True)
class WorldAnalysis:
    """WORLD vocoder parameters for one source word unit."""

    f0: np.ndarray
    spectral_envelope: np.ndarray
    aperiodicity: np.ndarray


_WORLD_ANALYSIS_CACHE: dict[tuple[str, int], WorldAnalysis] = {}


def render_score_to_word_unit_sample(
    notes: list[Note],
    output_dir: str | Path,
    policy: GenerationPolicy,
    source_score: str,
    unit_bank: AudioUnitBank,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    melisma_selection_fraction: float | None = None,
    melisma_unit_keys: tuple[str, ...] | None = None,
) -> dict:
    """Render one score by resynthesizing word units to TSV note pitches."""

    if unit_bank.sample_rate != sample_rate:
        raise ValueError(
            f"Unit bank sample rate {unit_bank.sample_rate} does not match render sample rate {sample_rate}"
        )

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(policy.seed)
    voice = make_voice_preset(policy.gender, policy.age, policy.style, rng)
    phrases = split_phrases(notes)
    group_marks, syllable_group_summary = plan_syllable_groups(
        notes,
        rng,
        selection_fraction=(
            melisma_selection_fraction
            if melisma_selection_fraction is not None
            else GROUP_SELECTION_FRACTION
        ),
    )
    melisma_unit_keys = _normalize_melisma_unit_keys(melisma_unit_keys)
    selected_voice_label = _choose_voice_label(unit_bank, policy.gender, rng)
    selected_units = unit_bank.units_by_voice[selected_voice_label]
    note_units = _choose_units_for_notes(
        note_count=len(notes),
        phrases=phrases,
        units=selected_units,
        group_marks=group_marks,
        melisma_unit_keys=melisma_unit_keys,
        rng=rng,
    )
    expressions, expression_summary = plan_note_expressions(
        notes=notes,
        pitch_policy=policy.pitch_policy,
        vibrato_policy=policy.vibrato_policy,
        transition_policy=policy.pitch_transition_policy,
        voice=voice,
        rng=rng,
        protected_indices=grouped_indices(group_marks),
    )

    total_duration = max(note.offset for note in notes) + 0.12
    audio = np.zeros(int(np.ceil(total_duration * sample_rate)), dtype=np.float32)
    metadata_notes = []

    groups_by_id = _groups_by_id(group_marks)

    for index, note in enumerate(notes):
        unit = note_units[index]
        group_mark = group_marks[index]
        expression = expressions[index]
        note_start_sample, note_end_sample = _note_sample_bounds(note, sample_rate)

        if group_mark.group_id is not None and group_mark.group_size > 1:
            if group_mark.group_position == 0:
                group_indices = groups_by_id[group_mark.group_id]
                unit_audio = unit_bank.load_audio(unit)
                group_audio = _render_word_unit_group(
                    notes=[notes[group_index] for group_index in group_indices],
                    unit_audio=unit_audio,
                    unit_cache_key=str(unit.wav_path),
                    expressions=[expressions[group_index] for group_index in group_indices],
                    style=policy.style,
                    age=policy.age,
                    sample_rate=sample_rate,
                    rng=rng,
                )
                group_start_sample, group_end_sample = _time_sample_bounds(
                    notes[group_indices[0]].onset,
                    notes[group_indices[-1]].offset,
                    sample_rate,
                )
                expected_group_samples = group_end_sample - group_start_sample
                _require_exact_length(
                    group_audio,
                    expected_group_samples,
                    context=f"group {group_mark.group_id}",
                )
                start = group_start_sample
                end = min(len(audio), group_end_sample)
                if end > start:
                    audio[start:end] += group_audio[: end - start]
        else:
            unit_audio = unit_bank.load_audio(unit)
            note_audio = _render_word_unit_note(
                note=note,
                unit_audio=unit_audio,
                unit_cache_key=str(unit.wav_path),
                expression=expression,
                is_continuation=False,
                style=policy.style,
                age=policy.age,
                sample_rate=sample_rate,
                rng=rng,
            )
            _require_exact_length(
                note_audio,
                note_end_sample - note_start_sample,
                context=f"note {index}",
            )

            start = note_start_sample
            end = min(len(audio), note_end_sample)
            if end > start:
                audio[start:end] += note_audio[: end - start]

        metadata_notes.append(
            {
                "index": index,
                "onset": note.onset,
                "offset": note.offset,
                "pitch": note.pitch,
                "render_start_sample": note_start_sample,
                "render_end_sample": note_end_sample,
                "render_duration_samples": note_end_sample - note_start_sample,
                "word_unit": unit.key,
                "word_text": unit.text,
                "word_voice_label": unit.voice_label,
                "word_edge_voice": unit.edge_voice,
                "render_mode": _render_mode_for_group_mark(group_mark),
                **group_mark.to_dict(),
                **expression.to_dict(),
            }
        )

    audio = _safe_normalize(audio)

    audio_path = output_path / "audio.wav"
    score_path = output_path / "score.tsv"
    metadata_path = output_path / "metadata.json"

    sf.write(audio_path, audio, sample_rate)
    write_score_tsv(score_path, notes)

    metadata = {
        "source_score": source_score,
        "sample_rate": sample_rate,
        "renderer": "edge_tts_word_units_world",
        "unit_bank": str(unit_bank.root),
        "policy": policy.to_dict(),
        "voice": voice.to_dict(),
        "selected_unit_voice_label": selected_voice_label,
        "melisma_unit_keys": list(melisma_unit_keys),
        "syllable_group_summary": syllable_group_summary,
        "expression_summary": expression_summary,
        "notes": metadata_notes,
        "todos": [
            "TODO: Improve long-note word stretching so consonants are not over-extended.",
            "TODO: Confirm edge-tts usage terms before final training/submission use.",
        ],
    }
    metadata_path.write_text(json.dumps(metadata, indent=2))
    return metadata


def _choose_voice_label(
    unit_bank: AudioUnitBank,
    policy_gender: str,
    rng: np.random.Generator,
) -> str:
    labels = unit_bank.voice_labels_for_gender(policy_gender)
    return str(rng.choice(labels))


def _choose_units_for_notes(
    note_count: int,
    phrases: list[list[int]],
    units: list[AudioUnit],
    group_marks,
    melisma_unit_keys: tuple[str, ...],
    rng: np.random.Generator,
) -> list[AudioUnit]:
    """Assign word units while making same-word reuse explicit.

    A word may span several TSV pitches only when those notes were selected as
    a same-syllable group. Ordinary adjacent notes must get different units so
    unselected pitch changes do not accidentally sound like melisma.
    """

    result: list[AudioUnit | None] = [None] * note_count
    group_units: dict[int, AudioUnit] = {}
    for phrase in phrases:
        previous: AudioUnit | None = None
        for note_index in phrase:
            mark = group_marks[note_index]
            if mark.group_id is not None and mark.group_position > 0:
                continue

            candidate = _choose_different_unit(units, previous=previous, rng=rng)
            if mark.group_id is not None:
                candidate = _choose_melisma_unit(
                    units=units,
                    current=candidate,
                    melisma_unit_keys=melisma_unit_keys,
                    rng=rng,
                    previous=previous,
                )
                group_units[mark.group_id] = candidate

            result[note_index] = candidate
            previous = candidate

    assigned = [unit if unit is not None else units[0] for unit in result]
    for index, mark in enumerate(group_marks):
        if mark.group_id is None or mark.group_position == 0:
            continue
        assigned[index] = group_units.get(mark.group_id, assigned[index])

    return assigned


def _choose_different_unit(
    units: list[AudioUnit],
    previous: AudioUnit | None,
    rng: np.random.Generator,
) -> AudioUnit:
    if previous is None or len(units) == 1:
        return units[int(rng.integers(0, len(units)))]

    for _ in range(8):
        candidate = units[int(rng.integers(0, len(units)))]
        if candidate.key != previous.key:
            return candidate
    return units[int(rng.integers(0, len(units)))]


def _choose_melisma_unit(
    units: list[AudioUnit],
    current: AudioUnit,
    melisma_unit_keys: tuple[str, ...],
    rng: np.random.Generator,
    previous: AudioUnit | None = None,
) -> AudioUnit:
    """Choose a unit whose vowel can plausibly carry several TSV pitches."""

    if (
        _is_melisma_friendly_unit(current, melisma_unit_keys)
        and (previous is None or current.key != previous.key)
        and rng.random() < 0.35
    ):
        return current

    candidates = [
        unit
        for unit in units
        if _is_melisma_friendly_unit(unit, melisma_unit_keys)
        and (previous is None or unit.key != previous.key)
    ]
    if not candidates:
        candidates = [unit for unit in units if _is_melisma_friendly_unit(unit, melisma_unit_keys)]
    if not candidates:
        return current
    return candidates[int(rng.integers(0, len(candidates)))]


def _is_melisma_friendly_unit(unit: AudioUnit, melisma_unit_keys: tuple[str, ...]) -> bool:
    return unit.key.lower() in melisma_unit_keys or unit.text.lower() in melisma_unit_keys


def _normalize_melisma_unit_keys(raw_keys: tuple[str, ...] | None) -> tuple[str, ...]:
    keys = raw_keys if raw_keys is not None else tuple(sorted(MELISMA_FRIENDLY_UNIT_KEYS))
    normalized = tuple(sorted({key.strip().lower() for key in keys if key.strip()}))
    return normalized or tuple(sorted(MELISMA_FRIENDLY_UNIT_KEYS))


def _groups_by_id(group_marks) -> dict[int, list[int]]:
    """Return note indices for every selected same-syllable group."""

    groups: dict[int, list[int]] = {}
    for index, mark in enumerate(group_marks):
        if mark.group_id is None:
            continue
        groups.setdefault(int(mark.group_id), []).append(index)
    return groups


def _render_mode_for_group_mark(group_mark) -> str:
    if group_mark.group_id is None:
        return "single_note"
    if group_mark.group_position == 0:
        return "same_syllable_group_start"
    return "same_syllable_group_continuation"


def _note_sample_bounds(note: Note, sample_rate: int) -> tuple[int, int]:
    return _time_sample_bounds(note.onset, note.offset, sample_rate)


def _time_sample_bounds(onset: float, offset: float, sample_rate: int) -> tuple[int, int]:
    start = max(0, int(round(onset * sample_rate)))
    end = int(round(offset * sample_rate))
    return start, max(start + 1, end)


def _require_exact_length(audio: np.ndarray, expected_samples: int, context: str) -> None:
    actual_samples = int(np.asarray(audio).shape[0])
    if actual_samples != expected_samples:
        raise RuntimeError(
            f"Rendered {context} has {actual_samples} samples, expected {expected_samples}. "
            "This would shift TSV onset/offset timing in the generated WAV."
        )


def _render_word_unit_note(
    note: Note,
    unit_audio: np.ndarray,
    unit_cache_key: str,
    expression,
    is_continuation: bool,
    style: str,
    age: str,
    sample_rate: int,
    rng: np.random.Generator,
) -> np.ndarray:
    start_sample, end_sample = _note_sample_bounds(note, sample_rate)
    n_samples = end_sample - start_sample
    source = _prepare_unit_source(unit_audio, is_continuation)
    texture = _world_resynthesize_to_note(
        source=source,
        cache_key=f"{unit_cache_key}:continuation={is_continuation}",
        note=note,
        expression=expression,
        sample_rate=sample_rate,
    )
    texture = _fit_source_to_length(texture, n_samples)
    texture = _shape_texture(texture, style=style, age=age, sample_rate=sample_rate, rng=rng)

    env = note_envelope(
        n_samples=n_samples,
        sample_rate=sample_rate,
        attack_s=_attack_s(note.duration, is_continuation, style, rng),
        release_s=_release_s(note.duration, grouped=False),
    )
    loudness = float(rng.uniform(0.86, 1.06))
    out = (texture * env * loudness).astype(np.float32)
    _require_exact_length(out, n_samples, context="single note render")
    return out


def _render_word_unit_group(
    notes: list[Note],
    unit_audio: np.ndarray,
    unit_cache_key: str,
    expressions,
    style: str,
    age: str,
    sample_rate: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Render one sung syllable across multiple TSV notes as one continuous unit.

    The first note carries the word onset. Later notes reuse the same word's
    vowel-like center so the TSV pitch changes sound like one sustained syllable
    rather than separate word attacks.
    """

    group_onset = notes[0].onset
    group_start_sample, group_end_sample = _time_sample_bounds(
        notes[0].onset,
        notes[-1].offset,
        sample_rate,
    )
    n_samples = group_end_sample - group_start_sample
    first_note_start, first_note_end = _note_sample_bounds(notes[0], sample_rate)
    first_note_samples = first_note_end - first_note_start
    onset, vowel_core = _prepare_group_sources(
        unit_audio=unit_audio,
        first_note_samples=first_note_samples,
        sample_rate=sample_rate,
    )
    texture = np.zeros(n_samples, dtype=np.float32)
    cursor = 0
    crossfade_n = max(1, int(round(sample_rate * GROUP_SEGMENT_CROSSFADE_S)))

    for position, (note, expression) in enumerate(zip(notes, expressions)):
        note_start_sample, note_end_sample = _note_sample_bounds(note, sample_rate)
        note_samples = note_end_sample - note_start_sample
        is_first = position == 0
        is_last = position == len(notes) - 1
        if is_first:
            source = _build_group_start_source(onset, vowel_core, note_samples)
            source_key = f"{unit_cache_key}:melisma_start:{source.size}"
            attack_s = _attack_s(note.duration, False, style, rng)
        else:
            source = _build_group_continuation_source(vowel_core, note_samples, sample_rate)
            source_key = f"{unit_cache_key}:melisma_vowel:{source.size}"
            attack_s = 0.0

        segment = _world_resynthesize_to_note(
            source=source,
            cache_key=source_key,
            note=note,
            expression=expression,
            sample_rate=sample_rate,
        )
        segment = _fit_source_to_length(segment, note_samples)
        segment *= _segment_envelope(
            n_samples=note_samples,
            sample_rate=sample_rate,
            attack_s=attack_s,
            release_s=_release_s(note.duration, grouped=True) if is_last else 0.0,
        )

        scheduled_start = note_start_sample - group_start_sample
        start = scheduled_start
        cursor = _mix_segment_with_crossfade(
            target=texture,
            segment=segment,
            start=start,
            cursor=cursor,
            crossfade_n=crossfade_n,
        )

    texture = _shape_texture(texture, style=style, age=age, sample_rate=sample_rate, rng=rng)
    loudness = float(rng.uniform(0.86, 1.06))
    out = (texture * loudness).astype(np.float32)
    _require_exact_length(out, n_samples, context="same-syllable group render")
    return out


def _world_resynthesize_to_note(
    source: np.ndarray,
    cache_key: str,
    note: Note,
    expression,
    sample_rate: int,
) -> np.ndarray:
    """Resynthesize a source word so its voiced frames follow the TSV pitch."""

    pw = _import_pyworld()
    start_sample, end_sample = _note_sample_bounds(note, sample_rate)
    n_samples = end_sample - start_sample
    duration_s = n_samples / float(sample_rate)
    analysis = _world_analyze(source, cache_key, sample_rate)
    target_frame_count = max(2, int(np.ceil(duration_s * 1000.0 / WORLD_FRAME_PERIOD_MS)) + 1)

    spectral_envelope = _resize_feature_matrix(
        analysis.spectral_envelope,
        target_frame_count,
    )
    aperiodicity = _resize_feature_matrix(
        analysis.aperiodicity,
        target_frame_count,
    )
    voiced_mask = _resize_voiced_mask(analysis.f0 > 0.0, target_frame_count)

    target_f0 = _target_f0_curve(
        note=note,
        expression=expression,
        sample_rate=sample_rate,
        target_frame_count=target_frame_count,
        duration_s=duration_s,
    )
    target_f0 = np.where(voiced_mask, target_f0, 0.0).astype(np.float64)

    resynthesized = pw.synthesize(
        target_f0,
        spectral_envelope.astype(np.float64),
        aperiodicity.astype(np.float64),
        sample_rate,
        frame_period=WORLD_FRAME_PERIOD_MS,
    )
    return _fit_source_to_length(resynthesized.astype(np.float32), n_samples)


def _world_resynthesize_to_notes(
    source: np.ndarray,
    cache_key: str,
    notes: list[Note],
    expressions,
    group_onset: float,
    sample_rate: int,
    n_samples: int,
) -> np.ndarray:
    """Resynthesize one word source over a multi-note target F0 curve."""

    pw = _import_pyworld()
    duration_s = max(0.001, n_samples / float(sample_rate))
    analysis = _world_analyze(source, cache_key, sample_rate)
    target_frame_count = max(2, int(np.ceil(duration_s * 1000.0 / WORLD_FRAME_PERIOD_MS)) + 1)

    spectral_envelope = _resize_feature_matrix(
        analysis.spectral_envelope,
        target_frame_count,
    )
    aperiodicity = _resize_feature_matrix(
        analysis.aperiodicity,
        target_frame_count,
    )
    voiced_mask = _resize_voiced_mask(analysis.f0 > 0.0, target_frame_count)
    target_f0 = _target_f0_curve_for_notes(
        notes=notes,
        expressions=expressions,
        group_onset=group_onset,
        sample_rate=sample_rate,
        n_samples=n_samples,
        target_frame_count=target_frame_count,
    )
    target_f0 = np.where(voiced_mask, target_f0, 0.0).astype(np.float64)

    resynthesized = pw.synthesize(
        target_f0,
        spectral_envelope.astype(np.float64),
        aperiodicity.astype(np.float64),
        sample_rate,
        frame_period=WORLD_FRAME_PERIOD_MS,
    )
    return _fit_source_to_length(resynthesized.astype(np.float32), n_samples)


def _world_analyze(source: np.ndarray, cache_key: str, sample_rate: int) -> WorldAnalysis:
    pw = _import_pyworld()
    cached = _WORLD_ANALYSIS_CACHE.get((cache_key, sample_rate))
    if cached is not None:
        return cached

    source = np.asarray(source, dtype=np.float64)
    if source.size < max(32, int(round(sample_rate * 0.04))):
        source = np.pad(source, (0, max(32, int(round(sample_rate * 0.04))) - source.size))
    peak = float(np.max(np.abs(source))) if source.size else 0.0
    if peak > 1e-8:
        source = source / peak * 0.80

    f0, time_axis = pw.harvest(
        source,
        sample_rate,
        f0_floor=55.0,
        f0_ceil=880.0,
        frame_period=WORLD_FRAME_PERIOD_MS,
    )
    f0 = pw.stonemask(source, f0, time_axis, sample_rate)
    spectral_envelope = pw.cheaptrick(source, f0, time_axis, sample_rate)
    aperiodicity = pw.d4c(source, f0, time_axis, sample_rate)

    analysis = WorldAnalysis(
        f0=f0.astype(np.float64),
        spectral_envelope=spectral_envelope.astype(np.float64),
        aperiodicity=aperiodicity.astype(np.float64),
    )
    _WORLD_ANALYSIS_CACHE[(cache_key, sample_rate)] = analysis
    return analysis


def _import_pyworld():
    try:
        import pyworld as pw
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The WORLD renderer requires `pyworld` and its runtime dependency "
            "`setuptools`/`pkg_resources`. Run "
            "`../.venv/bin/python -m pip install setuptools pyworld` in the project "
            "environment, then regenerate with `--renderer edge_tts_words`."
        ) from exc
    return pw


def _target_f0_curve(
    note: Note,
    expression,
    sample_rate: int,
    target_frame_count: int,
    duration_s: float | None = None,
) -> np.ndarray:
    duration_s = note.duration if duration_s is None else duration_s
    cents = build_cents_curve(duration_s, sample_rate, expression)
    sample_f0 = midi_to_hz_with_cents(note.pitch, cents)
    sample_times = np.arange(len(sample_f0), dtype=np.float64) / float(sample_rate)
    frame_times = np.arange(target_frame_count, dtype=np.float64) * WORLD_FRAME_PERIOD_MS / 1000.0
    return np.interp(
        frame_times,
        sample_times,
        sample_f0,
        left=float(sample_f0[0]),
        right=float(sample_f0[-1]),
    )


def _target_f0_curve_for_notes(
    notes: list[Note],
    expressions,
    group_onset: float,
    sample_rate: int,
    n_samples: int,
    target_frame_count: int,
) -> np.ndarray:
    sample_f0 = np.full(n_samples, np.nan, dtype=np.float64)
    group_start_sample = max(0, int(round(group_onset * sample_rate)))
    for note, expression in zip(notes, expressions):
        note_start_sample, note_end_sample = _note_sample_bounds(note, sample_rate)
        note_start = max(0, note_start_sample - group_start_sample)
        note_end = min(n_samples, note_end_sample - group_start_sample)
        if note_end <= note_start:
            continue
        note_duration_s = (note_end - note_start) / float(sample_rate)
        cents = build_cents_curve(note_duration_s, sample_rate, expression)
        note_f0 = midi_to_hz_with_cents(note.pitch, cents).astype(np.float64)
        if note_f0.size != note_end - note_start:
            old_x = np.linspace(0.0, 1.0, note_f0.size, dtype=np.float64)
            new_x = np.linspace(0.0, 1.0, note_end - note_start, dtype=np.float64)
            note_f0 = np.interp(new_x, old_x, note_f0)
        sample_f0[note_start:note_end] = note_f0

    known = np.isfinite(sample_f0)
    if not np.any(known):
        sample_f0.fill(midi_to_hz_with_cents(notes[0].pitch, np.array([0.0]))[0])
    elif not np.all(known):
        sample_positions = np.arange(n_samples, dtype=np.float64)
        sample_f0 = np.interp(sample_positions, sample_positions[known], sample_f0[known])

    sample_times = np.arange(n_samples, dtype=np.float64) / float(sample_rate)
    frame_times = np.arange(target_frame_count, dtype=np.float64) * WORLD_FRAME_PERIOD_MS / 1000.0
    return np.interp(
        frame_times,
        sample_times,
        sample_f0,
        left=float(sample_f0[0]),
        right=float(sample_f0[-1]),
    )


def _resize_feature_matrix(matrix: np.ndarray, target_rows: int) -> np.ndarray:
    if matrix.shape[0] == target_rows:
        return matrix.astype(np.float64)
    if matrix.shape[0] <= 1:
        return np.repeat(matrix.astype(np.float64), target_rows, axis=0)

    old_x = np.linspace(0.0, 1.0, matrix.shape[0], dtype=np.float64)
    new_x = np.linspace(0.0, 1.0, target_rows, dtype=np.float64)
    resized = np.empty((target_rows, matrix.shape[1]), dtype=np.float64)
    for bin_index in range(matrix.shape[1]):
        resized[:, bin_index] = np.interp(new_x, old_x, matrix[:, bin_index])
    return resized


def _resize_voiced_mask(mask: np.ndarray, target_rows: int) -> np.ndarray:
    default_mask = _default_voiced_mask(target_rows)
    if mask.size == 0:
        return default_mask
    old_x = np.linspace(0.0, 1.0, mask.size, dtype=np.float64)
    new_x = np.linspace(0.0, 1.0, target_rows, dtype=np.float64)
    resized = np.interp(new_x, old_x, mask.astype(np.float64)) >= 0.35
    if np.mean(resized) < 0.12:
        return default_mask
    return resized | default_mask


def _default_voiced_mask(target_rows: int) -> np.ndarray:
    mask = np.zeros(target_rows, dtype=bool)
    start = int(round(target_rows * DEFAULT_VOICED_START_FRACTION))
    end = max(start + 1, int(round(target_rows * DEFAULT_VOICED_END_FRACTION)))
    mask[start:end] = True
    return mask


def _prepare_unit_source(unit_audio: np.ndarray, is_continuation: bool) -> np.ndarray:
    source = _trim_to_active_region(np.asarray(unit_audio, dtype=np.float32))
    if source.size == 0:
        return np.zeros(1, dtype=np.float32)
    if not is_continuation:
        return source
    start = min(source.size - 1, max(0, int(round(source.size * 0.35))))
    return source[start:]


def _prepare_group_sources(
    unit_audio: np.ndarray,
    first_note_samples: int,
    sample_rate: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Return one onset source and one vowel-only source for a group."""

    active = _trim_to_active_region(unit_audio)
    if active.size == 0:
        empty = np.zeros(1, dtype=np.float32)
        return empty, empty

    return _split_onset_and_vowel_core(active, first_note_samples, sample_rate)


def _trim_to_active_region(audio: np.ndarray) -> np.ndarray:
    """Remove leading/trailing silence before consonant-vowel splitting."""

    source = np.nan_to_num(np.asarray(audio, dtype=np.float32))
    if source.size == 0:
        return source

    peak = float(np.max(np.abs(source)))
    if peak <= 1e-8:
        return source

    threshold = peak * 0.015
    active = np.flatnonzero(np.abs(source) >= threshold)
    if active.size == 0:
        return source

    pad = min(int(round(source.size * 0.02)), max(1, source.size // 20))
    start = max(0, int(active[0]) - pad)
    end = min(source.size, int(active[-1]) + pad + 1)
    return source[start:end].astype(np.float32)


def _split_onset_and_vowel_core(
    active: np.ndarray,
    first_note_samples: int,
    sample_rate: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Split a spoken unit into first-note onset and reusable vowel core.

    This is intentionally conservative: WORLD can change F0, but it does not
    know phoneme boundaries. The renderer must keep consonant-like material at
    the group start and use only the stable vowel center for continuation notes.
    """

    source = np.asarray(active, dtype=np.float32)
    if source.size == 0:
        return source, source

    min_onset = int(round(sample_rate * 0.070))
    max_onset = int(round(sample_rate * 0.160))
    first_note_cap = max(min_onset, int(round(first_note_samples * 0.55)))
    onset_end = min(
        source.size,
        max(min_onset, int(round(source.size * 0.28))),
        max_onset,
        first_note_cap,
    )
    onset_end = max(1, min(onset_end, source.size))

    core_start = min(
        source.size - 1,
        max(
            onset_end + int(round(sample_rate * 0.030)),
            int(round(source.size * 0.58)),
            int(round(sample_rate * 0.120)),
        ),
    )
    core_end = min(
        source.size,
        max(core_start + int(round(sample_rate * 0.060)), int(round(source.size * 0.92))),
    )
    vowel_core = source[core_start:core_end]
    if vowel_core.size < int(round(sample_rate * 0.030)):
        fallback_start = min(source.size - 1, max(onset_end, int(round(source.size * 0.62))))
        vowel_core = source[fallback_start:]
    if vowel_core.size == 0:
        vowel_core = source[onset_end:] if onset_end < source.size else source
    if vowel_core.size == 0:
        vowel_core = source

    vowel_core = _extract_stable_vowel_core(vowel_core, sample_rate)
    return source[:onset_end].astype(np.float32), vowel_core.astype(np.float32)


def _extract_stable_vowel_core(vowel_core: np.ndarray, sample_rate: int) -> np.ndarray:
    """Keep only a smooth vowel sustain loop, not the full moving TTS tail."""

    source = np.asarray(vowel_core, dtype=np.float32)
    if source.size == 0:
        return source

    min_samples = max(1, int(round(STABLE_VOWEL_MIN_S * sample_rate)))
    max_samples = max(min_samples, int(round(STABLE_VOWEL_MAX_S * sample_rate)))
    window_size = min(source.size, max_samples)
    if source.size <= min_samples:
        return _normalize_loop_segment(source)

    search_start = min(source.size - 1, int(round(source.size * 0.15)))
    search_end = max(search_start + 1, int(round(source.size * 0.92)))
    search_region = source[search_start:search_end]
    if search_region.size < window_size:
        return _normalize_loop_segment(source)

    hop = max(1, int(round(sample_rate * 0.010)))
    best_score = -np.inf
    best_start = 0
    for start in range(0, search_region.size - window_size + 1, hop):
        window = search_region[start : start + window_size]
        rms = float(np.sqrt(np.mean(np.square(window))) + 1e-8)
        roughness = float(np.mean(np.abs(np.diff(window)))) / rms
        edge_jump = float(abs(window[0] - window[-1])) / rms
        score = rms - 0.08 * roughness - 0.05 * edge_jump
        if score > best_score:
            best_score = score
            best_start = start

    stable = search_region[best_start : best_start + window_size]
    if stable.size < min_samples:
        stable = source[-min(source.size, min_samples) :]
    return _normalize_loop_segment(stable.astype(np.float32))


def _normalize_loop_segment(segment: np.ndarray) -> np.ndarray:
    out = np.asarray(segment, dtype=np.float32).copy()
    if out.size == 0:
        return out
    out -= float(np.mean(out))
    peak = float(np.max(np.abs(out)))
    if peak > 1e-8:
        out = out / peak * 0.80
    return out


def _build_group_start_source(
    onset: np.ndarray,
    vowel_core: np.ndarray,
    n_samples: int,
) -> np.ndarray:
    onset = np.asarray(onset, dtype=np.float32)
    vowel_core = np.asarray(vowel_core, dtype=np.float32)
    if n_samples <= 0:
        return np.zeros(0, dtype=np.float32)
    if onset.size >= n_samples:
        return onset[:n_samples].astype(np.float32)
    vowel_tail = _loop_segment(vowel_core, n_samples - onset.size)
    return np.concatenate([onset, vowel_tail])[:n_samples].astype(np.float32)


def _build_group_continuation_source(
    vowel_core: np.ndarray,
    n_samples: int,
    sample_rate: int,
) -> np.ndarray:
    vowel_core = np.asarray(vowel_core, dtype=np.float32)
    minimum = min(
        max(1, n_samples),
        max(int(round(sample_rate * 0.120)), vowel_core.size),
    )
    if vowel_core.size >= minimum:
        return vowel_core.astype(np.float32)
    return _loop_segment(vowel_core, minimum)


def _segment_envelope(
    n_samples: int,
    sample_rate: int,
    attack_s: float,
    release_s: float,
) -> np.ndarray:
    env = np.ones(max(0, n_samples), dtype=np.float32)
    if n_samples <= 0:
        return env
    attack_n = min(n_samples, max(0, int(round(attack_s * sample_rate))))
    if attack_n > 1:
        env[:attack_n] *= np.linspace(0.0, 1.0, attack_n, endpoint=True, dtype=np.float32)
    release_n = min(n_samples, max(0, int(round(release_s * sample_rate))))
    if release_n > 1:
        env[-release_n:] *= np.linspace(1.0, 0.0, release_n, endpoint=True, dtype=np.float32)
    return env


def _mix_segment_with_crossfade(
    target: np.ndarray,
    segment: np.ndarray,
    start: int,
    cursor: int,
    crossfade_n: int,
) -> int:
    if segment.size == 0 or start >= target.size:
        return cursor
    start = max(0, int(start))
    end = min(target.size, start + segment.size)
    segment = segment[: end - start]
    if segment.size == 0:
        return cursor

    overlap_n = min(max(0, cursor - start), crossfade_n, segment.size)
    if overlap_n > 1:
        phase = np.linspace(0.0, np.pi / 2.0, overlap_n, endpoint=True, dtype=np.float32)
        fade_out = np.cos(phase)
        fade_in = np.sin(phase)
        target[start : start + overlap_n] = (
            target[start : start + overlap_n] * fade_out
            + segment[:overlap_n] * fade_in
        )
        target[start + overlap_n : end] += segment[overlap_n:]
    else:
        target[start:end] += segment
    return max(cursor, end)


def _loop_segment(segment: np.ndarray, n_samples: int) -> np.ndarray:
    if n_samples <= 0:
        return np.zeros(0, dtype=np.float32)
    segment = np.asarray(segment, dtype=np.float32)
    if segment.size == 0:
        return np.zeros(n_samples, dtype=np.float32)
    if segment.size < 16:
        repeat_count = int(np.ceil(n_samples / max(1, segment.size)))
        return np.tile(segment, repeat_count + 1)[:n_samples].astype(np.float32)

    out = np.zeros(n_samples, dtype=np.float32)
    cursor = min(segment.size, n_samples)
    out[:cursor] = segment[:cursor]
    overlap = min(160, max(8, segment.size // 8))
    while cursor < n_samples:
        overlap_n = min(overlap, cursor, segment.size, n_samples - max(0, cursor - overlap))
        start = max(0, cursor - overlap_n)
        fade_in = np.linspace(0.0, 1.0, overlap_n, endpoint=True, dtype=np.float32)
        out[start:cursor] = (
            out[start:cursor] * (1.0 - fade_in)
            + segment[:overlap_n] * fade_in
        )

        write_start = cursor
        write_count = min(segment.size - overlap_n, n_samples - write_start)
        if write_count <= 0:
            break
        out[write_start : write_start + write_count] = segment[
            overlap_n : overlap_n + write_count
        ]
        cursor = write_start + write_count
    return out.astype(np.float32)


def _fit_source_to_length(source: np.ndarray, n_samples: int) -> np.ndarray:
    """Crop or loop a short source unit to exactly the target note length."""

    if n_samples <= 0:
        return np.zeros(0, dtype=np.float32)
    source = np.asarray(source, dtype=np.float32)
    if source.size == 0:
        return np.zeros(n_samples, dtype=np.float32)
    if source.size >= n_samples:
        return source[:n_samples].astype(np.float32)

    tail_start = min(source.size - 1, max(0, int(round(source.size * 0.45))))
    tail = source[tail_start:]
    if tail.size == 0:
        tail = source
    repeat_count = int(np.ceil((n_samples - source.size) / max(1, tail.size)))
    repeated = np.tile(tail, repeat_count + 1)
    out = np.concatenate([source, repeated])[:n_samples]
    return out.astype(np.float32)


def _shape_texture(
    texture: np.ndarray,
    style: str,
    age: str,
    sample_rate: int,
    rng: np.random.Generator,
) -> np.ndarray:
    out = texture.astype(np.float32)
    if out.size == 0:
        return out

    if style == "bright" or age in ("child", "teen"):
        out = _high_shelf(out, sample_rate, gain=1.10)
    elif style == "dark" or age == "old":
        out = _lowpass(out, sample_rate, cutoff=5200.0)

    if style == "breathy":
        noise = rng.normal(0.0, 1.0, out.size).astype(np.float32)
        noise = _bandpass(noise, sample_rate, 1800.0, 7200.0)
        out = out + 0.030 * noise

    peak = float(np.max(np.abs(out)))
    if peak > 1e-8:
        out = out / peak
    return out.astype(np.float32)


def _attack_s(
    duration_s: float,
    is_continuation: bool,
    style: str,
    rng: np.random.Generator,
) -> float:
    if is_continuation:
        return min(float(rng.uniform(0.002, 0.007)), duration_s * 0.08)
    base = float(rng.uniform(0.006, 0.024))
    if style == "soft_attack":
        base += float(rng.uniform(0.010, 0.024))
    return min(base, duration_s * 0.20)


def _release_s(duration_s: float, grouped: bool) -> float:
    if grouped:
        return float(
            min(
                GROUP_RELEASE_MAX_S,
                max(GROUP_RELEASE_MIN_S, duration_s * GROUP_RELEASE_DURATION_FRACTION),
            )
        )
    return float(
        min(
            NOTE_RELEASE_MAX_S,
            max(NOTE_RELEASE_MIN_S, duration_s * NOTE_RELEASE_DURATION_FRACTION),
        )
    )


def _high_shelf(audio: np.ndarray, sample_rate: int, gain: float) -> np.ndarray:
    bright = _bandpass(audio, sample_rate, 1800.0, sample_rate * 0.45)
    return (audio + (gain - 1.0) * bright).astype(np.float32)


def _lowpass(audio: np.ndarray, sample_rate: int, cutoff: float) -> np.ndarray:
    sos = signal.butter(2, cutoff, btype="lowpass", fs=sample_rate, output="sos")
    return signal.sosfilt(sos, audio).astype(np.float32)


def _bandpass(audio: np.ndarray, sample_rate: int, low_hz: float, high_hz: float) -> np.ndarray:
    nyquist = sample_rate * 0.5
    low = max(40.0, min(low_hz, nyquist * 0.90))
    high = max(low + 20.0, min(high_hz, nyquist * 0.96))
    sos = signal.butter(2, (low, high), btype="bandpass", fs=sample_rate, output="sos")
    return signal.sosfilt(sos, audio).astype(np.float32)


def _safe_normalize(audio: np.ndarray) -> np.ndarray:
    audio = np.nan_to_num(audio.astype(np.float32))
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if peak > 1e-8:
        audio = audio / peak * 0.90
    return audio.astype(np.float32)
