# CS与完整性校验

CS是用户数据区所有字节的8位算术和，不考虑进位：

```text
user_start = frame_start + 6          # C
user_end_exclusive = user_start + L1
calculated_cs = sum(buf[user_start:user_end_exclusive]) & 0xFF
received_cs = buf[frame_start + L1 + 6]
```

用户数据区包括：C、A、AFN、SEQ、全部数据单元和AUX。CS不包括任何68、L、CS本身、16，也不包括红外FE前导码。

来源：S2009-PDF 4.3.2、4.3.3.4；REV13-DOC 4.3.2、4.3.3.4。

## 完整性检查顺序

1. 第一启动字符为68。
2. 两份L完全相同。
3. L低2位为当前profile允许的协议标识。
4. 第二启动字符为68。
5. 已接收字节数至少为 `L1+8`。
6. 计算CS与收到的CS一致。
7. 最后一个字节为16。
8. 再进行C/A/AFN/SEQ/DA/DT和业务体语义检查。

结构检查与语义检查应分开报告。CS正确只能证明传输字节的加和一致，不能证明AFN/Fn、BCD、地址或数据长度合法。

## 流式接收状态

- 尚未收到 `L1+8`：`截断/等待更多字节`，不能报CS错误。
- 已有完整候选但结束符错误：`结构错误`。
- 结束符正确但CS错误：`校验错误`。
- 候选后仍有字节：当前帧结束于 `start+L1+8`，剩余字节继续找下一帧。
