"""English-like syllable inventory and phrase-aware syllable assignment."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Syllable:
    """A parameterized syllable.

    `consonant` is a short onset gesture. `vowel` is the sustained pitch-bearing
    component. `glide_to` optionally morphs the vowel color over the note.
    """

    text: str
    vowel: str
    consonant: str | None = None
    consonant_type: str = "none"
    glide_to: str | None = None


CORE_VOWELS = {
    "ah": Syllable("ah", "ah"),
    "aa": Syllable("aa", "ah"),
    "ae": Syllable("ae", "ae"),
    "eh": Syllable("eh", "eh"),
    "ee": Syllable("ee", "ee"),
    "ih": Syllable("ih", "ih"),
    "oh": Syllable("oh", "oh"),
    "aw": Syllable("aw", "aw"),
    "oo": Syllable("oo", "oo"),
    "uh": Syllable("uh", "uh"),
    "er": Syllable("er", "er"),
}


def _cv_series(consonant: str, consonant_type: str) -> dict[str, Syllable]:
    """Build a small English-like consonant-vowel series."""

    vowel_map = {
        "a": "ah",
        "e": "eh",
        "i": "ee",
        "o": "oh",
        "u": "oo",
    }
    return {
        f"{consonant}{suffix}": Syllable(
            text=f"{consonant}{suffix}",
            vowel=vowel,
            consonant=consonant,
            consonant_type=consonant_type,
        )
        for suffix, vowel in vowel_map.items()
    }


SOFT_SYLLABLES: dict[str, Syllable] = {}
for _consonant in ("l", "m", "n", "y", "w", "r"):
    SOFT_SYLLABLES.update(_cv_series(_consonant, "soft"))

HARD_SYLLABLES: dict[str, Syllable] = {}
for _consonant in ("p", "t", "k", "b", "d", "g"):
    HARD_SYLLABLES.update(_cv_series(_consonant, "hard"))

FRICATIVE_SYLLABLES: dict[str, Syllable] = {}
for _consonant in ("h", "f", "s", "sh", "th"):
    FRICATIVE_SYLLABLES.update(_cv_series(_consonant, "fricative"))

POP_SYLLABLES = {
    "yeah": Syllable("yeah", "eh", consonant="y", consonant_type="soft", glide_to="ah"),
    "yea": Syllable("yea", "eh", consonant="y", consonant_type="soft", glide_to="ah"),
    "hey": Syllable("hey", "eh", consonant="h", consonant_type="fricative", glide_to="ee"),
    "ooh": Syllable("ooh", "oo"),
    "woo": Syllable("woo", "oo", consonant="w", consonant_type="soft"),
    "whoa": Syllable("whoa", "oo", consonant="h", consonant_type="fricative", glide_to="oh"),
    "nah": Syllable("nah", "ah", consonant="n", consonant_type="soft"),
    "lah": Syllable("lah", "ah", consonant="l", consonant_type="soft"),
    "doo": Syllable("doo", "oo", consonant="d", consonant_type="hard"),
    "du": Syllable("du", "oo", consonant="d", consonant_type="hard"),
    "mm": Syllable("mm", "uh", consonant="m", consonant_type="soft"),
    "hmm": Syllable("hmm", "uh", consonant="h", consonant_type="fricative"),
}

SYLLABLE_REGISTRY = {
    **CORE_VOWELS,
    **SOFT_SYLLABLES,
    **HARD_SYLLABLES,
    **FRICATIVE_SYLLABLES,
    **POP_SYLLABLES,
}


POLICY_WEIGHTS = {
    "vowel_heavy": (0.65, 0.25, 0.08, 0.02),
    "soft_syllable_mix": (0.45, 0.40, 0.10, 0.05),
    "pop_syllable_mix": (0.45, 0.25, 0.10, 0.20),
    "hard_consonant_sparse": (0.50, 0.25, 0.20, 0.05),
    "breath_phrase_mix": (0.55, 0.30, 0.05, 0.10),
}


def choose_syllables_for_notes(
    note_count: int,
    phrases: list[list[int]],
    policy_name: str,
    rng: np.random.Generator,
) -> list[Syllable]:
    """Assign one syllable to each note.

    The policy is fixed for the WAV, but the selected syllable varies inside the
    WAV by phrase and by note. This mirrors real singing better than using one
    syllable for a whole TSV.
    """

    if policy_name not in POLICY_WEIGHTS:
        # TODO: Add stricter config validation once policy files become external.
        policy_name = "vowel_heavy"

    result: list[Syllable | None] = [None] * note_count
    categories = (
        list(CORE_VOWELS.values()),
        list(SOFT_SYLLABLES.values()),
        list(HARD_SYLLABLES.values()),
        list(POP_SYLLABLES.values()),
    )
    category_weights = np.array(POLICY_WEIGHTS[policy_name], dtype=float)
    category_weights /= category_weights.sum()

    for phrase in phrases:
        phrase_category = int(rng.choice(len(categories), p=category_weights))
        phrase_syllable = rng.choice(categories[phrase_category])
        repeat_span = int(rng.integers(2, 5))

        for local_index, note_index in enumerate(phrase):
            if local_index == 0 or local_index % repeat_span == 0 or rng.random() < 0.35:
                category = int(rng.choice(len(categories), p=category_weights))
                phrase_syllable = rng.choice(categories[category])
                repeat_span = int(rng.integers(2, 5))
            result[note_index] = phrase_syllable

    return [syllable if syllable is not None else CORE_VOWELS["ah"] for syllable in result]

