**INSTRUCTION · 32 BIT · J=1 I=0 CONTROL**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| **L** | [31:31] | 1 | Loop flag |
| **J** | [30:30] | 1 | = 1 |
| **I** | [29:29] | 1 | = 0 |
| **DST** | [28:24] | 5 | Unused |
| **DS** | [23:23] | 1 | Unused |
| **COND** | [22:19] | 4 | Condition |
| **F** | [18:18] | 1 | Unused |
| **OP** | [17:13] | 5 | Control operation |
| **REG** | [12:7] | 6 | Operand for JMPR (any operand, including special) |
| **ADDR** | [11:0] | 12 | Target address (JMP/CALL), halt code (HALT), IRQ code (IRQ) |
