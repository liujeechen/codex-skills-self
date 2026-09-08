# DL/T 376.1 协议知识库

本目录用于识别、定位、校验和逐字段解析 376.1 报文。规则分为两个 profile，解帧前必须先选 profile，禁止混用：

- `standard-2009`：以正式 PDF《Q/GDW 376.1—2009》为主证据。
- `revision-2012-2013`：以《376.1主站通信协议--13比对.doc》中的修订内容为证据。文档封面写作 Q/GDW 376.1—2012，厂站扩展文档则引用 Q/GDW 1376.1—2013，因此本库不把二者擅自视为完全相同版本。
- `station-2.0-v1.6`：在 `revision-2012-2013` 基础上启用《厂站终端2.0扩展协议》V1.6 的 AFN/Fn 扩展。

## 证据代号

| 代号 | 文件 | 定位方式 | 角色 |
|---|---|---|---|
| S2009-PDF | `376.1-2009…带索引目录.pdf` | 章、节、表、PDF页 | 正式2009版，标准帧规则的首要依据 |
| S2009-DOC | `Q／GDW 376.1.doc` | 章、节、表 | 2009版可编辑稿，用于表格文字交叉校验；封面发布日期有占位符，权威性低于PDF |
| REV13-DOC | `376.1主站通信协议--13比对.doc` | 章、节、表 | 2012/2013修订比对资料，包含安全认证、新Fn和事件扩展 |
| EXT-V1.6 | `厂站终端2.0维护扩展协议-修改.docx` | 3.x节、表、版本记录 | 厂站终端2.0私有扩展，定义F796、F816～F821、F792、F794和AFN=FE |

## 强制使用规则

1. 先按 [decode_procedure.md](decode_procedure.md) 找帧和校验，再解释业务。
2. 每个结论标注 profile；未选 profile 时只输出标准公共部分。
3. 标准文档没有定义的字节不得套用645、698、376.2或IEC定义。
4. 无证据的解释必须标记 `【推测】`；完全无依据时写“当前提供的协议资料中未找到该字段定义”。
5. 业务体长度必须由“方向 + AFN + Fn + Pn + profile”共同确定，不能仅凭剩余字节猜测。

## 文件导航

- [frame_structure.md](frame_structure.md)：帧边界、L和字节偏移。
- [control_field.md](control_field.md)：控制域C与链路服务。
- [address_field.md](address_field.md)：地址域A。
- [afn.md](afn.md)：AFN注册表。
- [seq.md](seq.md)：SEQ、多帧和重发。
- [da_dt.md](da_dt.md)：DA/DT算法与特殊值。
- [data_units.md](data_units.md)：数据单元解析规则及关键结构。
- [fn_catalog.md](fn_catalog.md)：2009与修订资料的完整AFN/Fn名称索引。
- [data_formats.md](data_formats.md)：BCD、时间和附录A格式。
- [checksum.md](checksum.md)：CS和完整性检查。
- [special_cases.md](special_cases.md)：AUX、前导码、多服务和异常处理。
- [document_conflicts.md](document_conflicts.md)：版本冲突和未定义项。
- [examples.md](examples.md)：逐字节示例。
- [decode_procedure.md](decode_procedure.md)：强制解帧流程和输出格式。
- [sources/](sources/README.md)：四份原文的完整可检索文本、文件指纹及扩展文档中的嵌入图，用于回溯逐字段表。
