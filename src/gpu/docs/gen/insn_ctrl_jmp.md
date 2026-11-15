**J=1 I=0 CONTROL (R=0: JMP/CALL/RET/HALT/IRQ/FLUSH)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | = 1 |
| <a id="I"></a>**I** | [29] | 1 | = 0 |
| <a id="COND"></a>**COND** | [28:25] | 4 | Condition [`conditions`](conditions.md) |
| <a id="WRITE"></a>**WRITE** | [24] | 1 | Unused for CTRL, must be 0 |
| <a id="F"></a>**F** | [23] | 1 | Unused for CTRL (must be 0) |
| <a id="DST_CODE"></a>**DST_CODE** | [22:17] | 6 | Unused for CTRL [`operand_map`](operand_map.md) |
| <a id="R"></a>**R** | [16] | 1 | Jump/Call: 0 = by immediate, 1 = by source register |
| <a id="CTRL_OP"></a>**CTRL_OP** | [15:12] | 4 | Control operation [`ctrl_ops`](ctrl_ops.md) |
| <a id="ADDR"></a>**ADDR** | [11:0] | 12 | Target address (JMP/CALL), halt/IRQ code, channel (FLUSH) |
