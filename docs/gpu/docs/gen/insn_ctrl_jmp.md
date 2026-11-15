**J=1 I=0 CTRL (JMP/CALL/RET/HALT/IRQ/FLUSH)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | = 1 |
| <a id="I"></a>**I** | [29] | 1 | = 0 |
| <a id="DST_CODE"></a>**DST_CODE** | [28:23] | 6 | Unused for non-JMPR CTRL [`operand_map`](operand_map.md) |
| <a id="WRITE"></a>**WRITE** | [22] | 1 | Unused for CTRL |
| <a id="COND"></a>**COND** | [21:18] | 4 | Condition [`conditions`](conditions.md) |
| <a id="F"></a>**F** | [17] | 1 | Unused for CTRL (must be 0) |
| <a id="OP"></a>**OP** | [16:12] | 5 | Control operation [`ctrl_ops`](ctrl_ops.md) |
| <a id="SX"></a>**SX** | [11] | 1 | Unused in CTRL |
| <a id="ADDR"></a>**ADDR** | [10:0] | 11 | Target address (JMP/CALL), halt/IRQ code, channel (FLUSH) |
