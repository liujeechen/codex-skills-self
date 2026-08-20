---
name: self-test-report
description: Generate or revise Chinese software self-test reports in genuine DOCX format from Git commits, code diffs, requirements, or described changes. Use when the user asks for a self-test report, test report based on a commit, report using their personal template, or invokes $self-test-report.
---

# Self-Test Report

Generate a complete Chinese self-test report from the actual change while preserving the user's Word template.

## Workflow

1. Resolve the requested commit. If none is specified, use the latest commit.
2. Inspect the commit message, changed files, diff, related call paths, data formats, boundaries, and regression scope.
3. Copy `assets/program-self-test-template.docx` to the repository `docs/` directory. Never modify the asset.
4. Replace template example content while retaining its package parts, styles, numbering, page layout, and five-column conclusion table.
5. Adapt section content and test-case count to the actual change. Do not preserve irrelevant example chapters.
6. Run `scripts/normalize_and_validate.py <output.docx>`.
7. Report the output path and validation result.

## Required Structure

Keep these four top-level sections from the template:

- 修改说明
- 自测结论
- 自测方案
- 自测记录

Choose and retain only the applicable change category: 新增功能, 缺陷修复, or 代码优化及重构. Fill the required subitems for that category.

The conclusion table must retain these columns:

- 测试模块
- 测试方案
- 测试用例
- 测试结果
- 备注说明

Keep every cell in the 测试结果 column empty. In each detailed test record, keep 测试结果 and 报文/截图记录 empty for manual entry.

## Content Rules

- Derive content from code evidence. Do not invent executed test results.
- Complete the change description, requirement or defect interpretation, root cause when applicable, implementation impact, test approach, test type, acceptance criteria, prerequisites, steps, and expected results.
- Cover normal flows, boundaries, failure paths, configuration persistence, protocol length/count/checksum effects, compatibility, and regression scope when relevant.
- Include the commit hash and subject near the start of the report.
- Use concise, executable test steps suitable for device-screen, serial-port, packet-capture, or log-based verification as applicable.

## Formatting Rules

- Output a genuine `.docx`, never HTML renamed as `.doc` or `.docx`.
- Force all visible text to pure black `#000000`.
- Keep body text regular, never bold.
- Set body paragraphs to a two-Chinese-character first-line indent (`w:firstLineChars="200"`).
- Keep title, top-level headings, subsection headings, field labels, and the table header bold when inherited from the template.
- The template supplies automatic numbering. Top-level heading text must be exactly `修改说明`, `自测结论`, `自测方案`, and `自测记录`; do not prefix `一、`, `二、`, `三、`, or `四、` manually.
- Preserve ordinary professional report styling. Do not add decorative colors or elaborate tables.

## Validation

Run:

```bash
python3 scripts/normalize_and_validate.py /absolute/path/to/report.docx
```

Treat any nonzero exit as a report-generation failure. Fix the document and rerun validation before returning it.
