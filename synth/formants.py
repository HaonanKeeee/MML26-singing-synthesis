"""Lightweight vowel formant shaping.

This is a source-filter approximation, not a full vocal-tract model. The current
goal is to make syllable changes clearly audible for pipeline/debug data. A
sample-based or neural vocal backend is still needed for realistic human voice.
"""

from __future__ import annotations

import numpy as np


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
    """Apply a pronounced spectral envelope for a vowel color.

    Earlier versions used broad IIR peak filters mixed with a large amount of
    unfiltered harmonic source. That kept labels stable, but it made different
    vowels sound too similar. This FFT-domain envelope intentionally exaggerates
    F1/F2/F3 enough that `ah`, `ee`, `oo`, `eh`, and diphthongs are easier to
    hear in purely synthetic debug audio.
    """

    if waveform.size == 0:
        return waveform

    formants, bandwidths = VOWEL_FORMANTS.get(vowel, VOWEL_FORMANTS["ah"])
    original = waveform.astype(np.float64)
    if original.size < 4:
        return waveform.astype(np.float32)

    spectrum = np.fft.rfft(original)
    freqs = np.fft.rfftfreq(original.size, d=1.0 / sample_rate)
    envelope = _vowel_envelope(
        freqs=freqs,
        formants=formants,
        bandwidths=bandwidths,
        formant_scale=formant_scale,
        brightness=brightness,
        sample_rate=sample_rate,
    )

    shaped = np.fft.irfft(spectrum * envelope, n=original.size)
    # Keep a little direct signal so very short notes do not become hollow, but
    # keep it low enough that vowel identity remains obvious.
    shaped = 0.12 * original + 0.88 * shaped

    input_peak = float(np.max(np.abs(original)))
    output_peak = float(np.max(np.abs(shaped)))
    if output_peak > 1e-8 and input_peak > 1e-8:
        shaped = shaped / output_peak * input_peak
    return shaped.astype(np.float32)


def _vowel_envelope(
    freqs: np.ndarray,
    formants: tuple[int, int, int],
    bandwidths: tuple[int, int, int],
    formant_scale: float,
    brightness: float,
    sample_rate: int,
) -> np.ndarray:
    """Build a smooth, vowel-specific spectral envelope."""

    nyquist = sample_rate * 0.5
    envelope = np.full_like(freqs, 0.025, dtype=np.float64)
    formant_weights = (3.2, 2.4, 1.35)

    for weight, frequency, bandwidth in zip(formant_weights, formants, bandwidths):
        center = min(nyquist * 0.92, max(80.0, frequency * formant_scale))
        width = max(70.0, bandwidth * formant_scale * 1.15)
        envelope += weight * np.exp(-0.5 * ((freqs - center) / width) ** 2)

    # A mild high-frequency shelf makes bright/young presets more forward while
    # still leaving the vowel formants as the main identity cue.
    brightness = max(0.65, min(1.45, brightness))
    shelf = 1.0 + (brightness - 1.0) * np.clip((freqs - 1200.0) / 4200.0, 0.0, 1.0)
    envelope *= shelf

    # Remove sub-audio/DC energy and normalize the envelope safely.
    envelope[freqs < 45.0] = 0.0
    peak = float(np.max(envelope))
    if peak > 1e-8:
        envelope /= peak
    return envelope
