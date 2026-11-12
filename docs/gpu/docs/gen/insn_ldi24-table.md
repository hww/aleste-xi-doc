**INSTRUCTION · 32 BIT · J=0 I=1 LDI24 (R[DST] = imm24)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| **L** | [31:31] | 1 | Loop flag |
| **J** | [30:30] | 1 | = 0 |
| **I** | [29:29] | 1 | = 1 |
| **DST** | [28:24] | 5 | R0..R31 only |
| **IMM24** | [23:0] | 24 | 24-bit constant; unconditional, flags untouched |
