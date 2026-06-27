"""Amplitude envelope helpers."""

from __future__ import annotations

import numpy as np


def note_envelope(
    n_samples: int,
    sample_rate: int,
    attack_s: float,
    release_s: float,
) -> np.ndarray:
    """Create a simple click-safe note envelope.

    The envelope is intentionally short so onset and offset labels stay clear.
    """

    if n_samples <= 0:
        return np.zeros(0, dtype=np.float32)

    env = np.ones(n_samples, dtype=np.float32)
    attack_n = min(n_samples, max(1, int(round(attack_s * sample_rate))))
    release_n = min(n_samples, max(1, int(round(release_s * sample_rate))))

    env[:attack_n] *= np.linspace(0.0, 1.0, attack_n, endpoint=True, dtype=np.float32)
    env[-release_n:] *= np.linspace(1.0, 0.0, release_n, endpoint=True, dtype=np.float32)
    return env

