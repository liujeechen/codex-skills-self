#!/usr/bin/env python3
"""Run deterministic structural expectations for registered dlt3761 cases."""

from __future__ import annotations

import json
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from inspect_frame import find_candidates, normalize_hex  # noqa: E402


def main() -> int:
    registry = json.loads((Path(__file__).with_name("cases.json")).read_text(encoding="utf-8"))
    failures: list[str] = []
    for case in registry["cases"]:
        candidates = find_candidates(normalize_hex(case["raw"]))
        if not candidates:
            failures.append(f"{case['id']}: no candidate")
            continue
        actual = candidates[0]
        expected = case["expected"]
        checks = {
            "status": actual.get("status"),
            "frame_size": actual.get("frame_size"),
            "l1": actual.get("l1"),
            "AFN": actual.get("AFN"),
            "Pn": actual.get("first_DA", {}).get("points"),
            "Fn": actual.get("first_DT", {}).get("functions"),
            "checksum_valid": actual.get("checksum", {}).get("valid"),
        }
        mismatches = [f"{key}: expected {value!r}, got {checks.get(key)!r}" for key, value in expected.items() if checks.get(key) != value]
        if mismatches:
            failures.append(f"{case['id']}: " + "; ".join(mismatches))
        else:
            print(f"PASS {case['id']} [{case['validation_status']}]")
    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1
    print(f"All {len(registry['cases'])} structural cases passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
