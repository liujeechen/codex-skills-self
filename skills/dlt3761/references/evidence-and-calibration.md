# Evidence, confidence, and calibration

## Evidence record

For an important interpretation, retain:

- selected profile and direction;
- knowledge filename and heading;
- original document evidence ID, chapter/section/table when available;
- whether the result is direct, calculated, inferred, or unknown;
- confidence label;
- real-case validation status if relevant.

Do not cite an extracted text line as stronger evidence than its original PDF/DOC/DOCX. Extraction can lose table geometry.

## Conflict handling

When two definitions differ:

1. State definition A with its source/profile.
2. State definition B with its source/profile.
3. Describe the concrete difference in bytes, direction, length, or meaning.
4. Identify which is formal standard evidence and which is revision/private-extension evidence when the documents support that classification.
5. Do not choose silently. Use the capture context or user-selected profile to choose for this decode.

The supplied corpus does not prove that its Q/GDW texts are an official “DL/T 376.1” publication. Preserve the exact source standard number in evidence statements.

## Confidence labels

| Label | Use only when |
|---|---|
| 已确认 | Applicable original text and the knowledge rule are both explicit and consistent. |
| 基本确认 | Evidence is clear, calculation is deterministic, but real-device coverage is still limited. |
| 待验证 | A plausible project rule exists but source/detail or representative captures are insufficient. |
| 存疑 | Bytes, selected profile, knowledge files, or source documents conflict. |

CS success is not business confirmation. A real capture is not automatically human-confirmed. User-provided semantics become strong regression evidence only after explicit confirmation and source/profile review.

## Calibration workflow

For an explicit correction:

1. Save the raw frame and the user's stated ground truth without editing either.
2. Re-run structural inspection and record the old output.
3. Identify the earliest divergence: framing, profile, C/A, AFN/SEQ, DA/DT, schema length/order, AUX, checksum, or business mapping.
4. Check the original source and then the existing knowledge rule.
5. Classify root cause:
   - Skill workflow error;
   - knowledge rule error;
   - missing knowledge;
   - special protocol version;
   - regional/vendor extension;
   - engineering implementation difference;
   - malformed capture/frame.
6. Scope the correction. Never generalize a vendor observation into the standard profile without source evidence.
7. Update the one authoritative project knowledge file and its evidence/conflict entry when needed.
8. Update SKILL.md only for procedural faults.
9. Add/promote the case in `tests/cases.json` with `validation_status: 已人工确认`, who/what confirmed it, evidence, and expected structural fields.
10. Run all regressions and report any remaining version-dependent branch.

If the source remains unavailable or ambiguous, retain the observation as `待验证` or `存疑`; do not rewrite the standard rule.
