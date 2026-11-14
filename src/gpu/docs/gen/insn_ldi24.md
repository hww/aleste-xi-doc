# INSTRUCTION · 32 BIT · J=0 I=1 LDI24 (R[DST] = imm24)

![INSTRUCTION · 32 BIT · J=0 I=1 LDI24 (R[DST] = imm24)](gen/insn_ldi24.svg)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | = 0 |
| <a id="I"></a>**I** | [29] | 1 | = 1 |
| <a id="DST"></a>**DST** | [28:24] | 5 | R0..R31 only |
| <a id="IMM24"></a>**IMM24** | [23:0] | 24 | 24-bit constant; unconditional, flags untouched |
