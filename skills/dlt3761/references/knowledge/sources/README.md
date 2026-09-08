# 原始资料索引

本目录保存四份输入资料的完整可检索文本，以及扩展协议中无法由正文文本表达的嵌入图片。它们用于回溯规则证据，不替代原始文件的法律或发布效力。

| 代号 | 原始文件 | SHA-256 | 本目录提取物 |
|---|---|---|---|
| S2009-PDF | `376.1-2009《电力用户用电信息采集系统_通信协议：主站与采集终端》_带索引目录.pdf`，201页 | `f36b794591a9599a7784056db16c727a1245fcdb7d5ae19e39a394cca47b97f0` | `standard_2009_pdf.txt` |
| S2009-DOC | `Q／GDW 376.1.doc` | `25b6d4cff564d296b8e229b87eba754b2556cddbb046bcacf838baa2fd2c0c58` | `standard_2009_doc.txt` |
| REV13-DOC | `376.1主站通信协议--13比对.doc` | `bc8d787560c13b5ecc0a0b04e4f22664336de8b65e94071a5d86e1567ca9070a` | `revision_2012_13_compare_doc.txt` |
| EXT-V1.6 | `厂站终端2.0维护扩展协议-修改.docx` | `8d3232d8cf1cf71514c71eff6fc12f710cba89d38c94ef305f8d23d18899680c` | `station_2_0_extension_v1_6_docx.txt`、两张F817补充图 |

## 使用限制

- Word/PDF转为纯文本后，跨页表格、合并单元格和上下标可能失去视觉布局；字段结论应同时参考表名、上下文和原文图表。
- `standard_2009_pdf.txt`中的页分隔保留了PDF页序，可配合正式PDF复核；Word文档的页码会随排版环境变化，优先用章节、表号和Fn定位。
- 两份旧版DOC的图形化位域已尽量由相邻标题、表格文本和另一版本交叉校验；不能可靠还原的内容不会被知识库自动补全。
- EXT-V1.6中的两张嵌入图片已原样保存为`extension_f817_standard_notes_1.png`和`extension_f817_standard_notes_2.png`，其有效规则另见`../data_units.md`。
