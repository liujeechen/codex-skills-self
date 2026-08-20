#!/usr/bin/env python3
"""Read-only structural inspector for Q/GDW/DL/T 376.1-style frames.

Business schemas deliberately remain in the project's protocol knowledge base.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any


def normalize_hex(text: str) -> bytes:
    cleaned = re.sub(r"0[xX]", "", text)
    cleaned = re.sub(r"[\s,:;_\-]", "", cleaned)
    if not cleaned:
        raise ValueError("empty hexadecimal input")
    if re.search(r"[^0-9a-fA-F]", cleaned):
        raise ValueError("input contains non-hexadecimal characters")
    if len(cleaned) % 2:
        raise ValueError("input contains an odd number of hexadecimal nibbles")
    return bytes.fromhex(cleaned)


def hex_bytes(data: bytes) -> str:
    return " ".join(f"{byte:02X}" for byte in data)


def decode_bcd_area(raw: bytes) -> dict[str, Any]:
    valid = all(((byte >> 4) <= 9 and (byte & 0x0F) <= 9) for byte in raw)
    value = None
    if valid:
        value = f"{raw[1] >> 4}{raw[1] & 0x0F}{raw[0] >> 4}{raw[0] & 0x0F}"
    return {"raw": hex_bytes(raw), "valid_bcd": valid, "value": value}


def expand_da(da1: int, da2: int) -> dict[str, Any]:
    raw = f"{da1:02X} {da2:02X}"
    if da1 == 0 and da2 == 0:
        return {"raw": raw, "kind": "P0", "points": [0]}
    if da1 == 0xFF and da2 == 0:
        return {"raw": raw, "kind": "all-valid-points", "points": []}
    if da2 == 0 or da1 == 0:
        return {"raw": raw, "kind": "undefined", "points": []}
    points = [(da2 - 1) * 8 + bit + 1 for bit in range(8) if da1 & (1 << bit)]
    return {"raw": raw, "kind": "bitmap", "points": points}


def expand_dt(dt1: int, dt2: int) -> dict[str, Any]:
    functions = [dt2 * 8 + bit + 1 for bit in range(8) if dt1 & (1 << bit)]
    return {
        "raw": f"{dt1:02X} {dt2:02X}",
        "functions": functions,
        "standard_group": dt2 <= 30,
        "empty": dt1 == 0,
    }


def inspect_candidate(stream: bytes, start: int) -> dict[str, Any]:
    remaining = len(stream) - start
    result: dict[str, Any] = {"stream_offset": start, "available_bytes": remaining}
    if remaining < 6:
        result.update({"status": "truncated-header", "missing_for_header": 6 - remaining})
        return result

    l_first = int.from_bytes(stream[start + 1 : start + 3], "little")
    l_second = int.from_bytes(stream[start + 3 : start + 5], "little")
    l1 = l_first >> 2
    frame_size = l1 + 8
    result.update(
        {
            "lraw": l_first,
            "lraw_hex": f"0x{l_first:04X}",
            "protocol_id": l_first & 0x03,
            "l1": l1,
            "frame_size": frame_size,
            "length_copy_matches": l_first == l_second,
            "second_start_valid": stream[start + 5] == 0x68,
        }
    )
    if remaining < frame_size:
        result.update({"status": "truncated-frame", "missing_bytes": frame_size - remaining})
        return result

    frame = stream[start : start + frame_size]
    result["end_stream_offset_exclusive"] = start + frame_size
    result["raw"] = hex_bytes(frame)
    result["end_valid"] = frame[-1] == 0x16
    received_cs = frame[-2]
    calculated_cs = sum(frame[6 : 6 + l1]) & 0xFF
    result["checksum"] = {
        "received": f"0x{received_cs:02X}",
        "calculated": f"0x{calculated_cs:02X}",
        "valid": received_cs == calculated_cs,
        "range": [6, 6 + l1 - 1],
    }

    warnings: list[str] = []
    if l_first != l_second:
        warnings.append("the two L fields differ")
    if stream[start + 5] != 0x68:
        warnings.append("second start character is not 68")
    if (l_first & 0x03) != 2:
        warnings.append("protocol_id is not 2")
    if frame[-1] != 0x16:
        warnings.append("end character is not 16")
    if received_cs != calculated_cs:
        warnings.append("checksum mismatch")
    if l1 < 8:
        warnings.append("L1 is shorter than the fixed C+A+AFN+SEQ fields")

    if l1 >= 8:
        control = frame[6]
        direction_up = bool(control & 0x80)
        prm = bool(control & 0x40)
        result["control"] = {
            "raw": f"0x{control:02X}",
            "DIR": int(direction_up),
            "direction": "terminal-to-master" if direction_up else "master-to-terminal",
            "PRM": int(prm),
            "D5": int(bool(control & 0x20)),
            "D5_name": "ACD" if direction_up else "FCB",
            "D4": int(bool(control & 0x10)),
            "D4_name": "reserved" if direction_up else "FCV",
            "FUNC": control & 0x0F,
        }
        address = frame[7:12]
        a1 = decode_bcd_area(address[:2])
        a2 = int.from_bytes(address[2:4], "little")
        group = address[4] & 1
        result["address"] = {
            "A1": a1,
            "A2": a2,
            "A2_raw": hex_bytes(address[2:4]),
            "group": group,
            "MSA": address[4] >> 1,
            "A3_raw": f"{address[4]:02X}",
        }
        semantic_warnings: list[str] = []
        if not a1["valid_bcd"]:
            semantic_warnings.append("A1 administrative-area BCD is invalid")
        if a2 == 0:
            semantic_warnings.append("A2 is the invalid zero address")
        if a2 == 0xFFFF and group != 1:
            semantic_warnings.append("A2=FFFF is not a system broadcast because A3.group is 0")
        if direction_up and control & 0x10:
            semantic_warnings.append("upstream C.D4 reserved bit is nonzero")
        if semantic_warnings:
            result["semantic_warnings"] = semantic_warnings
        result["AFN"] = f"0x{frame[12]:02X}"
        seq = frame[13]
        result["SEQ"] = {
            "raw": f"0x{seq:02X}",
            "TpV": (seq >> 7) & 1,
            "FIR": (seq >> 6) & 1,
            "FIN": (seq >> 5) & 1,
            "CON": (seq >> 4) & 1,
            "PSEQ_or_RSEQ": seq & 0x0F,
        }
        if l1 >= 12:
            result["first_DA"] = expand_da(frame[14], frame[15])
            result["first_DT"] = expand_dt(frame[16], frame[17])

        aux_end = len(frame) - 2
        aux: dict[str, Any] = {}
        if seq & 0x80 and aux_end >= 20:
            aux["Tp_candidate_offset"] = aux_end - 6
            aux["Tp_candidate_raw"] = hex_bytes(frame[aux_end - 6 : aux_end])
            aux_end -= 6
        if direction_up and control & 0x20 and aux_end >= 16:
            aux["EC_candidate_offset"] = aux_end - 2
            aux["EC_candidate_raw"] = hex_bytes(frame[aux_end - 2 : aux_end])
            aux_end -= 2
        if aux:
            aux["note"] = "Candidate boundaries from SEQ.TpV/C.ACD; confirm against the selected schema."
            result["AUX_candidates"] = aux
        if l1 >= 12:
            result["bytes_after_first_selector_before_aux_candidates_raw"] = hex_bytes(frame[18:aux_end])

    result["warnings"] = warnings
    result["status"] = "complete-valid" if not warnings else "complete-abnormal"
    return result


def find_candidates(stream: bytes) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    cursor = 0
    while cursor < len(stream):
        try:
            start = stream.index(0x68, cursor)
        except ValueError:
            break
        candidate = inspect_candidate(stream, start)
        results.append(candidate)
        if candidate.get("status") == "complete-valid":
            cursor = int(candidate["end_stream_offset_exclusive"])
        elif candidate.get("status", "").startswith("truncated") and candidate.get("length_copy_matches") and candidate.get("second_start_valid"):
            break
        else:
            cursor = start + 1
    return results


def print_human(stream: bytes, candidates: list[dict[str, Any]]) -> None:
    print(f"Input bytes: {len(stream)}")
    print(f"Normalized: {hex_bytes(stream)}")
    if not candidates:
        print("No 68 frame candidate found.")
        return
    for number, item in enumerate(candidates, 1):
        print(f"\nCandidate {number} at stream offset {item['stream_offset']}: {item['status']}")
        for key in ("lraw_hex", "protocol_id", "l1", "frame_size", "length_copy_matches", "second_start_valid"):
            if key in item:
                print(f"  {key}: {item[key]}")
        if "missing_bytes" in item:
            print(f"  missing_bytes: {item['missing_bytes']}")
        for key in ("control", "address", "AFN", "SEQ", "first_DA", "first_DT", "AUX_candidates", "checksum"):
            if key in item:
                print(f"  {key}: {json.dumps(item[key], ensure_ascii=False)}")
        if "end_valid" in item:
            print(f"  end_valid: {item['end_valid']}")
        for warning in item.get("warnings", []):
            print(f"  WARNING: {warning}")
        for warning in item.get("semantic_warnings", []):
            print(f"  SEMANTIC WARNING: {warning}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hex_stream", nargs="?", help="Hex bytes; stdin is used when omitted")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()
    text = args.hex_stream if args.hex_stream is not None else sys.stdin.read()
    try:
        stream = normalize_hex(text)
    except ValueError as error:
        print(f"Input error: {error}", file=sys.stderr)
        return 2
    candidates = find_candidates(stream)
    if args.json:
        print(json.dumps({"input_length": len(stream), "candidates": candidates}, ensure_ascii=False, indent=2))
    else:
        print_human(stream, candidates)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
