**CTRL OP (J=1, I=0)**

| Code | Name | Description |
| --- | --- | --- |
| 0 | NOP | Nothing |
| 1 | JMP | PC = ADDR |
| 2 | CALL | SHADOW[11:0] = PC+1, SHADOW[15:12] = flags; PC = ADDR |
| 3 | RET | PC = SHADOW[11:0]; flags not restored |
| 4 | JMPR | PC = operand[REG][11:0] (any operand, including special) |
| 5 | HALT | ADDR=0 -> IDLE; ADDR!=0 -> ERROR(code) |
| 6 | IRQ | Raise IRQ, code = ADDR |
| 7..31 | reserved | - |

**Notes:**

- Only CALL writes SHADOW. Nested calls: save SHADOW to a register first.
- L bit: after the word, if count > 1 then count--, PC = loop target; else fall through. Runs even if COND is false. L is allowed with any class, including control words.
