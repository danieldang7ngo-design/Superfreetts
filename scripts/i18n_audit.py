#!/usr/bin/env python3
"""Report UI string coverage for every packaged locale.

The add-on falls back to English when a key is missing, and returns the raw key
when English is missing too - which is how ``mms_manager_error_installed`` and
``error_batch_stalled`` ended up visible in the UI.  This script makes that
class of mistake impossible to miss, and ``--check`` can gate the locales that
must be fully translated (English and Vietnamese by default).

Usage:
    python scripts/i18n_audit.py                       # human-readable report
    python scripts/i18n_audit.py --check               # exit 1 on any gap
    python scripts/i18n_audit.py --check --strict-locales en,vi,ja
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADDON = ROOT / "superfreetts_addon"
LOCALES = ADDON / "locales"
KEY_PATTERN = re.compile(r'get_text\(\s*["\']([A-Za-z0-9_]+)["\']')
DEFAULT_STRICT_LOCALES = "en,vi"


def load_locale(lang: str) -> dict:
    path = LOCALES / f"{lang}.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def supported_languages() -> list[str]:
    return sorted(path.stem for path in LOCALES.glob("*.json"))


def keys_used_in_code() -> set[str]:
    used: set[str] = set()
    for path in ADDON.rglob("*.py"):
        source = path.read_text(encoding="utf-8", errors="replace")
        used.update(KEY_PATTERN.findall(source))
    return used


def parse_locale_list(raw: str) -> list[str]:
    """Turn ``"en, vi"`` into ``["en", "vi"]``, preserving order and de-duping."""
    languages: list[str] = []
    for chunk in raw.split(","):
        language = chunk.strip()
        if language and language not in languages:
            languages.append(language)
    return languages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero when a key used in code is missing from a gated locale",
    )
    parser.add_argument(
        "--strict-locales",
        default=DEFAULT_STRICT_LOCALES,
        help=(
            "comma-separated locales that must define every used key "
            f"(default: {DEFAULT_STRICT_LOCALES})"
        ),
    )
    parser.add_argument(
        "--min-coverage",
        type=float,
        default=0.0,
        metavar="PERCENT",
        help=(
            "with --check, fail when any locale defines fewer than PERCENT of "
            "the keys used in code (default: 0.0, i.e. no floor)"
        ),
    )
    args = parser.parse_args(argv)

    strict_locales = parse_locale_list(args.strict_locales)
    languages = supported_languages()
    unknown = [language for language in strict_locales if language not in languages]
    if unknown:
        parser.error(
            f"unknown strict locale(s): {', '.join(unknown)}; "
            f"available: {', '.join(languages)}"
        )

    strings = {lang: load_locale(lang) for lang in languages}
    english = strings.get("en", {})
    used = keys_used_in_code()
    missing_english = sorted(used - set(english))

    # how much of the code's vocabulary each locale actually defines
    used_coverage = {
        lang: 100.0 if not used else 100.0 * len(used & set(strings[lang])) / len(used)
        for lang in languages
    }

    print(f"{'locale':8} {'keys':>5} {'missing':>8} {'extra':>6} {'coverage':>9}")
    for lang in languages:
        table = strings[lang]
        missing = len(set(english) - set(table))
        extra = len(set(table) - set(english))
        coverage = 100.0 if not english else 100.0 * len(set(table) & set(english)) / len(english)
        print(f"{lang:8} {len(table):5d} {missing:8d} {extra:6d} {coverage:8.1f}%")

    if args.min_coverage > 0:
        print(f"\nused-key coverage (minimum {args.min_coverage:.1f}%):")
        for lang in languages:
            pct = used_coverage[lang]
            status = "OK" if pct >= args.min_coverage else "LOW"
            print(f"  {lang:8} {pct:6.1f}%  {status}")

    print(f"\nkeys used in code : {len(used)}")
    print(f"keys defined in en: {len(english)}")
    print(f"used but missing in en: {len(missing_english)}")
    for key in missing_english:
        print(f"  - {key}")

    strict_gaps: dict[str, list[str]] = {}
    print(f"\nstrict locales ({', '.join(strict_locales)}):")
    for lang in strict_locales:
        missing = sorted(used - set(strings[lang]))
        strict_gaps[lang] = missing
        status = "OK" if not missing else f"{len(missing)} missing"
        print(f"  {lang:8} {len(used) - len(missing):5d}/{len(used):<5d} used keys  {status}")
        for key in missing:
            print(f"    - {key}")

    below_floor = [lang for lang in languages if used_coverage[lang] < args.min_coverage]

    if args.check and (missing_english or any(strict_gaps.values()) or below_floor):
        if missing_english:
            print("\nFAIL: every get_text() key must exist in locales/en.json", file=sys.stderr)
        for lang, missing in strict_gaps.items():
            if missing:
                print(
                    f"FAIL: {lang}.json is missing {len(missing)} key(s) used in code",
                    file=sys.stderr,
                )
        for lang in below_floor:
            print(
                f"FAIL: {lang}.json covers {used_coverage[lang]:.1f}% of the keys used in code "
                f"(minimum {args.min_coverage:.1f}%)",
                file=sys.stderr,
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
