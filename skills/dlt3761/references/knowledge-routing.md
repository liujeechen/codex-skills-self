# Knowledge routing

## Resolve the single source of truth

Use this project knowledge root:

```text
/home/STR3_260804/tops_devp_station_II/docs/376_1_knowledge
```

When working from a checkout that may have moved, locate `docs/376_1_knowledge/README.md` with `rg --files` and use that directory instead. If no knowledge root is available, say so and restrict output to deterministic structural facts; do not reconstruct a second knowledge base from memory.

The Skill must reference these project files in place. Do not copy their protocol tables into the Skill.

## Route by question

| Need | Load from the knowledge root |
|---|---|
| Start, L, boundary, byte offsets | `frame_structure.md` |
| C bits, FUNC, FCB/ACD/FCV | `control_field.md` |
| A1/A2/A3, broadcast, MSA | `address_field.md` |
| AFN name/direction | `afn.md` |
| SEQ, FIR/FIN, PSEQ/RSEQ | `seq.md` |
| DA/DT, Pn/Fn algorithms | `da_dt.md` |
| AFN/Fn names | targeted section of `fn_catalog.md` |
| Application schema | targeted section of `data_units.md` |
| BCD, time, appendix formats | `data_formats.md` |
| CS | `checksum.md` |
| AUX/PW/EC/Tp, multi-unit/frame | `special_cases.md` |
| Version/private-extension conflict | `document_conflicts.md` |
| Canonical procedure/output | `decode_procedure.md` |
| Existing examples | `examples.md` |
| Evidence IDs and source hashes | `sources/README.md` |

## Profiles

- `standard-2009`: formal Q/GDW 376.1—2009 PDF is primary.
- `revision-2012-2013`: revision comparison DOC; do not assume it is identical to Q/GDW 1376.1—2013.
- `station-2.0-v1.6`: revision-family common layer plus the station 2.0 private extension, including F819.

If the profile is unspecified, decode only the common layer first and present version-dependent interpretations side by side. High Fn values above F248 require an explicit extension profile.

## Original protocol documents

Use these as final protocol evidence when mounted:

```text
/media/sf_VM_Share_2404/3761协议/376.1-2009《电力用户用电信息采集系统_通信协议：主站与采集终端》_带索引目录.pdf
/media/sf_VM_Share_2404/3761协议/Q／GDW 376.1.doc
/media/sf_VM_Share_2404/3761协议/376.1主站通信协议--13比对.doc
/media/sf_VM_Share_2404/3761协议/厂站终端2.0维护扩展协议-修改.docx
```

Searchable full-text extracts live under `sources/` in the knowledge root. Use them for fast section lookup, then inspect the original document when merged cells, figures, pagination, or table layout could change the meaning. Verify source identity against `sources/README.md` hashes before treating a replaced file as the same evidence.

## Operational versus evidentiary priority

For normal decoding, query the compact knowledge files first to minimize context. For deciding which definition is authoritative, use:

1. applicable original protocol document;
2. current project knowledge rule;
3. human-confirmed real-frame case;
4. model memory only as a search clue.

This distinction allows efficient operation without weakening the original documents' authority.
