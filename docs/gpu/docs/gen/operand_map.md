# Operand map (6 bits, 0..63)

| Code | Name | Read | Write |
| --- | --- | --- | --- |
| 0..31 | <a id="R0..R31"></a>**R0..R31** | 16-bit value | 16-bit value |
| 32 | <a id="ZERO"></a>**ZERO** | 0 | Ignored |
| 33 | <a id="FLAGS"></a>**FLAGS** | [3:0] = V C N Z | [3:0] |
| 34 | <a id="SHADOW"></a>**SHADOW** | [15:12] flags, [11:0] PC+1 | [11:0] PC |
| 35 | <a id="LOOP_CNT"></a>**LOOP_CNT** | Loop counter | Loop counter |
| 36 | <a id="LOOP_TGT"></a>**LOOP_TGT** | Loop target | Loop target |
| 37 | <a id="BUSY"></a>**BUSY** | {wb_cyc, flush_done, access_done, hit} | - |
| 38 | <a id="MHI"></a>**MHI** | Upper 16 bits of MUL | - |
| 39 | <a id="reserved"></a>**reserved** | 0 | - |
| 40..43 | <a id="DATA_0..3_"></a>**DATA[0..3]** | pixel_out from channel ch | pixel_in to channel ch |
| 44..47 | <a id="reserved"></a>**reserved** | 0 | - |
| 48..63 | <a id="CH_ch___IDX_IDXH_STEP_MODE_PAGE_"></a>**CH[ch]_{IDX,IDXH,STEP,MODE_PAGE}** | - | Write-only channel register |
