#!/usr/bin/env python3
"""Render one score TSV into one synthetic training sample.

This script is for debugging and listening. Use `build_synthetic_dataset.py` for
bulk generation.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from synth.policies import (  # noqa: E402
    PITCH_POLICIES,
    PITCH_TRANSITION_POLICIES,
    SYLLABLE_POLICIES,
    VIBRATO_POLICIES,
    make_explicit_policy,
)
from synth.render import DEFAULT_SAMPLE_RATE, render_score_to_sample  # noqa: E402
from synth.score_io import load_score_tsv  # noqa: E402
from synth.validate import validate_sample  # noqa: E402
from synth.voice_presets import AGES, GENDERS, STYLES  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render one score TSV into one synthetic vocal sample.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--score", required=True, help="Input TSV score path.")
    parser.add_argument("--output", required=True, help="Output sample directory.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for this sample.")
    parser.add_argument("--sample-rate", type=int, default=DEFAULT_SAMPLE_RATE)
    parser.add_argument("--gender", choices=GENDERS, default="neutral")
    parser.add_argument("--age", choices=AGES, default="young")
    parser.add_argument("--style", choices=STYLES, default="clean")
    parser.add_argument("--syllable-policy", choices=SYLLABLE_POLICIES, default="soft_syllable_mix")
    parser.add_argument("--pitch-policy", choices=PITCH_POLICIES, default="intune")
    parser.add_argument("--vibrato-policy", choices=VIBRATO_POLICIES, default="light")
    parser.add_argument(
        "--pitch-transition-policy",
        choices=PITCH_TRANSITION_POLICIES,
        default="light_scoop",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    notes = load_score_tsv(args.score)
    policy = make_explicit_policy(
        seed=args.seed,
        version_index=0,
        gender=args.gender,
        age=args.age,
        style=args.style,
        syllable_policy=args.syllable_policy,
        pitch_policy=args.pitch_policy,
        vibrato_policy=args.vibrato_policy,
        pitch_transition_policy=args.pitch_transition_policy,
    )

    metadata = render_score_to_sample(
        notes=notes,
        output_dir=args.output,
        policy=policy,
        source_score=str(args.score),
        sample_rate=args.sample_rate,
    )
    issues = validate_sample(args.output, expected_sample_rate=args.sample_rate)

    print(f"Wrote sample: {args.output}")
    print(f"Voice preset: {metadata['voice']['preset_name']}")
    print(f"Notes rendered: {len(metadata['notes'])}")
    if issues:
        print("Validation issues:")
        for issue in issues:
            print(f"  [{issue.severity}] {issue.sample}: {issue.message}")
        raise SystemExit(1)
    print("Validation passed")


if __name__ == "__main__":
    main()

