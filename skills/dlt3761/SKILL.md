---
name: dlt3761
description: Stable DL/T 376.1-compatible protocol analysis for hexadecimal streams, including frame discovery, L-based segmentation, integrity and CS checks, bytewise decoding of C/A/AFN/SEQ/DA/DT, Pn/Fn calculation, application-unit lookup, AUX/time-tag handling, anomaly diagnosis, real-frame calibration, and protocol-aware code review. Use for requests to identify, decode, validate, troubleshoot, compare, or implement project 376.1 frames, including the Q/GDW 376.1 profiles and station 2.0 private extensions such as F819.
---

# dlt3761

Use the project's existing knowledge base as the single maintained protocol-rule source. Apply a deterministic structural check first, then load only the references required for the selected AFN/Fn. Never silently fill gaps from model memory or a different power protocol.

## Locate the knowledge base

Read [references/knowledge-routing.md](references/knowledge-routing.md) first. Resolve the knowledge root and selected profile before interpreting version-dependent fields.

Treat “DL/T 376.1” as the user-facing project name. Preserve the source documents' actual standard identifiers in evidence: the current documents include Q/GDW 376.1—2009, revision comparison material, and a station 2.0 private extension. Do not call F819 a standard 376.1 Fn.

## Choose the operation

- For “解帧/解析/什么意思/是否合法”: run the complete decode workflow and produce the bytewise output contract.
- For a continuous stream or suspected sticky/partial packets: discover every candidate, segment by L, and report leading/trailing noise and truncated candidates separately.
- For an unknown or disputed meaning: backtrack through evidence and confidence rules; do not force a complete business interpretation.
- For code diagnosis: compare protocol rule, actual bytes, and code behavior. Do not edit code unless the user explicitly asks for implementation.
- For an explicit correction based on a real device: execute the calibration workflow before changing a rule or promoting a case.

## Decode workflow

Follow this sequence without skipping ahead because a business meaning appears familiar:

1. Preserve the raw input, normalize separators and `0x` prefixes, and reject non-hex or odd-nibble input.
2. Scan bytewise for `68`; treat 1–4 preceding `FE` bytes only as possible infrared preamble.
3. Read both little-endian L copies and require exact equality.
4. Calculate `Lraw`, `protocol_id = Lraw & 3`, `L1 = Lraw >> 2`, and `frame_size = L1 + 8`.
5. Use `frame_size` to determine the candidate boundary. If bytes are missing, report the exact deficit and do not claim a CS failure.
6. Validate the second `68` at offset 5.
7. Decode C bitwise: DIR, PRM, FCB/ACD, FCV/reserved, FUNC. Derive direction from DIR only.
8. Decode A: A1 BCD legality/value, A2 little-endian address, A3 group flag and MSA.
9. Decode AFN and its profile registration state.
10. Decode SEQ: TpV, FIR, FIN, CON, PSEQ/RSEQ.
11. Identify tail AUX candidates before consuming application units: Tp from TpV, upstream EC from ACD, and PW only from the selected schema.
12. Decode each DA bitmap, including P0 and all-valid-points special values; calculate every selected Pn.
13. Decode each DT bitmap and calculate every selected Fn. Never keep only the lowest set bit.
14. Lookup the schema by at least `(profile, direction, AFN, Fn, Pn-kind)` and consume exactly its declared bytes.
15. Repeat for multiple data units in Pn-ascending then Fn-ascending order. Stop when an unknown variable-length schema makes the next boundary unknowable.
16. Decode AUX/PW/EC/Tp details from the boundaries justified above.
17. Calculate CS over exactly the L1 bytes beginning at C, compare received CS, then validate final `16` separately.
18. Summarize direction, link role, AFN/Fn, business meaning, completeness, integrity, anomalies, evidence, profile, and confidence.

For deterministic Steps 1–13 and 17, prefer:

```bash
python3 scripts/inspect_frame.py '<hex stream>'
```

Use `--json` when machine-readable structural results are helpful. The script intentionally does not own AFN/Fn business schemas; continue with the knowledge base.

## Load references progressively

Do not load the complete knowledge base or all original documents for every frame.

1. Always load `decode_procedure.md` plus only the common-field files needed for the request.
2. After AFN/Fn is known, load `afn.md`, `fn_catalog.md`, and the relevant section of `data_units.md`.
3. Load `special_cases.md` only when AUX, multiple units, multiple frames, missing data, broadcast, or abnormal framing is involved.
4. Load `document_conflicts.md` when selecting a profile, encountering a private/high Fn, or seeing conflicting results.
5. Search the extracted source text by AFN/Fn, section, or table only when ambiguity, contradiction, user challenge, or unexplained data requires an original-source check.
6. Open the original PDF/DOC/DOCX location when extracted text may have lost table layout or the user requests source verification.

Never use the whole `fn_catalog.md` if a targeted search such as `rg -n 'AFN=0A|F819'` is enough.

## Apply evidence and uncertainty rules

Read [references/evidence-and-calibration.md](references/evidence-and-calibration.md) whenever a conclusion is disputed, an unknown field appears, or a real-frame correction is supplied.

Use these labels on important conclusions:

- `已确认`: original text is explicit and the applicable knowledge rule is unambiguous.
- `基本确认`: protocol evidence is clear but real-frame coverage remains limited.
- `待验证`: a rule or interpretation exists but lacks sufficient source or real-frame confirmation.
- `存疑`: the frame conflicts with the selected rule/profile or sources disagree.

If the provided materials do not define a field, write exactly: `当前协议资料中未确认该字段定义。`

Use `【待验证】` for evidence-backed but insufficiently validated claims and `【推测】` only for contextual hypotheses. Keep hypotheses separate from protocol facts. Never import definitions from DL/T 645, DL/T 698, DL/T 376.2, IEC protocols, or unrelated vendor protocols.

## Produce bytewise output

Read [references/output-contract.md](references/output-contract.md) for the required table and conclusion block. Default to a row for every field and every business subfield, with zero-based offsets, original bytes, calculated values, and anomalies.

Always show the calculations for L, Pn, Fn, and CS. Separate:

- structural integrity from business legality;
- received facts from inferred meaning;
- standard rules from station/regional/vendor extensions;
- complete frames, truncated candidates, invalid candidates, and unknown frames.

## Analyze protocol code safely

Read [references/code-analysis.md](references/code-analysis.md) before investigating an implementation.

Trace bytes through frame search, length conversion, fixed fields, schema dispatch, variable-length bounds, AUX stripping, and CS. Compare encoding and decoding symmetrically. Report evidence and a proposed fix first for diagnosis-only requests. Modify business code only when explicitly authorized, and verify against regression cases afterward.

## Calibrate with real frames

When the user explicitly confirms a real result:

1. Reproduce the old result and isolate the first wrong decision.
2. Recheck the applicable original section/table and knowledge rule.
3. Classify the cause as workflow error, knowledge error, missing knowledge, special version, regional/vendor extension, implementation difference, or malformed frame.
4. Update the existing project knowledge file if and only if its rule is wrong or incomplete; do not copy the correction into SKILL.md as a competing rule.
5. Update this workflow only if the workflow caused the error.
6. Add or promote a case under `tests/cases.json`, recording source, evidence, expected fields, and validation status.
7. Run `tests/run_regression.py` and ensure existing confirmed cases do not regress.

A single device observation never overrides an explicit standard rule. Record conflicts as a scoped implementation/version extension until corroborated.

## Regression cases

Use `tests/cases.json` as the case registry. Only entries with `validation_status: 已人工确认` are strong regression evidence. Treat `未人工确认`, `规则构造`, and `存疑` entries as structural exercises or investigation leads, never as authority over source documents.

Run:

```bash
python3 tests/run_regression.py
```

Keep raw captures immutable inside a case; add corrected expectations and evidence instead of rewriting history without explanation.
