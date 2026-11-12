**INSTRUCTION · 32 BIT · J=0 I=0 REG-REG (d = d op s)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| **L** | [31:31] | 1 | Loop flag |
| **J** | [30:30] | 1 | = 0 |
| **I** | [29:29] | 1 | = 0 |
| **DST** | [28:24] | 5 | Destination operand, low 5 bits |
| **DS** | [23:23] | 1 | DST bank: 0 = R0..R31, 1 = special operand |
| **COND** | [22:19] | 4 | Condition; false = no register write, no port access |
| **F** | [18:18] | 1 | 1 = update flags |
| **OP** | [17:13] | 5 | ALU operation |
| **SRC** | [12:7] | 6 | Second operand {S, n[4:0]} |
| **RSV** | [6:0] | 7 | Reserved, must be 0 |
