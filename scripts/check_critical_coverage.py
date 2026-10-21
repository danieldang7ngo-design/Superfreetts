#!/usr/bin/env python3
"""Fail CI when a security- or data-critical module drops below 70% coverage.

The overall project coverage is still being raised incrementally, so it is
tracked separately.  This gate protects the modules where an untested branch
can lose user data, bypass a safety check, or corrupt configuration/audio
state.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CRITICAL_MODULES = {
    "superfreetts_addon/config_models.py": 70.0,
    "superfreetts_addon/batch_executor.py": 70.0,
    "superfreetts_addon/component_text_processing.py": 70.0,
    "superfreetts_addon/audio_file_store.py": 70.0,
    "superfreetts_addon/voice_cache.py": 70.0,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "coverage_json",
        nargs="?",
        default="coverage.json",
        help="Path to the coverage.py JSON report",
    )
    args = parser.parse_args()

    report_path = Path(args.coverage_json)
    if not report_path.is_file():
        print(f"coverage report not found: {report_path}", file=sys.stderr)
        return 2

    report = json.loads(report_path.read_text(encoding="utf-8"))
    files = report.get("files", {})
    failures = []
    print("Critical-module coverage (minimum 70%):")
    for module, minimum in CRITICAL_MODULES.items():
        summary = files.get(module, {}).get("summary")
        if not summary:
            failures.append(f"{module}: missing from coverage report")
            print(f"  MISSING  {module}")
            continue
        actual = float(summary.get("percent_covered", 0.0))
        status = "ok" if actual >= minimum else "FAIL"
        print(f"  {status:4}  {actual:5.1f}%  {module}")
        if actual < minimum:
            failures.append(f"{module}: {actual:.1f}% < {minimum:.1f}%")

    if failures:
        print("\nCritical coverage failures:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
