**Operand map (6 bits, 0..63)**

| Code | Name | Read | Write |
| --- | --- | --- | --- |
| 0..31 | <a id="R0..R31"></a>**R0..R31** | 16-bit value | 16-bit value |
| 32 | <a id="ZERO"></a>**ZERO** | 0 | Ignored |
| 33 | <a id="FLAGS"></a>**FLAGS** | [3:0] = V C N Z | [3:0] |
| 34 | <a id="BUSY"></a>**BUSY** | {wb_cyc, flush_done, access_done, hit} | - |
| 35 | <a id="SHADOW"></a>**SHADOW** | [15:12] flags, [11:0] PC+1 | [11:0] PC |
| 36 | <a id="LOOP_CNT"></a>**LOOP_CNT** | Loop counter | Loop counter |
| 37 | <a id="LOOP_TGT"></a>**LOOP_TGT** | Loop target | Loop target |
| 38 | <a id="ROML"></a>**ROML** | Lower 16 bits of ROM word | Lower 16 bits of ROM word |
| 39 | <a id="ROMH"></a>**ROMH** | Upper 16 bits of ROM word (ROMA++) | Upper 16 bits of ROM word, commit, ROMA++ |
| 40 | <a id="ROMA"></a>**ROMA** | - | ROM access address |
| 41 | <a id="MHI"></a>**MHI** | Upper 16 bits of MUL | - |
| 42 | <a id="BANK"></a>**BANK** | [2:0] active bank | [2:0] bank select (global, all channels) |
| 43 | <a id="SPARE"></a>**SPARE** | 0 | reserved |
| 44..47 | <a id="DATA_0..3_"></a>**DATA[0..3]** | D: unpacked pixel (KEY if clipped); then pos += step | A: pixel in, starts pixel operation; then pos += step; operand[1..0] = channel |
| 48..63 | <a id="BANK_WINDOW"></a>**BANK_WINDOW** | - | write-only banked register; group = dst[3:2], channel = dst[1:0], bank = BANK |

**Notes:**

- BANK write takes effect on the next instruction (X-stage decode, in-order, no hold).
- Banks 5..7 are reserved: writes to the window are ignored, no error.
- RTL reference: 38 ROML, 39 ROMH, 40 ROMA, 41 MHI, 44..47 DATA (top.sv).
