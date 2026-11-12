**INSTRUCTION · 32 BIT · J=1 I=1 REG-IMM12 (d = d op imm)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| **L** | [31:31] | 1 | Loop flag |
| **J** | [30:30] | 1 | = 1 |
| **I** | [29:29] | 1 | = 1 |
| **DST** | [28:24] | 5 | Destination operand, low 5 bits |
| **DS** | [23:23] | 1 | DST bank |
| **COND** | [22:19] | 4 | Condition |
| **F** | [18:18] | 1 | Update flags |
| **OP** | [17:13] | 5 | ALU operation |
| **SX** | [12:12] | 1 | 1 = sign-extend IMM, 0 = zero-extend |
| **IMM** | [11:0] | 12 | 12-bit immediate, operand B |
