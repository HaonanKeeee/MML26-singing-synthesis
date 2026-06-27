"""Lightweight vowel formant shaping.

This is a source-filter approximation, not a full vocal-tract model. It is good
enough for a first synthetic dataset pass and can be replaced later.
"""

from __future__ import annotations

import numpy as np
from scipy import signal


VOWEL_FORMANTS = {
    # Frequencies are approximate English-like vowel centers.
    "ah": ((730, 1090, 2440), (90, 120, 180)),
    "ae": ((660, 1720, 2410), (90, 130, 180)),
    "eh": ((530, 1840, 2480), (80, 120, 180)),
    "ee": ((300, 2200, 3000), (70, 110, 200)),
    "ih": ((390, 1990, 2550), (70, 120, 180)),
    "oh": ((570, 840, 2410), (80, 110, 180)),
    "aw": ((590, 920, 2420), (80, 110, 180)),
    "oo": ((300, 870, 2240), (70, 110, 180)),
    "uh": ((440, 1020, 2240), (80, 120, 180)),
    "er": ((490, 1350, 1690), (80, 120, 160)),
}


def apply_vowel_formants(
    waveform: np.ndarray,
    sample_rate: int,
    vowel: str,
    formant_scale: float,
    brightness: float,
) -> np.ndarray:
    """Apply broad resonant filters for a vowel color."""

    if waveform.size == 0:
        return waveform

    formants, bandwidths = VOWEL_FORMANTS.get(vowel, VOWEL_FORMANTS["ah"])
    shaped = 0.20 * waveform.astype(np.float64)
    nyquist = sample_rate * 0.5

    for index, (frequency, bandwidth) in enumerate(zip(formants, bandwidths)):
        center = min(nyquist * 0.92, max(80.0, frequency * formant_scale))
        q = max(1.0, center / max(60.0, bandwidth))
        b, a = signal.iirpeak(center / nyquist, q)
        band = signal.lfilter(b, a, waveform)
        weight = (1.0 / (index + 1)) * (brightness ** (0.5 if index else 0.2))
        shaped += weight * band

    peak = np.max(np.abs(shaped))
    if peak > 1e-8:
        shaped = shaped / peak * max(1e-8, np.max(np.abs(waveform)))
    return shaped.astype(np.float32)

