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

**Table 4 — Register file · R0–R31 (16 bit)**

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

**Table 5 — System Registers (32..38, 39 reserved)**

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

![INSTRUCTION · 32 BIT](gen/insn.svg)

*Figure 2 — INSTRUCTION · 32 BIT*

**Table 6 — INSTRUCTION · 32 BIT**

| Format | Selector | Description |
| --- | --- | --- |
| <a id="reg-reg"></a>**REG-REG** | `J=0 I=0` | d = d op s |
| <a id="reg-imm12"></a>**REG-IMM12** | `J=1 I=1` | d = d op imm |
| <a id="ldi24"></a>**LDI24** | `J=0 I=1` | R[DST] = imm24; unconditional, flags untouched |
| <a id="control"></a>**CONTROL** | `J=1 I=0` | — |

**REG-REG** (`J=0 I=0`)

| Field | Bits | Width | Fixed | Description |
| --- | --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | — | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | 0 | Format selector, high |
| <a id="I"></a>**I** | [29] | 1 | 0 | Format selector, low |
| <a id="DST"></a>**DST** | [28:24] | 5 | — | Destination operand, low 5 bits |
| <a id="DS"></a>**DS** | [23] | 1 | — | DST bank: 0 = R0..R31, 1 = special operand |
| <a id="COND"></a>**COND** | [22:19] | 4 | — | Condition; false = no register write, no port access [`conditions`](gen/conditions.md) |
| <a id="F"></a>**F** | [18] | 1 | — | 1 = update flags |
| <a id="OP"></a>**OP** | [17:13] | 5 | — | ALU operation [`alu_ops`](gen/alu_ops.md) |
| <a id="SRC"></a>**SRC** | [12:7] | 6 | — | Second operand {S, n[4:0]} [`operand_map`](gen/operand_map.md) |
| <a id="RSV"></a>**RSV** | [6:0] | 7 | — | Reserved, must be 0 |

**REG-IMM12** (`J=1 I=1`)

| Field | Bits | Width | Fixed | Description |
| --- | --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | — | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | 1 | Format selector, high |
| <a id="I"></a>**I** | [29] | 1 | 1 | Format selector, low |
| <a id="DST"></a>**DST** | [28:24] | 5 | — | Destination operand, low 5 bits |
| <a id="DS"></a>**DS** | [23] | 1 | — | — |
| <a id="COND"></a>**COND** | [22:19] | 4 | — | [`conditions`](gen/conditions.md) |
| <a id="F"></a>**F** | [18] | 1 | — | — |
| <a id="OP"></a>**OP** | [17:13] | 5 | — | [`alu_ops`](gen/alu_ops.md) |
| <a id="SX"></a>**SX** | [12] | 1 | — | 1 = sign-extend IMM, 0 = zero-extend |
| <a id="IMM"></a>**IMM** | [11:0] | 12 | — | 12-bit immediate, operand B |

**LDI24** (`J=0 I=1`)

| Field | Bits | Width | Fixed | Description |
| --- | --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | — | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | 0 | Format selector, high |
| <a id="I"></a>**I** | [29] | 1 | 1 | Format selector, low |
| <a id="DST"></a>**DST** | [28:24] | 5 | — | R0..R31 only |
| <a id="IMM24"></a>**IMM24** | [23:0] | 24 | — | 24-bit constant |

**CONTROL** (`J=1 I=0`)

| Field | Bits | Width | Fixed | Description |
| --- | --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | — | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | 1 | Format selector, high |
| <a id="I"></a>**I** | [29] | 1 | 0 | Format selector, low |
| <a id="DST"></a>**DST** | [28:24] | 5 | — | Unused |
| <a id="DS"></a>**DS** | [23] | 1 | — | Unused |
| <a id="COND"></a>**COND** | [22:19] | 4 | — | [`conditions`](gen/conditions.md) |
| <a id="F"></a>**F** | [18] | 1 | — | Unused |
| <a id="OP"></a>**OP** | [17:13] | 5 | — | [`ctrl_ops`](gen/ctrl_ops.md) |
| <a id="REG"></a>**REG** | [12:7] | 6 | — | Operand for JMPR (any operand, including special) |
| <a id="ADDR"></a>**ADDR** | [11:0] | 12 | — | Target address (JMP/CALL), halt code (HALT), IRQ code (IRQ) |

**Notes:**

- L bit: after the word, if count > 1 then count--, PC = loop target; else fall through. Runs even if COND is false.


*Fig. 4. Instruction format.*