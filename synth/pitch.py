"""Pitch conversion helpers.

All pitch curves must remain centered around the TSV MIDI pitch. Small detune,
vibrato, and short transitions are audio-expression details, not label changes.
"""

from __future__ import annotations

import numpy as np


def midi_to_hz(midi_note: float) -> float:
    """Convert a MIDI pitch number to frequency in Hertz."""

    return float(440.0 * (2.0 ** ((midi_note - 69.0) / 12.0)))


def cents_to_ratio(cents: float | np.ndarray) -> float | np.ndarray:
    """Convert cents to a multiplicative frequency ratio."""

    return 2.0 ** (np.asarray(cents) / 1200.0)


def midi_to_hz_with_cents(midi_note: float, cents: float | np.ndarray) -> np.ndarray:
    """Convert MIDI pitch plus cents offset to a frequency curve."""

    return midi_to_hz(midi_note) * cents_to_ratio(cents)

