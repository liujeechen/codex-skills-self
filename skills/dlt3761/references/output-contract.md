# Bytewise decode output contract

Start with the normalized raw frame and profile. For a stream containing multiple candidates, number each candidate and show its start/end stream offsets.

Use a zero-based table:

```text
Offset  Bytes              Field       Result
------  -----------------  ----------  --------------------------------
0       68                 Start       first start character
1-2     LL HH              L#1         Lraw=..., protocol_id=..., L1=...
3-4     LL HH              L#2         matches/does not match
5       68                 Start       second start character
6       CC                 C           DIR=..., PRM=..., ...
7-11    ...                A           A1=..., A2=..., group=..., MSA=...
12      AF                 AFN         AFN=..., meaning/profile=...
13      SQ                 SEQ         TpV=..., FIR=..., FIN=..., CON=...
14-15   DA1 DA2            DA          P0/Pn list; show calculation
16-17   DT1 DT2            DT          Fn list; show calculation
...     ...                Data        field, encoding, value, unit
...     ...                AUX         PW/EC/Tp with justified boundary
n       CS                 CS          received=..., calculated=...
n+1     16                 End         valid/invalid
```

Do not collapse a multi-byte data object into one unexplained row. List its defined subfields. Preserve raw bytes for unknown and reserved fields.

## Required calculations

Show, as applicable:

```text
Lraw = L_low + (L_high << 8)
protocol_id = Lraw & 3
L1 = Lraw >> 2
frame_size = L1 + 8

Pn = (DA2 - 1) * 8 + bit_index + 1
Fn = DT2 * 8 + bit_index + 1

CS = sum(frame[C_offset : C_offset + L1]) & 0xFF
```

Special DA/DT values must be named from `da_dt.md`, not passed through the general formula.

## Conclusion block

Always finish with:

```text
帧方向：主站 -> 终端 / 终端 -> 主站
链路角色：...
AFN：...
Pn：...
Fn：...
业务含义：...
profile：...
校验：正确 / 错误 / 因截断无法校验
完整性：完整帧 / 截断帧 / 疑似异常帧 / 未识别
异常与未知：...
置信度：已确认 / 基本确认 / 待验证 / 存疑
证据：知识文件；原始文档章节/表；案例状态
```

When data is truncated, distinguish “field not present because the frame is short” from a legal absent optional field. When schema boundaries are unknown, stop byte assignment at the last proven boundary and label the remaining raw bytes; do not search for plausible DA/DT inside unknown data.
