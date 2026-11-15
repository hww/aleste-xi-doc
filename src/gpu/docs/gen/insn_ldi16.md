**J=0 I=1 LDI16**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | = 0 |
| <a id="I"></a>**I** | [29] | 1 | = 1 |
| <a id="COND"></a>**COND** | [28:25] | 4 | Condition [`conditions`](conditions.md) |
| <a id="WRITE"></a>**WRITE** | [24] | 1 | Unused for LDI, must be 1 |
| <a id="F"></a>**F** | [23] | 1 | Unused for LDI, must be 0 |
| <a id="DST_CODE"></a>**DST_CODE** | [22:17] | 6 | Destination operand (6 bits) [`operand_map`](operand_map.md) |
| <a id="RSV"></a>**RSV** | [16] | 1 | Reserved, must be 0 |
| <a id="IMM16"></a>**IMM16** | [15:0] | 16 | 16-bit constant |
