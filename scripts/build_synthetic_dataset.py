#!/usr/bin/env python3
"""Build a syntheticdataset directory from all score TSV files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from synth.policies import make_policy_for_version  # noqa: E402
from synth.render import DEFAULT_SAMPLE_RATE, render_score_to_sample  # noqa: E402
from synth.score_io import load_score_tsv  # noqa: E402
from synth.validate import validate_sample  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate syntheticdataset/<sample>/audio.wav and score.tsv pairs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--scores-dir", default="scores", help="Directory containing input TSV scores.")
    parser.add_argument("--output-dir", default="syntheticdataset", help="Output synthetic dataset directory.")
    parser.add_argument("--versions-per-score", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--sample-rate", type=int, default=DEFAULT_SAMPLE_RATE)
    parser.add_argument("--limit-scores", type=int, default=None, help="Debug limit for the number of scores.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Rewrite files in existing sample folders. Extra old files are left untouched.",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip per-sample validation during generation.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scores_dir = Path(args.scores_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    score_paths = sorted(scores_dir.glob("*.tsv"))
    if args.limit_scores is not None:
        score_paths = score_paths[: args.limit_scores]
    if not score_paths:
        raise SystemExit(f"No TSV files found in {scores_dir}")

    failures = []
    total_written = 0
    for score_path in tqdm(score_paths, desc="scores"):
        notes = load_score_tsv(score_path)
        for version_index in range(args.versions_per_score):
            policy = make_policy_for_version(args.seed, score_path.stem, version_index)
            sample_name = (
                f"score_{score_path.stem}_"
                f"{policy.gender}_{policy.age}_{policy.style}_"
                f"{policy.syllable_policy}_v{version_index:02d}"
            )
            sample_dir = output_dir / sample_name
            if sample_dir.exists() and not args.overwrite:
                continue

            render_score_to_sample(
                notes=notes,
                output_dir=sample_dir,
                policy=policy,
                source_score=str(score_path),
                sample_rate=args.sample_rate,
            )
            total_written += 1

            if not args.skip_validation:
                issues = validate_sample(sample_dir, expected_sample_rate=args.sample_rate)
                errors = [issue for issue in issues if issue.severity == "error"]
                if errors:
                    failures.extend(errors)

    print(f"Generated or updated {total_written} samples in {output_dir}")
    if failures:
        print("Validation errors:")
        for issue in failures[:50]:
            print(f"  [{issue.severity}] {issue.sample}: {issue.message}")
        if len(failures) > 50:
            print(f"  ... {len(failures) - 50} more")
        raise SystemExit(1)


if __name__ == "__main__":
    main()

