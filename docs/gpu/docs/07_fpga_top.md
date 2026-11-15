# FPGA Top Overview

LX-GPU is a 16-bit processor with a pixel engine, a cache, and a Wishbone interface for external memory. Instructions execute one at a time, stalling on data wait (`ack`). All devices (registers, ALU, cache, pixel engine) use the `ack` protocol — a one-cycle strobe.

## Block Diagram

The processor consists of several interconnected blocks: PC, ROM, Decode, RegFile, ALU, Cache, PixelEngine, Blender, and Writeback. Each block has its own `ack`; a top-level `ack` collects them. The architecture is modular: blocks know nothing about each other, only the protocol.

![LX-GPU architecture](images/lx-gpu-architecture.drawio.svg)

*Fig. 1. LX-GPU block diagram.*

## Execution Protocol

Each instruction executes on `ack`. When an instruction is latched into the instruction register (IR), it is decoded and devices start working. If a device needs time (e.g. cache fill), it does not assert `ack`, and `pc` stalls. When all devices assert `ack`, the instruction is complete: `pc` advances, IR loads the next instruction.

## Registers and Operands

Processor registers are split into three groups: general (R0..R31), system (32..39), and pixel engine channels (48..63). The register map is shown below.

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

All instructions are 32-bit. Fields are fixed: `L`, `I`, `DST`, `DS`, `COND`, `F`, `REG_OP`, `SRC`, `IMM12`. See the ISA section for details.

![J=1 I=0 CTRL (JMP/CALL/RET/HALT/IRQ/FLUSH)](gen/insn_ctrl_jmp.svg)

*Figure 1 — J=1 I=0 CTRL (JMP/CALL/RET/HALT/IRQ/FLUSH)*

**Table 3 — J=1 I=0 CTRL (JMP/CALL/RET/HALT/IRQ/FLUSH)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | = 1 |
| <a id="I"></a>**I** | [29] | 1 | = 0 |
| <a id="DST_CODE"></a>**DST_CODE** | [28:23] | 6 | Unused for non-JMPR CTRL [`operand_map`](gen/operand_map.md) |
| <a id="WRITE"></a>**WRITE** | [22] | 1 | Unused for CTRL |
| <a id="COND"></a>**COND** | [21:18] | 4 | Condition [`conditions`](gen/conditions.md) |
| <a id="F"></a>**F** | [17] | 1 | Unused for CTRL (must be 0) |
| <a id="OP"></a>**OP** | [16:12] | 5 | Control operation [`ctrl_ops`](gen/ctrl_ops.md) |
| <a id="SX"></a>**SX** | [11] | 1 | Unused in CTRL |
| <a id="ADDR"></a>**ADDR** | [10:0] | 11 | Target address (JMP/CALL), halt/IRQ code, channel (FLUSH) |


*Fig. 4. Instruction format.*