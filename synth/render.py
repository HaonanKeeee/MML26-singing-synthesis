"""Render note labels into synthetic vocal-like audio."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import soundfile as sf

from .envelopes import note_envelope
from .formants import apply_vowel_formants
from .ornaments import build_cents_curve, sample_note_expression
from .pitch import midi_to_hz_with_cents
from .policies import GenerationPolicy
from .score_io import Note, split_phrases, write_score_tsv
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
    syllables = choose_syllables_for_notes(len(notes), phrases, policy.syllable_policy, rng)

    total_duration = max(note.offset for note in notes) + 0.12
    audio = np.zeros(int(np.ceil(total_duration * sample_rate)), dtype=np.float32)
    metadata_notes = []

    _add_phrase_breaths(audio, notes, phrases, voice, policy, sample_rate, rng)

    previous_note: Note | None = None
    for index, note in enumerate(notes):
        syllable = syllables[index]
        expression = sample_note_expression(
            note=note,
            previous_note=previous_note,
            pitch_policy=policy.pitch_policy,
            vibrato_policy=policy.vibrato_policy,
            transition_policy=policy.pitch_transition_policy,
            voice=voice,
            rng=rng,
        )
        note_audio = _render_note(note, syllable, expression, voice, sample_rate, rng)
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
                **expression.to_dict(),
            }
        )
        previous_note = note

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
    voice: VoicePreset,
    sample_rate: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Render a single note as a harmonic vowel plus short consonant onset."""

    n_samples = max(1, int(round(note.duration * sample_rate)))
    cents = build_cents_curve(note.duration, sample_rate, expression)
    frequency = midi_to_hz_with_cents(note.pitch, cents)
    phase = 2.0 * np.pi * np.cumsum(frequency) / sample_rate

    source = _harmonic_source(phase, voice, rng)
    source = apply_vowel_formants(
        source,
        sample_rate=sample_rate,
        vowel=syllable.vowel,
        formant_scale=voice.formant_scale,
        brightness=voice.brightness,
    )

    if syllable.glide_to is not None and n_samples > int(0.12 * sample_rate):
        # TODO: Implement true time-varying formants. For now, blend a second
        # vowel color across the note to approximate English-like diphthongs.
        second = apply_vowel_formants(
            source,
            sample_rate=sample_rate,
            vowel=syllable.glide_to,
            formant_scale=voice.formant_scale,
            brightness=voice.brightness,
        )
        blend = np.linspace(0.0, 1.0, n_samples, dtype=np.float32)
        source = (1.0 - blend) * source + blend * second

    source = _add_breathiness(source, voice.breathiness, rng)
    source = _add_consonant_onset(source, syllable, sample_rate, rng)

    attack = _sample_attack_s(note.duration, voice.style, syllable, rng)
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


def _add_breathiness(source: np.ndarray, breathiness: float, rng: np.random.Generator) -> np.ndarray:
    if breathiness <= 0.0:
        return source
    noise = rng.normal(0.0, 1.0, len(source)).astype(np.float32)
    return (source + breathiness * noise).astype(np.float32)


def _add_consonant_onset(
    source: np.ndarray,
    syllable: Syllable,
    sample_rate: int,
    rng: np.random.Generator,
) -> np.ndarray:
    if syllable.consonant is None or len(source) == 0:
        return source

    if syllable.consonant_type == "hard":
        duration_s = float(rng.uniform(0.020, 0.055))
        amount = 0.45
    elif syllable.consonant_type == "fricative":
        duration_s = float(rng.uniform(0.025, 0.065))
        amount = 0.35
    else:
        duration_s = float(rng.uniform(0.015, 0.040))
        amount = 0.22

    n = min(len(source), int(round(duration_s * sample_rate)))
    if n <= 1:
        return source

    noise = rng.normal(0.0, 1.0, n).astype(np.float32)
    burst_env = np.linspace(1.0, 0.0, n, dtype=np.float32)
    out = source.copy()
    out[:n] = (1.0 - amount * burst_env) * out[:n] + amount * burst_env * noise
    return out


def _sample_attack_s(
    duration_s: float,
    style: str,
    syllable: Syllable,
    rng: np.random.Generator,
) -> float:
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

