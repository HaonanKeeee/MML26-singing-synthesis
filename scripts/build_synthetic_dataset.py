#!/usr/bin/env python3
"""Build a syntheticdataset directory from all score TSV files."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from synth.policies import make_grid_policy, make_policy_for_version  # noqa: E402
from synth.render import DEFAULT_SAMPLE_RATE, render_score_to_sample  # noqa: E402
import synth.sample_render as sample_render  # noqa: E402
from synth.sample_render import render_score_to_word_unit_sample  # noqa: E402
from synth.score_io import load_score_tsv  # noqa: E402
from synth.unit_bank import AudioUnitBank  # noqa: E402
from synth.validate import validate_sample  # noqa: E402
from synth.voice_ranges import (  # noqa: E402
    is_voice_allowed_by_filter,
    recommended_gender_for_score,
    score_pitch_stats,
)
from synth.voice_presets import AGES, GENDERS, STYLES  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate syntheticdataset/<sample>/audio.wav and score.tsv pairs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--scores-dir", default="scores", help="Directory containing input TSV scores.")
    parser.add_argument("--output-dir", default="syntheticdataset", help="Output synthetic dataset directory.")
    parser.add_argument(
        "--generation-mode",
        choices=("grid", "random_versions"),
        default="grid",
        help="Use age/gender/style grid generation or the older random-version sampler.",
    )
    parser.add_argument(
        "--versions-per-score",
        type=int,
        default=8,
        help="Number of random versions per score. Only used by random_versions mode.",
    )
    parser.add_argument(
        "--versions-per-combination",
        type=int,
        default=1,
        help="Number of repeats for each age/gender/style combination in grid mode.",
    )
    parser.add_argument(
        "--genders",
        default=",".join(GENDERS),
        help="Comma-separated gender presets to use in grid mode.",
    )
    parser.add_argument(
        "--gender-assignment",
        choices=("requested", "auto"),
        default="requested",
        help=(
            "`requested` uses --genders exactly. `auto` picks male or female "
            "per TSV from pitch tessitura, then intersects that with --genders."
        ),
    )
    parser.add_argument(
        "--ages",
        default=",".join(AGES),
        help="Comma-separated age presets to use in grid mode.",
    )
    parser.add_argument(
        "--styles",
        default=",".join(STYLES),
        help="Comma-separated style presets to use in grid mode.",
    )
    parser.add_argument(
        "--voice-range-filter",
        choices=("allowed", "comfortable", "off"),
        default="allowed",
        help=(
            "Filter age/gender presets by the TSV pitch range. "
            "`allowed` keeps comfortable and extended-range voices, "
            "`comfortable` keeps only comfortable ranges, and `off` keeps the full grid."
        ),
    )
    parser.add_argument(
        "--renderer",
        choices=("algorithmic", "edge_tts_words"),
        default="algorithmic",
        help="Audio rendering backend to use for generated samples.",
    )
    parser.add_argument(
        "--unit-bank-dir",
        default="voice_units/edge_tts_words_10voices",
        help="Unit-bank directory used by --renderer=edge_tts_words.",
    )
    parser.add_argument(
        "--melisma-selection-fraction",
        type=float,
        default=None,
        help=(
            "Optional fraction of candidate same-syllable groups to render. "
            "Use 1.0 for listening/debug checks where every valid TSV group "
            "should become one syllable."
        ),
    )
    parser.add_argument(
        "--melisma-unit-keys",
        default=None,
        help=(
            "Optional comma-separated unit keys for same-syllable groups, "
            "for example `la` or `la,yeah`. Only used by --renderer=edge_tts_words."
        ),
    )
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
    parser.add_argument(
        "--zero-release",
        action="store_true",
        help=(
            "Disable note-end release fades in the edge_tts_words renderer so "
            "each rendered note stays at full envelope until its TSV offset."
        ),
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

    unit_bank = None
    if args.renderer == "edge_tts_words":
        if args.zero_release:
            _disable_edge_tts_release()
        unit_bank = AudioUnitBank(args.unit_bank_dir, sample_rate=args.sample_rate)

    failures = []
    total_written = 0
    total_skipped_by_range = 0
    for score_path in tqdm(score_paths, desc="scores"):
        notes = load_score_tsv(score_path)
        pitch_stats = score_pitch_stats(notes)
        policies, skipped_by_range = _policies_for_score(args, score_path.stem, pitch_stats)
        total_skipped_by_range += skipped_by_range
        used_word_sequences: dict[tuple[str, ...], str] = {}

        for policy in policies:
            sample_name = _sample_name(score_path.stem, policy)
            sample_dir = output_dir / sample_name
            if sample_dir.exists() and not args.overwrite:
                continue

            if args.renderer == "edge_tts_words":
                if unit_bank is None:
                    raise RuntimeError("Unit bank was not loaded for edge_tts_words renderer")
                _render_unique_word_sequence_sample(
                    notes=notes,
                    output_dir=sample_dir,
                    policy=policy,
                    source_score=str(score_path),
                    unit_bank=unit_bank,
                    sample_rate=args.sample_rate,
                    melisma_selection_fraction=args.melisma_selection_fraction,
                    melisma_unit_keys=_parse_optional_csv(args.melisma_unit_keys),
                    sample_name=sample_name,
                    used_word_sequences=used_word_sequences,
                )
            else:
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
    if args.voice_range_filter != "off":
        print(
            f"Skipped {total_skipped_by_range} age/gender/style/version combinations "
            f"with --voice-range-filter={args.voice_range_filter}"
        )
    if failures:
        print("Validation errors:")
        for issue in failures[:50]:
            print(f"  [{issue.severity}] {issue.sample}: {issue.message}")
        if len(failures) > 50:
            print(f"  ... {len(failures) - 50} more")
        raise SystemExit(1)


def _disable_edge_tts_release() -> None:
    sample_render.NOTE_RELEASE_MIN_S = 0.0
    sample_render.NOTE_RELEASE_MAX_S = 0.0
    sample_render.NOTE_RELEASE_DURATION_FRACTION = 0.0
    sample_render.GROUP_RELEASE_MIN_S = 0.0
    sample_render.GROUP_RELEASE_MAX_S = 0.0
    sample_render.GROUP_RELEASE_DURATION_FRACTION = 0.0


def _render_unique_word_sequence_sample(
    *,
    notes,
    output_dir: Path,
    policy,
    source_score: str,
    unit_bank: AudioUnitBank,
    sample_rate: int,
    melisma_selection_fraction: float | None,
    melisma_unit_keys: tuple[str, ...] | None,
    sample_name: str,
    used_word_sequences: dict[tuple[str, ...], str],
) -> dict:
    """Render with a unique word-unit sequence among samples from one TSV."""

    max_attempts = 16
    for attempt in range(max_attempts):
        render_policy = policy
        if attempt > 0:
            render_policy = replace(
                policy,
                seed=(int(policy.seed) + attempt * 104729) & 0xFFFFFFFF,
            )

        metadata = render_score_to_word_unit_sample(
            notes=notes,
            output_dir=output_dir,
            policy=render_policy,
            source_score=source_score,
            unit_bank=unit_bank,
            sample_rate=sample_rate,
            melisma_selection_fraction=melisma_selection_fraction,
            melisma_unit_keys=melisma_unit_keys,
        )
        sequence = _word_unit_sequence(metadata)
        previous_sample = used_word_sequences.get(sequence)
        if previous_sample is None:
            used_word_sequences[sequence] = sample_name
            return metadata

    raise RuntimeError(
        f"Could not generate a unique word-unit sequence for {sample_name} "
        f"after {max_attempts} attempts. Last duplicate matched {previous_sample}."
    )


def _word_unit_sequence(metadata: dict) -> tuple[str, ...]:
    return tuple(str(note.get("word_unit", "")) for note in metadata.get("notes", []))


def _policies_for_score(args: argparse.Namespace, score_stem: str, pitch_stats):
    policies = []
    skipped_by_range = 0
    assigned_gender = _assigned_gender(args, pitch_stats)

    if args.generation_mode == "random_versions":
        for version_index in range(args.versions_per_score):
            policy = make_policy_for_version(args.seed, score_stem, version_index)
            if assigned_gender is not None and policy.gender != assigned_gender:
                skipped_by_range += 1
                continue
            if _policy_allowed_by_voice_range(args, pitch_stats, policy.gender, policy.age):
                policies.append(policy)
            else:
                skipped_by_range += 1
        return policies, skipped_by_range

    genders = _parse_subset(args.genders, GENDERS, "gender")
    if assigned_gender is not None:
        genders = [gender for gender in genders if gender == assigned_gender]
    ages = _parse_subset(args.ages, AGES, "age")
    styles = _parse_subset(args.styles, STYLES, "style")
    for gender in genders:
        for age in ages:
            voice_allowed = _policy_allowed_by_voice_range(args, pitch_stats, gender, age)
            for style in styles:
                for version_index in range(args.versions_per_combination):
                    if not voice_allowed:
                        skipped_by_range += 1
                        continue
                    policies.append(
                        make_grid_policy(
                            base_seed=args.seed,
                            score_stem=score_stem,
                            gender=gender,
                            age=age,
                            style=style,
                            version_index=version_index,
                        )
                    )
    return policies, skipped_by_range


def _assigned_gender(args: argparse.Namespace, pitch_stats) -> str | None:
    if args.gender_assignment == "requested":
        return None
    if args.gender_assignment == "auto":
        return recommended_gender_for_score(pitch_stats)
    raise ValueError(f"Unsupported gender assignment mode: {args.gender_assignment}")


def _policy_allowed_by_voice_range(
    args: argparse.Namespace,
    pitch_stats,
    gender: str,
    age: str,
) -> bool:
    return is_voice_allowed_by_filter(
        stats=pitch_stats,
        gender=gender,
        age=age,
        filter_mode=args.voice_range_filter,
    )


def _sample_name(score_stem: str, policy) -> str:
    return (
        f"score_{score_stem}_"
        f"{policy.gender}_{policy.age}_{policy.style}_"
        f"v{policy.version_index:02d}"
    )


def _parse_subset(raw: str, allowed: tuple[str, ...], label: str) -> list[str]:
    values = [value.strip() for value in raw.split(",") if value.strip()]
    if not values:
        raise SystemExit(f"At least one {label} preset must be provided")
    invalid = [value for value in values if value not in allowed]
    if invalid:
        raise SystemExit(
            f"Invalid {label} preset(s): {', '.join(invalid)}. "
            f"Allowed values: {', '.join(allowed)}"
        )
    return values


def _parse_optional_csv(raw: str | None) -> tuple[str, ...] | None:
    if raw is None:
        return None
    values = tuple(value.strip() for value in raw.split(",") if value.strip())
    return values or None


if __name__ == "__main__":
    main()
