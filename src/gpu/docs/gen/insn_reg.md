# INSTRUCTION · 32 BIT · J=0 I=0 REG-REG (d = d op s)

![INSTRUCTION · 32 BIT · J=0 I=0 REG-REG (d = d op s)](gen/insn_reg.svg)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | = 0 |
| <a id="I"></a>**I** | [29] | 1 | = 0 |
| <a id="DST"></a>**DST** | [28:24] | 5 | Destination operand, low 5 bits |
| <a id="DS"></a>**DS** | [23] | 1 | DST bank: 0 = R0..R31, 1 = special operand |
| <a id="COND"></a>**COND** | [22:19] | 4 | Condition; false = no register write, no port access [`conditions`](gen/conditions.md) |
| <a id="F"></a>**F** | [18] | 1 | 1 = update flags |
| <a id="OP"></a>**OP** | [17:13] | 5 | ALU operation [`alu_ops`](gen/alu_ops.md) |
| <a id="SRC"></a>**SRC** | [12:7] | 6 | Second operand {S, n[4:0]} [`operand_map`](gen/operand_map.md) |
| <a id="RSV"></a>**RSV** | [6:0] | 7 | Reserved, must be 0 |
