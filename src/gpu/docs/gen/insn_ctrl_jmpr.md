# J=1 I=0 CTRL (JMPR)

![J=1 I=0 CTRL (JMPR)](gen/insn_ctrl_jmpr.svg)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | = 1 |
| <a id="I"></a>**I** | [29] | 1 | = 0 |
| <a id="DST_CODE"></a>**DST_CODE** | [28:23] | 6 | Source register for target address [`operand_map`](gen/operand_map.md) |
| <a id="WRITE"></a>**WRITE** | [22] | 1 | Unused |
| <a id="COND"></a>**COND** | [21:18] | 4 | Condition [`conditions`](gen/conditions.md) |
| <a id="F"></a>**F** | [17] | 1 | Unused |
| <a id="OP"></a>**OP** | [16:12] | 5 | = JMPR [`ctrl_ops`](gen/ctrl_ops.md) |
| <a id="REG"></a>**REG** | [11:6] | 6 | Source operand code (0..63) [`operand_map`](gen/operand_map.md) |
| <a id="RSV"></a>**RSV** | [5:0] | 6 | Unused |
