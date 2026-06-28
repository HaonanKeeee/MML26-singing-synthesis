"""Render note labels into synthetic vocal-like audio."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

from .envelopes import note_envelope
from .formants import apply_vowel_formants
from .ornaments import build_cents_curve, plan_note_expressions
from .pitch import midi_to_hz_with_cents
from .policies import GenerationPolicy
from .score_io import Note, split_phrases, write_score_tsv
from .syllable_groups import (
    SyllableGroupMark,
    continuation_indices,
    plan_syllable_groups,
)
from .syllables import Syllable, choose_syllables_for_notes
from .voice_presets import VoicePreset, make_voice_preset


DEFAULT_SAMPLE_RATE = 16_000


def render_score_to_sample(
    notes: list[Note],
    output_dir: str | Path,
    policy: GenerationPolicy,
    source_score: str,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
) -> dict:
    """Render one score into one `audio.wav` + `score.tsv` sample directory."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(policy.seed)
    voice = make_voice_preset(policy.gender, policy.age, policy.style, rng)
    phrases = split_phrases(notes)
    group_marks, syllable_group_summary = plan_syllable_groups(notes, rng)
    syllables = choose_syllables_for_notes(
        len(notes),
        phrases,
        policy.syllable_policy,
        rng,
        group_marks=group_marks,
    )
    expressions, expression_summary = plan_note_expressions(
        notes=notes,
        pitch_policy=policy.pitch_policy,
        vibrato_policy=policy.vibrato_policy,
        transition_policy=policy.pitch_transition_policy,
        voice=voice,
        rng=rng,
        protected_indices=continuation_indices(group_marks),
    )

    total_duration = max(note.offset for note in notes) + 0.12
    audio = np.zeros(int(np.ceil(total_duration * sample_rate)), dtype=np.float32)
    metadata_notes = []

    _add_phrase_breaths(audio, notes, phrases, voice, policy, sample_rate, rng)

    for index, note in enumerate(notes):
        syllable = syllables[index]
        group_mark = group_marks[index]
        expression = expressions[index]
        note_audio = _render_note(
            note,
            syllable,
            expression,
            group_mark,
            voice,
            sample_rate,
            rng,
        )
        start = int(round(note.onset * sample_rate))
        end = min(len(audio), start + len(note_audio))
        if end > start:
            audio[start:end] += note_audio[: end - start]

        metadata_notes.append(
            {
                "index": index,
                "onset": note.onset,
                "offset": note.offset,
                "pitch": note.pitch,
                "syllable": syllable.text,
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
        "policy": policy.to_dict(),
        "voice": voice.to_dict(),
        "syllable_group_summary": syllable_group_summary,
        "expression_summary": expression_summary,
        "notes": metadata_notes,
        "todos": [
            "TODO: Replace the simple source-filter synthesizer with a stronger vocal model if allowed.",
            "TODO: Add optional accompaniment only if mentors confirm it is safe for labels.",
        ],
    }
    metadata_path.write_text(json.dumps(metadata, indent=2))
    return metadata


def _render_note(
    note: Note,
    syllable: Syllable,
    expression,
    group_mark: SyllableGroupMark,
    voice: VoicePreset,
    sample_rate: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Render a single note as a harmonic vowel plus short consonant onset."""

    n_samples = max(1, int(round(note.duration * sample_rate)))
    cents = build_cents_curve(note.duration, sample_rate, expression)
    frequency = midi_to_hz_with_cents(note.pitch, cents)
    phase = 2.0 * np.pi * np.cumsum(frequency) / sample_rate

    harmonic_source = _harmonic_source(phase, voice, rng)
    source = apply_vowel_formants(
        harmonic_source,
        sample_rate=sample_rate,
        vowel=syllable.vowel,
        formant_scale=voice.formant_scale,
        brightness=voice.brightness,
    )

    if (
        not group_mark.is_continuation
        and syllable.glide_to is not None
        and n_samples > int(0.12 * sample_rate)
    ):
        # TODO: Implement true time-varying formants. For now, blend a second
        # vowel color across the note to approximate English-like diphthongs.
        second = apply_vowel_formants(
            harmonic_source,
            sample_rate=sample_rate,
            vowel=syllable.glide_to,
            formant_scale=voice.formant_scale,
            brightness=voice.brightness,
        )
        blend = _vowel_glide_curve(n_samples)
        source = (1.0 - blend) * source + blend * second

    source = _add_breathiness(source, voice.breathiness, sample_rate, rng)
    if not group_mark.is_continuation:
        source = _add_consonant_onset(source, syllable, sample_rate, rng)

    attack = _sample_attack_s(note.duration, voice.style, syllable, group_mark, rng)
    release = float(min(0.050, max(0.012, note.duration * 0.12)))
    env = note_envelope(n_samples, sample_rate, attack, release)
    loudness = float(rng.uniform(0.82, 1.08)) * voice.amplitude
    return (source * env * loudness).astype(np.float32)


def _harmonic_source(phase: np.ndarray, voice: VoicePreset, rng: np.random.Generator) -> np.ndarray:
    """Create a band-limited-ish harmonic source with mild shimmer."""

    source = np.zeros_like(phase, dtype=np.float64)
    harmonic_count = 10
    for harmonic in range(1, harmonic_count + 1):
        amplitude = 1.0 / (harmonic ** voice.harmonic_tilt)
        amplitude *= voice.brightness ** (0.25 if harmonic > 2 else 0.1)
        source += amplitude * np.sin(harmonic * phase + rng.uniform(0.0, 2.0 * np.pi))

    peak = np.max(np.abs(source))
    if peak > 1e-8:
        source /= peak
    return source.astype(np.float32)


def _vowel_glide_curve(n_samples: int) -> np.ndarray:
    """Create a smooth vowel morph curve for diphthong-like syllables."""

    if n_samples <= 1:
        return np.zeros(max(0, n_samples), dtype=np.float32)
    x = np.linspace(0.0, 1.0, n_samples, dtype=np.float32)
    # Most diphthong color change happens after the onset and before the final
    # release, so hold the starting vowel briefly and then move smoothly.
    x = np.clip((x - 0.18) / 0.62, 0.0, 1.0)
    return (x * x * (3.0 - 2.0 * x)).astype(np.float32)


def _add_breathiness(
    source: np.ndarray,
    breathiness: float,
    sample_rate: int,
    rng: np.random.Generator,
) -> np.ndarray:
    if breathiness <= 0.0:
        return source
    noise = rng.normal(0.0, 1.0, len(source)).astype(np.float32)
    noise = _shape_noise(noise, sample_rate, "h")
    source_rms = _rms(source)
    noise_rms = _rms(noise)
    if noise_rms > 1e-8:
        noise = noise / noise_rms * max(source_rms, 1e-4)
    return (source + breathiness * 0.55 * noise).astype(np.float32)


def _add_consonant_onset(
    source: np.ndarray,
    syllable: Syllable,
    sample_rate: int,
    rng: np.random.Generator,
) -> np.ndarray:
    if syllable.consonant is None or len(source) == 0:
        return source

    duration_s, amount = _consonant_onset_params(syllable, rng)

    n = min(len(source), int(round(duration_s * sample_rate)))
    if n <= 1:
        return source

    noise = rng.normal(0.0, 1.0, n).astype(np.float32)
    noise = _shape_noise(noise, sample_rate, syllable.consonant)
    noise_rms = _rms(noise)
    if noise_rms > 1e-8:
        noise = noise / noise_rms * max(_rms(source[:n]), 1e-4)

    burst_env = np.linspace(1.0, 0.0, n, dtype=np.float32) ** 1.7
    out = source.copy()
    out[:n] = (1.0 - amount * burst_env) * out[:n] + amount * burst_env * noise
    return out


def _consonant_onset_params(
    syllable: Syllable,
    rng: np.random.Generator,
) -> tuple[float, float]:
    """Return onset duration and mix amount for the consonant class."""

    consonant = syllable.consonant or ""
    if consonant in ("p", "t", "k"):
        return float(rng.uniform(0.030, 0.060)), 0.70
    if consonant in ("b", "d", "g"):
        return float(rng.uniform(0.024, 0.050)), 0.55
    if consonant in ("s", "sh", "f", "th"):
        return float(rng.uniform(0.050, 0.090)), 0.62
    if consonant == "h":
        return float(rng.uniform(0.045, 0.080)), 0.42
    if consonant in ("m", "n"):
        return float(rng.uniform(0.045, 0.085)), 0.36
    if consonant in ("w", "y", "l", "r"):
        return float(rng.uniform(0.030, 0.060)), 0.28
    if syllable.consonant_type == "hard":
        return float(rng.uniform(0.026, 0.055)), 0.58
    if syllable.consonant_type == "fricative":
        return float(rng.uniform(0.040, 0.080)), 0.50
    return float(rng.uniform(0.018, 0.045)), 0.24


def _shape_noise(noise: np.ndarray, sample_rate: int, consonant: str | None) -> np.ndarray:
    """Color onset/breath noise so consonants have distinct acoustic cues."""

    band = {
        "p": (500.0, 1800.0),
        "b": (300.0, 1600.0),
        "t": (3000.0, 7200.0),
        "d": (1800.0, 5200.0),
        "k": (1200.0, 4200.0),
        "g": (800.0, 3400.0),
        "s": (4200.0, 7600.0),
        "sh": (2200.0, 5200.0),
        "f": (2500.0, 7400.0),
        "th": (3300.0, 7600.0),
        "h": (1600.0, 6800.0),
        "m": (180.0, 1100.0),
        "n": (350.0, 1800.0),
        "l": (500.0, 2600.0),
        "r": (450.0, 2200.0),
        "w": (180.0, 1400.0),
        "y": (900.0, 3400.0),
    }.get(consonant or "", (900.0, 5200.0))
    return _bandpass_noise(noise, sample_rate, *band)


def _bandpass_noise(noise: np.ndarray, sample_rate: int, low_hz: float, high_hz: float) -> np.ndarray:
    nyquist = sample_rate * 0.5
    low = max(40.0, min(low_hz, nyquist * 0.90))
    high = max(low + 20.0, min(high_hz, nyquist * 0.96))
    if high >= nyquist:
        high = nyquist * 0.96
    if low >= high:
        return noise.astype(np.float32)
    sos = signal.butter(2, (low, high), btype="bandpass", fs=sample_rate, output="sos")
    return signal.sosfilt(sos, noise).astype(np.float32)


def _rms(audio: np.ndarray) -> float:
    if audio.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(audio.astype(np.float64)))))


def _sample_attack_s(
    duration_s: float,
    style: str,
    syllable: Syllable,
    group_mark: SyllableGroupMark,
    rng: np.random.Generator,
) -> float:
    if group_mark.is_continuation:
        return min(float(rng.uniform(0.002, 0.006)), duration_s * 0.08)

    base = float(rng.uniform(0.006, 0.025))
    if style == "soft_attack":
        base += float(rng.uniform(0.010, 0.020))
    if syllable.consonant_type in ("hard", "fricative"):
        base = min(base, 0.014)
    return min(base, duration_s * 0.20)


def _add_phrase_breaths(
    audio: np.ndarray,
    notes: list[Note],
    phrases: list[list[int]],
    voice: VoicePreset,
    policy: GenerationPolicy,
    sample_rate: int,
    rng: np.random.Generator,
) -> None:
    """Add short pre-phrase breaths without shifting note onsets."""

    if policy.syllable_policy != "breath_phrase_mix" and voice.breathiness < 0.07:
        return

    for phrase in phrases:
        first = notes[phrase[0]]
        if first.onset < 0.12 or rng.random() > 0.45:
            continue
        breath_duration = float(rng.uniform(0.060, 0.160))
        breath_end = max(0.0, first.onset - float(rng.uniform(0.015, 0.045)))
        breath_start = max(0.0, breath_end - breath_duration)
        start = int(round(breath_start * sample_rate))
        end = int(round(breath_end * sample_rate))
        if end <= start:
            continue
        n = end - start
        noise = rng.normal(0.0, 1.0, n).astype(np.float32)
        env = np.sin(np.linspace(0.0, np.pi, n, dtype=np.float32))
        audio[start:end] += noise * env * float(rng.uniform(0.006, 0.018))


def _safe_normalize(audio: np.ndarray) -> np.ndarray:
    audio = np.nan_to_num(audio.astype(np.float32))
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if peak > 1e-8:
        audio = audio / peak * 0.90
    return audio.astype(np.float32)
