| Адрес | Имя | Чтение | Запись |
| --- | --- | --- | --- |
| 0-31 | **R0-R31** | 24-bit register file | 24-bit register file |
| 32 | **ZERO** | Constant zero | Ignored |
| 33 | **ACC** | Previous ALU result | Not writable |
| 34 | **P** | Multiplier result | Not writable |
| 35 | **FIFO8** | Pop one byte; wait while empty | Not writable |
| 36 | **FIFO16** | Pop two bytes, low byte first | Not writable |
| 37 | **FIFO16S** | Pop two bytes, sign-extended | Not writable |
| 38 | **SPIX** | Source pixel from SW | Not writable |
| 39 | **DPIX** | Destination pixel from DW | Write pixel to DW, mark dirty |
| 40 | **SIDX** | Not readable | Set source linear pixel index |
| 41 | **DIDX** | Not readable | Set destination linear pixel index |
| 42 | **FLUSH** | Not readable | Flush dirty destination word |
| 43 | **PALI** | Not readable | Palette index |
| 44 | **PALD** | Not readable | Palette colour |
| 45 | **IMM** | 9-bit immediate from X field | Not writable |
| 46 | **STAT** | Status flags | Request interrupt |
