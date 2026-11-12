**COND (4 bits, ARM-style)**

| Code | Name | Description |
| --- | --- | --- |
| 0 | AL | Always |
| 1 | EQ | Z=1 |
| 2 | NE | Z=0 |
| 3 | CS | C=1 (unsigned >=) |
| 4 | CC | C=0 (unsigned <) |
| 5 | MI | N=1 |
| 6 | PL | N=0 |
| 7 | VS | V=1 |
| 8 | VC | V=0 |
| 9 | HI | C=1 and Z=0 |
| 10 | LS | C=0 or Z=1 |
| 11 | GE | N=V |
| 12 | LT | N!=V |
| 13 | GT | Z=0 and N=V |
| 14 | LE | Z=1 or N!=V |
| 15 | reserved | - |

**Notes:**

- Decoded into a register during the operand-read phase from flags of the previous instruction.
