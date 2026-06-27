#!/usr/bin/env python3
"""Validate a generated syntheticdataset directory."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from synth.render import DEFAULT_SAMPLE_RATE  # noqa: E402
from synth.validate import validate_dataset  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate generated synthetic singing samples.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--dataset-dir", default="syntheticdataset")
    parser.add_argument("--sample-rate", type=int, default=DEFAULT_SAMPLE_RATE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    issues = validate_dataset(args.dataset_dir, expected_sample_rate=args.sample_rate)
    counts = Counter(issue.severity for issue in issues)

    if not issues:
        print(f"Validation passed: {args.dataset_dir}")
        return

    print(f"Validation issues for {args.dataset_dir}:")
    for issue in issues:
        print(f"  [{issue.severity}] {issue.sample}: {issue.message}")
    print(f"Summary: {dict(counts)}")

    if counts.get("error", 0):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

