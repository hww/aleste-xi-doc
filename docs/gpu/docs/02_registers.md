# Register Map

There are 64 operand slots (6 bits) in total. Slots 0..31 are general-purpose registers (R0..R31), 32..42 are system registers, 43 is reserved, 44..47 are DATA[0..3], 48..63 are the pixel engine channel registers (a banked window in channels v2).

## General-Purpose Registers

Registers R0..R31 serve as source and destination in most instructions. R0 is a normal register; the constant zero comes from the ZERO operand (`32`).

**Table 1 — Register file · R0–R31 (16 bit)**

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

![regfile: write mem[wa] on posedge; synchronous read on rd_en_i with write-through bypass](gen/timing_regfile.svg)

## System Registers

System registers (32..42, 43 reserved) are available as a source in any instruction, and as a destination only in `MOV`. They provide access to flags, channel status, CALL/RET shadow, loop counter, ROM access, the MUL high half, and the channel register bank (`BANK`).

**Table 2 — System Registers (32..42, 43 reserved)**

| Value | Name | Description |
| --- | --- | --- |
| 32 | <a id="ZERO"></a>**ZERO** | Constant zero |
| 33 | <a id="FLAGS"></a>**FLAGS** | Flags V, C, N, Z (see flags_bitfield) |
| 34 | <a id="BUSY"></a>**BUSY** | Channel status (see busy_bitfield) |
| 35 | <a id="SHADOW"></a>**SHADOW** | CALL/RET return address and flags (see shadow_bitfield) |
| 36 | <a id="LOOP_CNT"></a>**LOOP_CNT** | Loop counter |
| 37 | <a id="LOOP_TGT"></a>**LOOP_TGT** | Loop target |
| 38 | <a id="ROML"></a>**ROML** | ROM access, low 16 bits |
| 39 | <a id="ROMH"></a>**ROMH** | ROM access, high 16 bits (a read or a write increments ROMA) |
| 40 | <a id="ROMA"></a>**ROMA** | ROM access address (write only) |
| 41 | <a id="MHI"></a>**MHI** | Upper 16 bits of MUL |
| 42 | <a id="BANK"></a>**BANK** | Bank of the channel window 48..63 (channels v2), R/W, 3 bits |


*Fig. 6. System registers.*
