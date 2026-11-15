**J=1 I=0 CONTROL RJUMP (R=1: JMPR)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | = 1 |
| <a id="I"></a>**I** | [29] | 1 | = 0 |
| <a id="COND"></a>**COND** | [28:25] | 4 | Condition [`conditions`](conditions.md) |
| <a id="WRITE"></a>**WRITE** | [24] | 1 | Unused for CTRL, must be 0 |
| <a id="F"></a>**F** | [23] | 1 | Unused for CTRL (must be 0) |
| <a id="DST_CODE"></a>**DST_CODE** | [22:17] | 6 | Unused for CTRL [`operand_map`](operand_map.md) |
| <a id="R"></a>**R** | [16] | 1 | = 1 (register jump) |
| <a id="CTRL_OP"></a>**CTRL_OP** | [15:12] | 4 | = JMPR (register indirect jump) [`ctrl_ops`](ctrl_ops.md) |
| <a id="SRC"></a>**SRC** | [11:6] | 6 | Source operand code (0..63) [`operand_map`](operand_map.md) |
| <a id="RSV"></a>**RSV** | [5:0] | 6 | Unused, must be 0 |
