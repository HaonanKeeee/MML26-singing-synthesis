"""Voice preset definitions.

These presets are synthetic timbre controls, not real demographic models. They
give the generator broad spectral variety while keeping labels unchanged.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np


@dataclass(frozen=True)
class VoicePreset:
    gender: str
    age: str
    style: str
    preset_name: str
    formant_scale: float
    brightness: float
    breathiness: float
    harmonic_tilt: float
    amplitude: float
    pitch_stability: float

    def to_dict(self) -> dict[str, float | str]:
        return asdict(self)


GENDERS = ("male", "female", "neutral")
AGES = ("child", "teen", "young", "middle", "old")
STYLES = (
    "clean",
    "breathy",
    "bright",
    "dark",
    "nasal",
    "soft_attack",
    "vibrato_light",
    "vibrato_expressive",
)


AGE_FORMANT_SCALE = {
    "child": 1.22,
    "teen": 1.10,
    "young": 1.00,
    "middle": 0.96,
    "old": 0.92,
}

GENDER_FORMANT_SCALE = {
    "male": 0.88,
    "female": 1.10,
    "neutral": 1.00,
}


def make_voice_preset(
    gender: str,
    age: str,
    style: str,
    rng: np.random.Generator,
) -> VoicePreset:
    """Create a deterministic-ish voice preset with small random jitter."""

    if gender not in GENDERS:
        raise ValueError(f"Unsupported gender preset: {gender}")
    if age not in AGES:
        raise ValueError(f"Unsupported age preset: {age}")
    if style not in STYLES:
        raise ValueError(f"Unsupported style preset: {style}")

    formant_scale = GENDER_FORMANT_SCALE[gender] * AGE_FORMANT_SCALE[age]
    formant_scale *= float(rng.normal(1.0, 0.025))

    brightness = {
        "child": 1.12,
        "teen": 1.08,
        "young": 1.00,
        "middle": 0.94,
        "old": 0.88,
    }[age]
    breathiness = {
        "child": 0.03,
        "teen": 0.025,
        "young": 0.02,
        "middle": 0.025,
        "old": 0.045,
    }[age]
    harmonic_tilt = {
        "male": 1.30,
        "female": 1.05,
        "neutral": 1.18,
    }[gender]
    amplitude = 0.55
    pitch_stability = {
        "child": 0.78,
        "teen": 0.88,
        "young": 1.00,
        "middle": 0.95,
        "old": 0.82,
    }[age]

    if style == "breathy":
        breathiness += 0.06
        brightness *= 0.94
    elif style == "bright":
        brightness *= 1.18
        harmonic_tilt *= 0.90
    elif style == "dark":
        brightness *= 0.82
        harmonic_tilt *= 1.22
    elif style == "nasal":
        brightness *= 1.08
    elif style == "soft_attack":
        amplitude *= 0.92
    elif style == "vibrato_light":
        pitch_stability *= 0.98
    elif style == "vibrato_expressive":
        pitch_stability *= 0.90

    return VoicePreset(
        gender=gender,
        age=age,
        style=style,
        preset_name=f"{gender}_{age}_{style}",
        formant_scale=float(formant_scale),
        brightness=float(brightness),
        breathiness=float(breathiness),
        harmonic_tilt=float(harmonic_tilt),
        amplitude=float(amplitude),
        pitch_stability=float(pitch_stability),
    )

