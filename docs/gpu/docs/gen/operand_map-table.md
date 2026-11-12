**Operand map ({S, n[4:0]}; S=0 -> R0..R31)**

| Code | Name | Read | Write |
| --- | --- | --- | --- |
| 32 | ZERO | 0 | Ignored |
| 33 | FLAGS | [3:0] = V C N Z | Same |
| 34 | SHADOW | [11:0] PC, [15:12] flags | [11:0] PC |
| 35 | LOOP | [23:12] count, [11:0] target | Same |
| 36 | BUSY_SRC | 1 if SRC port busy | - |
| 37 | BUSY_DST | 1 if DST port busy | - |
| 38 | BUSY_STM | 1 if STM port busy | - |
| 39 | SRC.IDX | Pixel index | Set index, start prefetch |
| 40 | SRC.PIX | Unpacked pixel (fmt applied); IDX += STEP | Pack pixel (fmt applied) |
| 41 | SRC.W16 | Raw 16-bit word (fmt not applied); IDX += 1 word | Write raw word |
| 42 | SRC.STEP | Signed step | Same |
| 43 | SRC.MODE | fmt | Set format |
| 44 | SRC.PAGE | Page | set_page; writeback |
| 45 | DST.IDX | Pixel index | Set index, start prefetch |
| 46 | DST.PIX | Unpacked pixel (fmt applied); no IDX change | Pack pixel (fmt applied), set dirty; IDX += STEP |
| 47 | DST.W16 | Raw 16-bit word (fmt not applied) | Write raw word, set dirty |
| 48 | DST.STEP | Signed step | Same |
| 49 | DST.MODE | fmt | Set format |
| 50 | DST.PAGE | Page | set_page; writeback |
| 51 | STM.PTR | Stream pointer | Same |
| 52 | STM.W16 | Raw 16-bit word at PTR (fmt not applied); PTR += 1 word | - |
| 53 | STM.W24 | Two words: w0[15:0], w1[7:0] -> [23:16]; PTR += 2 words | - |
| 54 | STM.STEP | Signed step | Same |
| 55 | STM.MODE | fmt | Set format |
| 56 | STM.PAGE | Page | set_page |
| 57 | FLUSH | 0 | Any value: flush all dirty words |
| 58 | STM.PIX | Unpacked pixel (fmt applied); PTR += STEP | - |

**Notes:**

- Operands that are not readable or not writable are rejected by the assembler.
- Source advances on read, destination on write. Transparency: write the old pixel back.
- STM is read-only.
- W16 accesses a raw word (fmt not applied); PIX accesses a pixel (fmt applied). Both go through the same channel buffer.
- JMPR reads any operand via the operand mux; special operands are allowed.
