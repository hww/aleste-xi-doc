# Register Map

There are 64 operand slots (6 bits) in total. Slots 0..31 are general-purpose registers (R0..R31), 32..39 are system registers, 40..43 are DATA[0..3], 44..47 are reserved, 48..63 are pixel engine channels.

## General-Purpose Registers

Registers R0..R31 serve as source and destination in most instructions. R0 is a normal register; the constant zero comes from the ZERO operand (`32`).

**Table 5 — Register file · R0–R31 (16 bit)**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="R0"></a>**R0** | General-purpose (NOT hardwired to zero; use ZERO=32 for constant 0) |
| 1 | <a id="R1"></a>**R1** | General-purpose |
| 2 | <a id="R2"></a>**R2** | General-purpose |
| 3 | <a id="R3"></a>**R3** | General-purpose |
| 4 | <a id="R4"></a>**R4** | General-purpose |
| 5 | <a id="R5"></a>**R5** | General-purpose |
| 6 | <a id="R6"></a>**R6** | General-purpose |
| 7 | <a id="R7"></a>**R7** | General-purpose |
| 8 | <a id="R8"></a>**R8** | General-purpose |
| 9 | <a id="R9"></a>**R9** | General-purpose |
| 10 | <a id="R10"></a>**R10** | General-purpose |
| 11 | <a id="R11"></a>**R11** | General-purpose |
| 12 | <a id="R12"></a>**R12** | General-purpose |
| 13 | <a id="R13"></a>**R13** | General-purpose |
| 14 | <a id="R14"></a>**R14** | General-purpose |
| 15 | <a id="R15"></a>**R15** | General-purpose |
| 16 | <a id="R16"></a>**R16** | General-purpose |
| 17 | <a id="R17"></a>**R17** | General-purpose |
| 18 | <a id="R18"></a>**R18** | General-purpose |
| 19 | <a id="R19"></a>**R19** | General-purpose |
| 20 | <a id="R20"></a>**R20** | General-purpose |
| 21 | <a id="R21"></a>**R21** | General-purpose |
| 22 | <a id="R22"></a>**R22** | General-purpose |
| 23 | <a id="R23"></a>**R23** | General-purpose |
| 24 | <a id="R24"></a>**R24** | General-purpose |
| 25 | <a id="R25"></a>**R25** | General-purpose |
| 26 | <a id="R26"></a>**R26** | General-purpose |
| 27 | <a id="R27"></a>**R27** | General-purpose |
| 28 | <a id="R28"></a>**R28** | General-purpose |
| 29 | <a id="R29"></a>**R29** | General-purpose |
| 30 | <a id="R30"></a>**R30** | General-purpose |
| 31 | <a id="R31"></a>**R31** | General-purpose |


*Fig. 5. GPRs (6-bit operand field).*

A read takes one cycle (`q_a <= mem[ra]` on `posedge clk`), a write takes one cycle (`mem[wa] <= wdata`). Read-after-write in the same cycle is covered by bypass: `rdata_a = wdata_r` when `we && (wa == ra)`, so the new value is visible without waiting for the write to land.

![regfile: write mem_R5 (t2), read q_a (t2), bypass (t1, same-cycle)](gen/timing_regfile.svg)

*Figure 2 — regfile: write mem_R5 (t2), read q_a (t2), bypass (t1, same-cycle)*


## System Registers

System registers (32..38, 39 reserved) are available as a source in any instruction, and as a destination only in `MOV`. They provide access to flags, CALL/RET shadow, loop counter, and cache status.

**Table 6 — System Registers (32..38, 39 reserved)**

| Value | Name | Description |
| --- | --- | --- |
| 32 | <a id="ZERO"></a>**ZERO** | Constant zero |
| 33 | <a id="FLAGS"></a>**FLAGS** | Flags V, C, N, Z (see flags_bitfield) |
| 34 | <a id="SHADOW"></a>**SHADOW** | CALL/RET return address and flags (see shadow_bitfield) |
| 35 | <a id="LOOP_CNT"></a>**LOOP_CNT** | Loop counter |
| 36 | <a id="LOOP_TGT"></a>**LOOP_TGT** | Loop target |
| 37 | <a id="BUSY"></a>**BUSY** | Busy flags (see busy_bitfield) |
| 38 | <a id="MHI"></a>**MHI** | Upper 16 bits of MUL |
| 39 | <a id="reserved"></a>**reserved** | - |


*Fig. 6. System registers.*

## Pixel Engine Channels

Channels (48..63) are 4 sets of 4 registers each: IDX, IDXH, STEP, MODE_PAGE. They are write-only via `MOV`.

**Table 7 — Pixel Engine Channels (48..63)**

| Value | Name | Description |
| --- | --- | --- |
| 48 | <a id="CH0_IDX"></a>**CH0_IDX** | Pixel index |
| 49 | <a id="CH0_IDXH"></a>**CH0_IDXH** | Upper 3 bits of index |
| 50 | <a id="CH0_STEP"></a>**CH0_STEP** | Step (12.4) |
| 51 | <a id="CH0_MODE_PAGE"></a>**CH0_MODE_PAGE** | MODE and PAGE |
| 52 | <a id="CH1_IDX"></a>**CH1_IDX** | Pixel index |
| 53 | <a id="CH1_IDXH"></a>**CH1_IDXH** | Upper 3 bits of index |
| 54 | <a id="CH1_STEP"></a>**CH1_STEP** | Step (12.4) |
| 55 | <a id="CH1_MODE_PAGE"></a>**CH1_MODE_PAGE** | MODE and PAGE |
| 56 | <a id="CH2_IDX"></a>**CH2_IDX** | Pixel index |
| 57 | <a id="CH2_IDXH"></a>**CH2_IDXH** | Upper 3 bits of index |
| 58 | <a id="CH2_STEP"></a>**CH2_STEP** | Step (12.4) |
| 59 | <a id="CH2_MODE_PAGE"></a>**CH2_MODE_PAGE** | MODE and PAGE |
| 60 | <a id="CH3_IDX"></a>**CH3_IDX** | Pixel index |
| 61 | <a id="CH3_IDXH"></a>**CH3_IDXH** | Upper 3 bits of index |
| 62 | <a id="CH3_STEP"></a>**CH3_STEP** | Step (12.4) |
| 63 | <a id="CH3_MODE_PAGE"></a>**CH3_MODE_PAGE** | MODE and PAGE |


*Fig. 7. Pixel engine channels.*

## DATA[0..3]

DATA[0..3] (40..43) are pixel engine temporary registers. Reading triggers a pixel read operation; writing triggers a pixel write operation.

**Table 8 — DATA[0..3] (40..43)**

| Value | Name | Description |
| --- | --- | --- |
| 40 | <a id="DATA0"></a>**DATA0** | Pixel engine temporary register |
| 41 | <a id="DATA1"></a>**DATA1** | Pixel engine temporary register |
| 42 | <a id="DATA2"></a>**DATA2** | Pixel engine temporary register |
| 43 | <a id="DATA3"></a>**DATA3** | Pixel engine temporary register |


*Fig. 8. DATA registers.*

