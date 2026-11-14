# J=1 I=1 REG-IMM11

![J=1 I=1 REG-IMM11](gen/insn_imm11.svg)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | = 1 |
| <a id="I"></a>**I** | [29] | 1 | = 1 |
| <a id="DST_CODE"></a>**DST_CODE** | [28:23] | 6 | Destination operand (6 bits) [`operand_map`](gen/operand_map.md) |
| <a id="WRITE"></a>**WRITE** | [22] | 1 | 1 = write result; 0 = do not write |
| <a id="COND"></a>**COND** | [21:18] | 4 | Condition [`conditions`](gen/conditions.md) |
| <a id="F"></a>**F** | [17] | 1 | Update flags |
| <a id="OP"></a>**OP** | [16:12] | 5 | ALU operation [`alu_ops`](gen/alu_ops.md) |
| <a id="SX"></a>**SX** | [11] | 1 | 1 = sign-extend IMM11, 0 = zero-extend |
| <a id="IMM"></a>**IMM** | [10:0] | 11 | 11-bit immediate, operand B |
