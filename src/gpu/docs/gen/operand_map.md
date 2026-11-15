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
| 38 | <a id="ROML"></a>**ROML** | Lover 16 bits of ROM | Lover 16 bits of ROM |
| 39 | <a id="ROMH"></a>**ROMH** | Upper 16 bits of ROM | Upper 16 bits of ROM, ROMA++ |
| 40 | <a id="ROMA"></a>**ROMA** | - | ROM Access address with |
| 41 | <a id="MHI"></a>**MHI** | Upper 16 bits of MUL | - |
| 42..43 | <a id="reserved"></a>**reserved** | 0 | - |
| 44..47 | <a id="DATA_0..3_"></a>**DATA[0..3]** | pixel_out from channel ch | pixel_in to channel ch, operand[1..0] is channel number |
| 48..51 | <a id="IDX_0..3_"></a>**IDX[0..3]** | - | Write-only channel IDX registers, operand[1..0] is channel number |
| 52..55 | <a id="IDXH_0..3_"></a>**IDXH[0..3]** | - | Write-only channel IDXH registers, operand[1..0] is channel number |
| 56..59 | <a id="STEP_0..3_"></a>**STEP[0..3]** | - | Write-only channel STEP registers, operand[1..0] is channel number |
| 60..63 | <a id="MODE_PAGE_0..3_"></a>**MODE_PAGE[0..3]** | - | Write-only channel PAGE registers, operand[1..0] is channel number |
