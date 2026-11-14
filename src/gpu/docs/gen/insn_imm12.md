# INSTRUCTION · 32 BIT · J=1 I=1 REG-IMM12 (d = d op imm)

![INSTRUCTION · 32 BIT · J=1 I=1 REG-IMM12 (d = d op imm)](gen/insn_imm12.svg)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | = 1 |
| <a id="I"></a>**I** | [29] | 1 | = 1 |
| <a id="DST"></a>**DST** | [28:24] | 5 | Destination operand, low 5 bits |
| <a id="DS"></a>**DS** | [23] | 1 | DST bank |
| <a id="COND"></a>**COND** | [22:19] | 4 | Condition [`conditions`](gen/conditions.md) |
| <a id="F"></a>**F** | [18] | 1 | Update flags |
| <a id="OP"></a>**OP** | [17:13] | 5 | ALU operation [`alu_ops`](gen/alu_ops.md) |
| <a id="SX"></a>**SX** | [12] | 1 | 1 = sign-extend IMM, 0 = zero-extend |
| <a id="IMM"></a>**IMM** | [11:0] | 12 | 12-bit immediate, operand B |
