#!/usr/bin/env python3
"""Generate short word/syllable audio units with edge-tts.

This script builds a reusable voice-unit bank. It does not generate the final
`syntheticdataset` samples directly. The intended workflow is:

1. Generate short clean TTS units such as `ah`, `ee`, `la`, `hey`, and `sha`.
2. Store them as 16 kHz mono WAV files under `voice_units/edge_tts`.
3. Let a later sample-based renderer pitch-shift, time-stretch, and ornament
   these units to match each TSV note.

TODO: Confirm the chosen TTS provider's terms before using generated units for
competition training or checkpoint submission.
TODO: Add a sample-based renderer that consumes this unit bank.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf


DEFAULT_SAMPLE_RATE = 16_000


@dataclass(frozen=True)
class VoiceSpec:
    """One edge-tts voice used to create a unit bank."""

    label: str
    voice: str
    gender: str = ""
    locale: str = ""


@dataclass(frozen=True)
class UnitSpec:
    """One target unit and the text prompt sent to TTS."""

    key: str
    text: str
    group: str


DEFAULT_VOICES = (
    VoiceSpec("female_aria", "en-US-AriaNeural", "Female", "en-US"),
    VoiceSpec("female_jenny", "en-US-JennyNeural", "Female", "en-US"),
    VoiceSpec("male_guy", "en-US-GuyNeural", "Male", "en-US"),
    VoiceSpec("male_andrew", "en-US-AndrewNeural", "Male", "en-US"),
)


VOWEL_UNITS = (
    UnitSpec("ah", "ah", "vowel"),
    UnitSpec("aa", "ah", "vowel"),
    UnitSpec("ae", "aah", "vowel"),
    UnitSpec("eh", "eh", "vowel"),
    UnitSpec("ee", "ee", "vowel"),
    UnitSpec("ih", "ih", "vowel"),
    UnitSpec("oh", "oh", "vowel"),
    UnitSpec("aw", "aw", "vowel"),
    UnitSpec("oo", "ooh", "vowel"),
    UnitSpec("uh", "uh", "vowel"),
    UnitSpec("er", "er", "vowel"),
)


SOFT_UNITS = tuple(
    UnitSpec(key, key, "soft")
    for key in (
        "la",
        "le",
        "li",
        "lo",
        "lu",
        "ma",
        "me",
        "mi",
        "mo",
        "mu",
        "na",
        "ne",
        "ni",
        "no",
        "nu",
        "ya",
        "ye",
        "yi",
        "yo",
        "yu",
        "wa",
        "we",
        "wi",
        "wo",
        "wu",
        "ra",
        "re",
        "ri",
        "ro",
        "ru",
    )
)


CONSONANT_UNITS = tuple(
    UnitSpec(key, key, "consonant")
    for key in (
        "pa",
        "ta",
        "ka",
        "ba",
        "da",
        "ga",
        "ha",
        "sa",
        "sha",
        "fa",
        "tha",
    )
)


CLEAR_ATTACK_UNITS = tuple(
    UnitSpec(f"{consonant}_{vowel}", f"{consonant_text}{vowel_text}", "clear_attack")
    for consonant, consonant_text in (
        ("t", "t"),
        ("k", "k"),
        ("h", "h"),
        ("sh", "sh"),
    )
    for vowel, vowel_text in (
        ("a", "a"),
        ("e", "e"),
        ("ae", "ae"),
        ("i", "i"),
        ("o", "o"),
        ("u", "u"),
        ("au", "au"),
    )
)


POP_UNITS = (
    UnitSpec("hey", "hey", "pop"),
    UnitSpec("yeah", "yeah", "pop"),
    UnitSpec("yea", "yeah", "pop"),
    UnitSpec("ooh", "ooh", "pop"),
    UnitSpec("woo", "woo", "pop"),
    UnitSpec("whoa", "whoa", "pop"),
    UnitSpec("nah", "nah", "pop"),
    UnitSpec("lah", "lah", "pop"),
    UnitSpec("doo", "doo", "pop"),
    UnitSpec("mm", "mm", "pop"),
    UnitSpec("hmm", "hmm", "pop"),
)


SIMPLE20_UNITS = (
    UnitSpec("i", "I", "simple20"),
    UnitSpec("oh", "oh", "simple20"),
    UnitSpec("ah", "ah", "simple20"),
    UnitSpec("ooh", "ooh", "simple20"),
    UnitSpec("la", "la", "simple20"),
    UnitSpec("tea", "tea", "simple20"),
    UnitSpec("see", "see", "simple20"),
    UnitSpec("me", "me", "simple20"),
    UnitSpec("we", "we", "simple20"),
    UnitSpec("he", "he", "simple20"),
    UnitSpec("she", "she", "simple20"),
    UnitSpec("day", "day", "simple20"),
    UnitSpec("go", "go", "simple20"),
    UnitSpec("no", "no", "simple20"),
    UnitSpec("so", "so", "simple20"),
    UnitSpec("you", "you", "simple20"),
    UnitSpec("way", "way", "simple20"),
    UnitSpec("sun", "sun", "simple20"),
    UnitSpec("fun", "fun", "simple20"),
    UnitSpec("run", "run", "simple20"),
)


WORD_BANK_BASIC_UNITS = (
    UnitSpec("you", "you", "word"),
    UnitSpec("i", "I", "word"),
    UnitSpec("me", "me", "word"),
    UnitSpec("my", "my", "word"),
    UnitSpec("we", "we", "word"),
    UnitSpec("us", "us", "word"),
    UnitSpec("he", "he", "word"),
    UnitSpec("she", "she", "word"),
    UnitSpec("it", "it", "word"),
    UnitSpec("they", "they", "word"),
    UnitSpec("them", "them", "word"),
    UnitSpec("the", "the", "word"),
    UnitSpec("a", "a", "word"),
    UnitSpec("and", "and", "word"),
    UnitSpec("or", "or", "word"),
    UnitSpec("but", "but", "word"),
    UnitSpec("to", "to", "word"),
    UnitSpec("in", "in", "word"),
    UnitSpec("on", "on", "word"),
    UnitSpec("for", "for", "word"),
    UnitSpec("with", "with", "word"),
    UnitSpec("of", "of", "word"),
    UnitSpec("is", "is", "word"),
    UnitSpec("are", "are", "word"),
    UnitSpec("was", "was", "word"),
    UnitSpec("be", "be", "word"),
    UnitSpec("am", "am", "word"),
    UnitSpec("do", "do", "word"),
    UnitSpec("can", "can", "word"),
    UnitSpec("will", "will", "word"),
    UnitSpec("go", "go", "word"),
    UnitSpec("come", "come", "word"),
    UnitSpec("get", "get", "word"),
    UnitSpec("got", "got", "word"),
    UnitSpec("give", "give", "word"),
    UnitSpec("take", "take", "word"),
    UnitSpec("make", "make", "word"),
    UnitSpec("let", "let", "word"),
    UnitSpec("say", "say", "word"),
    UnitSpec("know", "know", "word"),
    UnitSpec("think", "think", "word"),
    UnitSpec("want", "want", "word"),
    UnitSpec("need", "need", "word"),
    UnitSpec("see", "see", "word"),
    UnitSpec("look", "look", "word"),
    UnitSpec("feel", "feel", "word"),
    UnitSpec("hear", "hear", "word"),
    UnitSpec("touch", "touch", "word"),
    UnitSpec("hold", "hold", "word"),
    UnitSpec("keep", "keep", "word"),
    UnitSpec("leave", "leave", "word"),
    UnitSpec("stay", "stay", "word"),
    UnitSpec("fall", "fall", "word"),
    UnitSpec("run", "run", "word"),
    UnitSpec("walk", "walk", "word"),
    UnitSpec("dance", "dance", "word"),
    UnitSpec("sing", "sing", "word"),
    UnitSpec("cry", "cry", "word"),
    UnitSpec("smile", "smile", "word"),
    UnitSpec("love", "love", "word"),
    UnitSpec("heart", "heart", "word"),
    UnitSpec("girl", "girl", "word"),
    UnitSpec("boy", "boy", "word"),
    UnitSpec("man", "man", "word"),
    UnitSpec("friend", "friend", "word"),
    UnitSpec("home", "home", "word"),
    UnitSpec("life", "life", "word"),
    UnitSpec("time", "time", "word"),
    UnitSpec("day", "day", "word"),
    UnitSpec("night", "night", "word"),
    UnitSpec("world", "world", "word"),
    UnitSpec("dream", "dream", "word"),
    UnitSpec("mind", "mind", "word"),
    UnitSpec("eyes", "eyes", "word"),
    UnitSpec("hands", "hands", "word"),
    UnitSpec("fire", "fire", "word"),
    UnitSpec("rain", "rain", "word"),
    UnitSpec("sun", "sun", "word"),
    UnitSpec("moon", "moon", "word"),
    UnitSpec("light", "light", "word"),
    UnitSpec("dark", "dark", "word"),
    UnitSpec("blue", "blue", "word"),
    UnitSpec("good", "good", "word"),
    UnitSpec("bad", "bad", "word"),
    UnitSpec("right", "right", "word"),
    UnitSpec("wrong", "wrong", "word"),
    UnitSpec("back", "back", "word"),
    UnitSpec("up", "up", "word"),
    UnitSpec("down", "down", "word"),
    UnitSpec("now", "now", "word"),
    UnitSpec("oh", "oh", "word"),
    UnitSpec("yeah", "yeah", "word"),
    UnitSpec("hey", "hey", "word"),
    UnitSpec("la", "la", "word"),
)


UNIT_SETS = {
    "vowels": VOWEL_UNITS,
    "soft": SOFT_UNITS,
    "consonants": CONSONANT_UNITS,
    "clear_attacks": CLEAR_ATTACK_UNITS,
    "pop": POP_UNITS,
    "simple20": SIMPLE20_UNITS,
    "mvp": (
        UnitSpec("ah", "ah", "vowel"),
        UnitSpec("eh", "eh", "vowel"),
        UnitSpec("ee", "ee", "vowel"),
        UnitSpec("oh", "oh", "vowel"),
        UnitSpec("oo", "ooh", "vowel"),
        UnitSpec("uh", "uh", "vowel"),
        UnitSpec("la", "la", "soft"),
        UnitSpec("ma", "ma", "soft"),
        UnitSpec("na", "na", "soft"),
        UnitSpec("ya", "ya", "soft"),
        UnitSpec("wa", "wa", "soft"),
        UnitSpec("hey", "hey", "pop"),
        UnitSpec("yeah", "yeah", "pop"),
        UnitSpec("ooh", "ooh", "pop"),
        UnitSpec("woo", "woo", "pop"),
        UnitSpec("whoa", "whoa", "pop"),
        UnitSpec("doo", "doo", "pop"),
        UnitSpec("ta", "ta", "consonant"),
        UnitSpec("ka", "ka", "consonant"),
        UnitSpec("sa", "sa", "consonant"),
        UnitSpec("sha", "sha", "consonant"),
    ),
    "word_bank_basic": WORD_BANK_BASIC_UNITS,
    "word_bank_clear_attacks": WORD_BANK_BASIC_UNITS + CLEAR_ATTACK_UNITS,
}
UNIT_SETS["extended"] = (
    VOWEL_UNITS + SOFT_UNITS + CONSONANT_UNITS + CLEAR_ATTACK_UNITS + POP_UNITS
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a short edge-tts voice-unit bank.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--output-dir",
        default="voice_units/edge_tts",
        help="Directory where WAV unit files and metadata are written.",
    )
    parser.add_argument(
        "--unit-set",
        choices=tuple(UNIT_SETS),
        default="mvp",
        help="Predefined unit list to generate.",
    )
    parser.add_argument(
        "--units",
        default=None,
        help=(
            "Optional comma-separated custom units. Use `key` or `key:text`; "
            "for example `ah,oo:ooh,sha`."
        ),
    )
    parser.add_argument(
        "--voice",
        action="append",
        default=None,
        help=(
            "Voice spec in `label=edgeVoiceName` format. Can be passed multiple "
            "times. Defaults to two female and two male English voices."
        ),
    )
    parser.add_argument(
        "--edge-voice-locale-prefix",
        default=None,
        help=(
            "Fetch all current edge-tts voices whose locale starts with this prefix, "
            "for example `en-`. This requires network access and overrides default voices."
        ),
    )
    parser.add_argument(
        "--edge-voice-genders",
        default="Female,Male",
        help="Comma-separated edge voice genders to include with --edge-voice-locale-prefix.",
    )
    parser.add_argument("--rate", default="+0%", help="edge-tts speaking rate adjustment.")
    parser.add_argument("--volume", default="+0%", help="edge-tts volume adjustment.")
    parser.add_argument("--pitch", default="+0Hz", help="edge-tts pitch adjustment.")
    parser.add_argument("--sample-rate", type=int, default=DEFAULT_SAMPLE_RATE)
    parser.add_argument("--trim-top-db", type=float, default=35.0)
    parser.add_argument("--pad-ms", type=float, default=40.0)
    parser.add_argument(
        "--delay-s",
        type=float,
        default=0.25,
        help="Small delay between online TTS calls to avoid hammering the service.",
    )
    parser.add_argument("--retries", type=int, default=2, help="Retries per unit after TTS failures.")
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with an error if any unit fails after retries.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Rewrite existing WAV units.")
    parser.add_argument("--keep-raw", action="store_true", help="Keep raw MP3 files from edge-tts.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned units without network calls.")
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="List available edge-tts voices and exit. This requires network access.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.list_voices:
        asyncio.run(_list_voices())
        return

    voices = _resolve_voices(args)
    units = _parse_units(args.unit_set, args.units)
    output_dir = Path(args.output_dir)

    if args.dry_run:
        for voice in voices:
            for unit in units:
                print(_unit_wav_path(output_dir, voice, unit))
        print(f"Planned {len(voices) * len(units)} unit WAV files")
        return

    asyncio.run(_generate_all(args, output_dir, voices, units))


async def _generate_all(
    args: argparse.Namespace,
    output_dir: Path,
    voices: list[VoiceSpec],
    units: list[UnitSpec],
) -> None:
    try:
        import edge_tts
    except ImportError as exc:
        raise SystemExit(
            "Missing optional dependency `edge-tts`. Install it with "
            "`../.venv/bin/python -m pip install edge-tts` or reinstall requirements."
        ) from exc

    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "_raw"
    records = []
    failures = []
    generated = 0
    skipped = 0

    for voice in voices:
        for unit in units:
            wav_path = _unit_wav_path(output_dir, voice, unit)
            raw_path = raw_dir / voice.label / f"{unit.key}.mp3"
            if wav_path.exists() and not args.overwrite:
                skipped += 1
                records.append(_metadata_record(voice, unit, wav_path, generated=False))
                continue

            wav_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.parent.mkdir(parents=True, exist_ok=True)

            error: Exception | None = None
            for attempt in range(args.retries + 1):
                try:
                    communicate = edge_tts.Communicate(
                        text=unit.text,
                        voice=voice.voice,
                        rate=args.rate,
                        volume=args.volume,
                        pitch=args.pitch,
                    )
                    await communicate.save(str(raw_path))
                    _convert_raw_to_wav(
                        raw_path=raw_path,
                        wav_path=wav_path,
                        sample_rate=args.sample_rate,
                        trim_top_db=args.trim_top_db,
                        pad_ms=args.pad_ms,
                    )
                    if not args.keep_raw:
                        raw_path.unlink(missing_ok=True)
                    error = None
                    break
                except Exception as exc:  # noqa: BLE001 - keep batch generation resumable.
                    error = exc
                    raw_path.unlink(missing_ok=True)
                    if attempt < args.retries:
                        retry_delay = max(args.delay_s, 0.5) * float(attempt + 1)
                        await asyncio.sleep(retry_delay)

            if error is not None:
                failure = {
                    "voice_label": voice.label,
                    "edge_voice": voice.voice,
                    "unit": unit.key,
                    "text": unit.text,
                    "error": f"{type(error).__name__}: {error}",
                }
                failures.append(failure)
                print(
                    f"Failed {voice.label}/{unit.key} after {args.retries + 1} attempts: {error}",
                    file=sys.stderr,
                )
                continue

            generated += 1
            records.append(_metadata_record(voice, unit, wav_path, generated=True))
            if args.delay_s > 0:
                await asyncio.sleep(args.delay_s)

    metadata = {
        "generator": "edge-tts",
        "sample_rate": args.sample_rate,
        "unit_count": len(units),
        "voice_count": len(voices),
        "generated_count": generated,
        "skipped_existing_count": skipped,
        "failed_count": len(failures),
        "voices": [asdict(voice) for voice in voices],
        "units": [asdict(unit) for unit in units],
        "files": records,
        "failures": failures,
        "todos": [
            "TODO: Verify TTS terms before using generated units for competition training.",
            "TODO: Add pitch-shift/time-stretch sample renderer that consumes this bank.",
        ],
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
    print(f"Generated {generated} new unit WAV files in {output_dir}")
    if skipped:
        print(f"Skipped {skipped} existing unit WAV files")
    if failures:
        print(f"Failed {len(failures)} unit WAV files; see metadata.json for details")
        if args.fail_on_error:
            raise SystemExit(1)


async def _list_voices() -> None:
    try:
        import edge_tts
    except ImportError as exc:
        raise SystemExit("Missing optional dependency `edge-tts`.") from exc

    voices = await edge_tts.list_voices()
    for voice in voices:
        locale = voice.get("Locale", "")
        short_name = voice.get("ShortName", "")
        gender = voice.get("Gender", "")
        if locale.startswith("en-"):
            print(f"{short_name}\t{gender}\t{locale}")


def _resolve_voices(args: argparse.Namespace) -> list[VoiceSpec]:
    if args.edge_voice_locale_prefix and args.voice:
        raise SystemExit("Use either --voice or --edge-voice-locale-prefix, not both")
    if args.edge_voice_locale_prefix:
        return asyncio.run(
            _fetch_edge_voices(
                locale_prefix=args.edge_voice_locale_prefix,
                genders=args.edge_voice_genders,
            )
        )
    return _parse_voices(args.voice)


async def _fetch_edge_voices(locale_prefix: str, genders: str) -> list[VoiceSpec]:
    """Fetch the current edge-tts catalog and return matching voices."""

    try:
        import edge_tts
    except ImportError as exc:
        raise SystemExit("Missing optional dependency `edge-tts`.") from exc

    allowed_genders = {value.strip() for value in genders.split(",") if value.strip()}
    voices = []
    seen_labels = set()
    for voice in await edge_tts.list_voices():
        locale = voice.get("Locale", "")
        gender = voice.get("Gender", "")
        short_name = voice.get("ShortName", "")
        if not locale.startswith(locale_prefix):
            continue
        if allowed_genders and gender not in allowed_genders:
            continue

        label = _safe_name(f"{gender}_{short_name}")
        if label in seen_labels:
            label = _safe_name(f"{label}_{locale}")
        seen_labels.add(label)
        voices.append(VoiceSpec(label=label, voice=short_name, gender=gender, locale=locale))

    if not voices:
        raise SystemExit(
            f"No edge-tts voices found for locale prefix {locale_prefix!r} "
            f"and genders {sorted(allowed_genders)!r}"
        )
    return sorted(voices, key=lambda item: (item.locale, item.gender, item.voice))


def _convert_raw_to_wav(
    raw_path: Path,
    wav_path: Path,
    sample_rate: int,
    trim_top_db: float,
    pad_ms: float,
) -> None:
    """Decode edge-tts output, trim silence, pad lightly, and save mono WAV."""

    audio, _ = librosa.load(raw_path, sr=sample_rate, mono=True)
    if audio.size == 0:
        raise ValueError(f"Decoded empty audio from {raw_path}")

    trimmed, _ = librosa.effects.trim(audio, top_db=trim_top_db)
    if trimmed.size > 0:
        audio = trimmed

    pad = int(round(sample_rate * pad_ms / 1000.0))
    if pad > 0:
        audio = np.pad(audio, (pad, pad), mode="constant")

    audio = np.nan_to_num(audio.astype(np.float32))
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if peak > 1e-8:
        audio = audio / peak * 0.90
    sf.write(wav_path, audio, sample_rate)


def _parse_voices(raw_specs: list[str] | None) -> list[VoiceSpec]:
    if not raw_specs:
        return list(DEFAULT_VOICES)

    voices = []
    for raw in raw_specs:
        if "=" not in raw:
            raise SystemExit(f"Invalid --voice value {raw!r}; expected label=edgeVoiceName")
        label, voice = raw.split("=", 1)
        label = _safe_name(label.strip())
        voice = voice.strip()
        if not label or not voice:
            raise SystemExit(f"Invalid --voice value {raw!r}; expected label=edgeVoiceName")
        voices.append(VoiceSpec(label, voice))
    return voices


def _parse_units(unit_set: str, raw_units: str | None) -> list[UnitSpec]:
    if raw_units is None:
        return list(UNIT_SETS[unit_set])

    units = []
    for raw in raw_units.split(","):
        raw = raw.strip()
        if not raw:
            continue
        if ":" in raw:
            key, text = raw.split(":", 1)
        else:
            key, text = raw, raw
        units.append(UnitSpec(_safe_name(key.strip()), text.strip(), "custom"))
    if not units:
        raise SystemExit("At least one unit must be provided")
    return units


def _unit_wav_path(output_dir: Path, voice: VoiceSpec, unit: UnitSpec) -> Path:
    return output_dir / voice.label / f"{unit.key}.wav"


def _metadata_record(
    voice: VoiceSpec,
    unit: UnitSpec,
    wav_path: Path,
    generated: bool,
) -> dict[str, str | bool]:
    return {
        "voice_label": voice.label,
        "edge_voice": voice.voice,
        "gender": voice.gender,
        "locale": voice.locale,
        "unit": unit.key,
        "text": unit.text,
        "group": unit.group,
        "wav_path": str(wav_path),
        "generated_this_run": generated,
    }


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_").lower()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
