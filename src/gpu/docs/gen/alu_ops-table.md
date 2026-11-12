**ALU OP (5 bits)**

| Code | Name | Description | Flags |
| --- | --- | --- | --- |
| 0 | MOV | d = s | Z N |
| 1 | AND | d = d & s | Z N |
| 2 | OR | d = d | s | Z N |
| 3 | XOR | d = d ^ s (NOT = XOR with -1) | Z N |
| 4 | ANDN | d = d & ~s | Z N |
| 5 | ADD | d = d + s | Z N C V |
| 6 | SUB | d = d - s; C = not borrow | Z N C V |
| 7 | CMP | SUB, result discarded, flags always written | Z N C V |
| 8 | TST | AND, result discarded, flags always written | Z N |
| 9 | ROR | 24-bit rotate right by s[4:0] mod 24 | Z N |
| 10 | SHR | ROR with zero fill | Z N |
| 11 | SAR | ROR with bit 23 fill | Z N |
| 12 | MUL | d = (d x s)[23:0], signed, multi-cycle (DSP) | Z N |
| 13 | MULH | d = (d x s)[35:12], multi-cycle | Z N |
| 14..31 | reserved | - | - |

**Notes:**

- Writing to ZERO discards the result. NOP = MOV ZERO, ZERO.
- Flags are written only if F=1 (CMP/TST always).
