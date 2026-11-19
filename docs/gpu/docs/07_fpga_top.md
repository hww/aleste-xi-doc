# FPGA Top Overview

LX-GPU is a 16-bit-data processor (32-bit instructions) with a pixel engine, a cache, and a Wishbone interface for external memory. The core is a 3-stage pipeline F → D → X; it stalls in X while a device has not acknowledged, and in D while an X-stage hazard resolves.

## Block Diagram

The processor consists of several interconnected blocks: `core_fetch` (PC, hardware loop, SHADOW), `core_rom`, `core_regfile`, `core_alu` + `core_cond` (X-stage execute), and `ch_top` (containing `ch_addr_gen`, `ch_blender`, `ch_cache`). Decode and writeback live in the X stage of `gpu_top`; there are no separate Decode / Writeback modules. The architecture is modular: blocks know nothing about each other, only the protocol.

![LX-GPU architecture](images/lx-gpu-architecture.drawio.svg)

*Fig. 1. LX-GPU block diagram.*

## Execution Protocol

The pipeline advances when `adv = ~halted & ~x_busy & ~fu_hold`. An X-stage instruction that issues a device request (`ch_data_req`, `rom_req`, `ch_flush_req`) holds `x_busy` until the device acknowledges (`x_dev_ack`); `pc`, the IR, the regfile outputs and `x_ins_r` all hold. One device per instruction. The cache `ack_o` is a one-cycle hit strobe; on a miss the cache fills in the background and the requester must hold/re-issue. The consumer-side data ack in `ch_top` is `blend_ack` from the blender, not the cache `ack_o`.

## Registers and Operands

Processor registers are split into four groups: general (R0..R31), system (32..41, with 42..43 reserved), DATA[0..3] (44..47), and pixel engine channels (48..63). The register map is shown below.

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


*Fig. 2. General-purpose registers.*

**Table 2 — System Registers (32..38, 39 reserved)**

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


*Fig. 3. System registers.*

## Instruction Format

All instructions are 32-bit. Fields are fixed: `L[31]`, class `[30:29]`, `COND[28:25]`, `WRITE[24]`, `F[23]`, `DST[22:17]`, `ALU_OP[16:12]`, `SRC[11:6]`, `SX`/`IMM11[10:0]`, `ADDR[11:0]`, `IMM16[15:0]`. See the ISA section for details.

![J=1 I=0 CONTROL (R=0: JMP/CALL/RET/HALT/IRQ/FLUSH)](gen/insn_ctrl_jmp.svg)

*Figure 1 — J=1 I=0 CONTROL (R=0: JMP/CALL/RET/HALT/IRQ/FLUSH)*

**Table 3 — J=1 I=0 CONTROL (R=0: JMP/CALL/RET/HALT/IRQ/FLUSH)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | = 1 |
| <a id="I"></a>**I** | [29] | 1 | = 0 |
| <a id="COND"></a>**COND** | [28:25] | 4 | Condition [`conditions`](gen/conditions.md) |
| <a id="WRITE"></a>**WRITE** | [24] | 1 | Unused for CTRL, must be 0 |
| <a id="F"></a>**F** | [23] | 1 | Unused for CTRL (must be 0) |
| <a id="DST_CODE"></a>**DST_CODE** | [22:17] | 6 | Unused for CTRL [`operand_map`](gen/operand_map.md) |
| <a id="R"></a>**R** | [16] | 1 | Jump/Call: 0 = by immediate, 1 = by source register |
| <a id="CTRL_OP"></a>**CTRL_OP** | [15:12] | 4 | Control operation [`ctrl_ops`](gen/ctrl_ops.md) |
| <a id="ADDR"></a>**ADDR** | [11:0] | 12 | Target address (JMP/CALL), halt/IRQ code, channel (FLUSH) |


*Fig. 4. Instruction format.*