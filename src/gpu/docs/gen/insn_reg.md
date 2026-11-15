**J=0 I=0 REG-REG**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | = 0 |
| <a id="I"></a>**I** | [29] | 1 | = 0 |
| <a id="DST_CODE"></a>**DST_CODE** | [28:23] | 6 | Destination operand (6 bits) [`operand_map`](operand_map.md) |
| <a id="WRITE"></a>**WRITE** | [22] | 1 | 1 = write result; 0 = do not write (flags still update if F=1) |
| <a id="COND"></a>**COND** | [21:18] | 4 | Condition [`conditions`](conditions.md) |
| <a id="F"></a>**F** | [17] | 1 | 1 = update flags |
| <a id="OP"></a>**OP** | [16:12] | 5 | ALU operation [`alu_ops`](alu_ops.md) |
| <a id="SRC"></a>**SRC** | [11:6] | 6 | Second operand (6 bits) [`operand_map`](operand_map.md) |
| <a id="RSV"></a>**RSV** | [5:0] | 6 | Reserved, must be 0 |
