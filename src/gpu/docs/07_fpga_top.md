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

{{auto:registers}}

*Fig. 2. General-purpose registers.*

{{auto:sysregs}}

*Fig. 3. System registers.*

## Instruction Format

All instructions are 32-bit. Fields are fixed: `L`, `I`, `DST`, `DS`, `COND`, `F`, `REG_OP`, `SRC`, `IMM12`. See the ISA section for details.

{{auto:insn_ctrl_jmp}}

*Fig. 4. Instruction format.*