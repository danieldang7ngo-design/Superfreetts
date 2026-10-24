#!/usr/bin/env python3
"""Report UI string coverage for every packaged locale.

The add-on falls back to English when a key is missing, and returns the raw key
when English is missing too - which is how ``mms_manager_error_installed`` and
``error_batch_stalled`` ended up visible in the UI.  This script makes that
class of mistake impossible to miss.

Usage:
    python scripts/i18n_audit.py            # human-readable report
    python scripts/i18n_audit.py --check    # exit 1 if a used key lacks English
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero when a key used in code has no English text",
    )
    args = parser.parse_args()

    languages = supported_languages()
    strings = {lang: load_locale(lang) for lang in languages}
    english = strings.get("en", {})
    used = keys_used_in_code()
    missing_english = sorted(used - set(english))

    print(f"{'locale':8} {'keys':>5} {'missing':>8} {'extra':>6} {'coverage':>9}")
    for lang in languages:
        table = strings[lang]
        missing = len(set(english) - set(table))
        extra = len(set(table) - set(english))
        coverage = 100.0 if not english else 100.0 * len(set(table) & set(english)) / len(english)
        print(f"{lang:8} {len(table):5d} {missing:8d} {extra:6d} {coverage:8.1f}%")

    print(f"\nkeys used in code : {len(used)}")
    print(f"keys defined in en: {len(english)}")
    print(f"used but missing in en: {len(missing_english)}")
    for key in missing_english:
        print(f"  - {key}")

    if args.check and missing_english:
        print("\nFAIL: every get_text() key must exist in locales/en.json", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
