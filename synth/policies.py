"""Generation policy selection.

A policy is fixed for one generated WAV. Note-level and phrase-level details
are sampled from this policy during rendering.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .voice_presets import AGES, GENDERS, STYLES


SYLLABLE_POLICIES = (
    "vowel_heavy",
    "soft_syllable_mix",
    "pop_syllable_mix",
    "hard_consonant_sparse",
    "breath_phrase_mix",
)

PITCH_POLICIES = ("intune", "mild_detune", "expressive_detune")
VIBRATO_POLICIES = ("none", "light", "normal", "expressive")
PITCH_TRANSITION_POLICIES = ("none", "light_scoop", "pop_scoop", "expressive_slide")


@dataclass(frozen=True)
class GenerationPolicy:
    """Fixed generation settings for a single output sample."""

    gender: str
    age: str
    style: str
    syllable_policy: str
    pitch_policy: str
    vibrato_policy: str
    pitch_transition_policy: str
    seed: int
    version_index: int

    def to_dict(self) -> dict[str, str | int]:
        return asdict(self)


def make_policy_for_version(base_seed: int, score_stem: str, version_index: int) -> GenerationPolicy:
    """Create a reproducible but varied policy for a score/version pair."""

    seed = _stable_seed(base_seed, score_stem, version_index)
    rng = np.random.default_rng(seed)
    gender = str(rng.choice(GENDERS))
    age = str(rng.choice(AGES))
    style = str(rng.choice(STYLES))
    syllable_policy = str(rng.choice(SYLLABLE_POLICIES))

    pitch_policy = str(rng.choice(PITCH_POLICIES, p=[0.58, 0.34, 0.08]))
    vibrato_policy = str(rng.choice(VIBRATO_POLICIES, p=[0.25, 0.35, 0.30, 0.10]))
    transition_policy = str(rng.choice(PITCH_TRANSITION_POLICIES, p=[0.35, 0.35, 0.23, 0.07]))

    return GenerationPolicy(
        gender=gender,
        age=age,
        style=style,
        syllable_policy=syllable_policy,
        pitch_policy=pitch_policy,
        vibrato_policy=vibrato_policy,
        pitch_transition_policy=transition_policy,
        seed=seed,
        version_index=version_index,
    )


def make_explicit_policy(
    seed: int,
    version_index: int,
    gender: str,
    age: str,
    style: str,
    syllable_policy: str,
    pitch_policy: str,
    vibrato_policy: str,
    pitch_transition_policy: str,
) -> GenerationPolicy:
    """Build a policy from CLI-provided values."""

    return GenerationPolicy(
        gender=gender,
        age=age,
        style=style,
        syllable_policy=syllable_policy,
        pitch_policy=pitch_policy,
        vibrato_policy=vibrato_policy,
        pitch_transition_policy=pitch_transition_policy,
        seed=seed,
        version_index=version_index,
    )


def _stable_seed(base_seed: int, score_stem: str, version_index: int) -> int:
    """Return a stable 32-bit seed without relying on Python hash randomization."""

    value = int(base_seed) & 0xFFFFFFFF
    for char in f"{score_stem}:{version_index}":
        value = (value * 1664525 + ord(char) + 1013904223) & 0xFFFFFFFF
    return value

