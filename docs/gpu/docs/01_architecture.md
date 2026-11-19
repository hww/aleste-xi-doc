# Graphics coprocessor for Z80: architecture

*Source for the documentation generator. YAML declarations in `spec/` produce SVG and MD tables. Numbers are approximate; details are refined on the simulator.*

## 1. Principles

1. **Simplicity over peak speed.** The bottleneck is memory, so the core can be simple.
2. **Programmable core, not a hardwired state machine.** Microcode lives in BRAM; a new algorithm means new microcode, not new logic.
3. **Only the hot path goes into hardware:** word buffers, pixel packing, address computation inside ports.
4. **Screen coordinates inside, addresses outside are invisible.** The CPU says "draw at (x, y)"; the port turns a pixel index into a word address.
5. **Pixel formats: 1, 2, 4, 8, 16 bpp; pass-through modes LO8/HI8/16.**
6. **No hardware scrolling.** Replaced by fast block copying.
7. **One instruction format, four classes** (`J`, `I`): reg-reg, reg-imm11, LDI16, control.
8. **Flags Z, N, C, V.** ARM-style conditions. `CMP`/`TST` always write flags; others by `F=1`. Any ALU op can be issued with `WRITE=0` to discard the result while still updating flags.
9. **`SHADOW` — return address + flags**; `CALL` writes it, `RET` uses PC only, `JMPR` for indirect return.
10. **`LOOP` register** — count + target, `L` bit drives it.
11. **Ports stall the sequencer in hardware**; the model does not simulate cycle counts.
12. **Four channels CH0..CH3.** Each channel has its own `PAGE`, `MODE`, `IDX`, `IDXH`, `STEP`. `DATA[n]` is the pixel port of channel `n`. There is no separate `SRC`/`DST`/`STM` port: roles are assigned by microcode convention.

## 2. Overall picture

![Microcore architecture](images/lx-gpu-architecture.webp)

*Domain boundary: command and register logic in the 8-bit domain; the core, word buffers, and video controller on 16-bit memory. They meet at the core's registers.*

GPU → Wishbone → VideoMemoryArbiter. The arbiter is out of scope; raster scan has top priority.

## 3. Microinstruction (32 bit)

The microinstruction is a fixed 32-bit word. The pair (J, I) selects one of four formats: REG-REG, REG-IMM11, LDI16, CONTROL.

![J=0 I=0 REG-REG](gen/insn_reg.svg)

*Figure 1 — J=0 I=0 REG-REG*

**Table 1 — J=0 I=0 REG-REG**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | = 0 |
| <a id="I"></a>**I** | [29] | 1 | = 0 |
| <a id="COND"></a>**COND** | [28:25] | 4 | Condition [`conditions`](gen/conditions.md) |
| <a id="WRITE"></a>**WRITE** | [24] | 1 | 1 = write result; 0 = do not write (flags still update if F=1) |
| <a id="F"></a>**F** | [23] | 1 | 1 = update flags |
| <a id="DST_CODE"></a>**DST_CODE** | [22:17] | 6 | Destination operand (6 bits) [`operand_map`](gen/operand_map.md) |
| <a id="ALU_OP"></a>**ALU_OP** | [16:12] | 5 | ALU operation [`alu_ops`](gen/alu_ops.md) |
| <a id="SRC"></a>**SRC** | [11:6] | 6 | Second operand (6 bits) [`operand_map`](gen/operand_map.md) |
| <a id="RSV"></a>**RSV** | [5:0] | 6 | Reserved, must be 0 |


![J=1 I=1 REG-IMM11](gen/insn_imm11.svg)

*Figure 2 — J=1 I=1 REG-IMM11*

**Table 2 — J=1 I=1 REG-IMM11**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | = 1 |
| <a id="I"></a>**I** | [29] | 1 | = 1 |
| <a id="COND"></a>**COND** | [28:25] | 4 | Condition [`conditions`](gen/conditions.md) |
| <a id="WRITE"></a>**WRITE** | [24] | 1 | 1 = write result; 0 = do not write |
| <a id="F"></a>**F** | [23] | 1 | Update flags |
| <a id="DST_CODE"></a>**DST_CODE** | [22:17] | 6 | Destination operand (6 bits) [`operand_map`](gen/operand_map.md) |
| <a id="ALU_OP"></a>**ALU_OP** | [16:12] | 5 | ALU operation [`alu_ops`](gen/alu_ops.md) |
| <a id="SX"></a>**SX** | [11] | 1 | 1 = sign-extend IMM11, 0 = zero-extend |
| <a id="IMM"></a>**IMM** | [10:0] | 11 | 11-bit immediate, operand B |


![J=1 I=0 CONTROL (R=0: JMP/CALL/RET/HALT/IRQ/FLUSH)](gen/insn_ctrl_jmp.svg)

*Figure 3 — J=1 I=0 CONTROL (R=0: JMP/CALL/RET/HALT/IRQ/FLUSH)*

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


![J=1 I=0 CONTROL RJUMP (R=1: JMPR)](gen/insn_ctrl_jmpr.svg)

*Figure 4 — J=1 I=0 CONTROL RJUMP (R=1: JMPR)*

**Table 4 — J=1 I=0 CONTROL RJUMP (R=1: JMPR)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | = 1 |
| <a id="I"></a>**I** | [29] | 1 | = 0 |
| <a id="COND"></a>**COND** | [28:25] | 4 | Condition [`conditions`](gen/conditions.md) |
| <a id="WRITE"></a>**WRITE** | [24] | 1 | Unused for CTRL, must be 0 |
| <a id="F"></a>**F** | [23] | 1 | Unused for CTRL (must be 0) |
| <a id="DST_CODE"></a>**DST_CODE** | [22:17] | 6 | Unused for CTRL [`operand_map`](gen/operand_map.md) |
| <a id="R"></a>**R** | [16] | 1 | = 1 (register jump) |
| <a id="CTRL_OP"></a>**CTRL_OP** | [15:12] | 4 | = JMPR (register indirect jump) [`ctrl_ops`](gen/ctrl_ops.md) |
| <a id="SRC"></a>**SRC** | [11:6] | 6 | Source operand code (0..63) [`operand_map`](gen/operand_map.md) |
| <a id="RSV"></a>**RSV** | [5:0] | 6 | Unused, must be 0 |


**Field overlap in control words.** Bits [11:6] belong to both `ADDR[11:0]` and `REG[5:0]`. This is intentional: for `JMPR` the target register is encoded in the same position as `SRC` in reg-reg words, while `ADDR` supplies the immediate target for `JMP`/`CALL`. The two interpretations are mutually exclusive per opcode; the assembler rejects combinations that would need both.

**Bit positions in the RTL** (normative for `gpu_top` / `core_fetch`): `COND[28:25]`, `WRITE[24]`, `F[23]`, `DST[22:17]`, `ALU_OP[16:12]`, `SRC[11:6]`, `SX[11]`/`IMM11[10:0]`, `ADDR[11:0]`, `IMM16[15:0]`. `L` is bit `[31]`; class bits are `[30:29]`.

**Execution order.** One instruction per cycle (model). The ALU reads its two operands A and B at the start of the cycle and writes the result at the end. Flags come from the previous instruction.

**Condition and flags.** Z, N, C, V from the previous flag-writing instruction. `COND` selects; false = no register write, no port access.

**Table 5 — COND (4 bits, ARM-style)**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="AL"></a>**AL** | Always |
| 1 | <a id="EQ"></a>**EQ** | Z=1 |
| 2 | <a id="NE"></a>**NE** | Z=0 |
| 3 | <a id="CS"></a>**CS** | C=1 (unsigned >=) |
| 4 | <a id="CC"></a>**CC** | C=0 (unsigned <) |
| 5 | <a id="MI"></a>**MI** | N=1 |
| 6 | <a id="PL"></a>**PL** | N=0 |
| 7 | <a id="VS"></a>**VS** | V=1 |
| 8 | <a id="VC"></a>**VC** | V=0 |
| 9 | <a id="HI"></a>**HI** | C=1 and Z=0 |
| 10 | <a id="LS"></a>**LS** | C=0 or Z=1 |
| 11 | <a id="GE"></a>**GE** | N=V |
| 12 | <a id="LT"></a>**LT** | N!=V |
| 13 | <a id="GT"></a>**GT** | Z=0 and N=V |
| 14 | <a id="LE"></a>**LE** | Z=1 or N!=V |
| 15 | <a id="NV"></a>**NV** | Never (default=false) |


ROM is synchronous: `data_r <= mem[addr]` latches on `ack`, so the instruction is available one cycle after `addr`. The `pc` is stable during the whole cycle, and the `ack` from the previous instruction gates the read.

![microcode_rom: synchronous read on fetch_en_i (1 cyc latency, held on stall)](gen/timing_microcode_rom.svg)

*Figure 5 — microcode_rom: synchronous read on fetch_en_i (1 cyc latency, held on stall)*


## 4. ALU

The ALU implements 18 operations: logic (MOV/MVN/AND/BIC/OR/ORN/XOR/XNOR), arithmetic (ADD/ADC/SUB/SBC), shift (ROR/SHR/SAR), and other (MUL/TST/CMP). The operation is selected by `op[4:0]`.

**Table 6 — ALU OP (5 bits, class = op[4:3], fn = op[2:1], flag = op[0])**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="MOV"></a>**MOV** | cls=00, fn=00, inv=0: d = s |
| 1 | <a id="MVN"></a>**MVN** | cls=00, fn=00, inv=1: d = ~s |
| 2 | <a id="AND"></a>**AND** | cls=00, fn=01, inv=0: d = d & s |
| 3 | <a id="BIC"></a>**BIC** | cls=00, fn=01, inv=1: d = d & ~s |
| 4 | <a id="OR"></a>**OR** | cls=00, fn=10, inv=0: d = d \| s |
| 5 | <a id="ORN"></a>**ORN** | cls=00, fn=10, inv=1: d = d \| ~s |
| 6 | <a id="XOR"></a>**XOR** | cls=00, fn=11, inv=0: d = d ^ s |
| 7 | <a id="XNOR"></a>**XNOR** | cls=00, fn=11, inv=1: d = d ^ ~s |
| 8 | <a id="ADD"></a>**ADD** | cls=01, fn=00, sub=0, cin_sel=0: d = d + s |
| 10 | <a id="ADC"></a>**ADC** | cls=01, fn=01, sub=0, cin_sel=1: d = d + s + C |
| 13 | <a id="SUB"></a>**SUB** | cls=01, fn=10, sub=1, cin_sel=0: d = d - s; C = not borrow |
| 15 | <a id="SBC"></a>**SBC** | cls=01, fn=11, sub=1, cin_sel=1: d = d - s - (1-C) |
| 16 | <a id="ROR"></a>**ROR** | cls=10, fn=00: 16-bit rotate right by s[3:0] |
| 18 | <a id="SHR"></a>**SHR** | cls=10, fn=01: logical shift right |
| 20 | <a id="SAR"></a>**SAR** | cls=10, fn=10: arithmetic shift right |
| 24 | <a id="MUL"></a>**MUL** | cls=11, fn=00: d = (d * s)[15:0] signed; high 16 to MHI |

**Notes:**

- Writing to ZERO discards the result. NOP = MOV ZERO, ZERO.
- TST/CMP are encoded in the assembler with WRITE=0; dedicated opcodes 28/30 are equivalent to AND/SUB with WRITE=0.


**Notes:**
- Writing to ZERO discards the result. NOP = MOV ZERO, ZERO.
- Flags are written only if F=1 (CMP/TST always write flags).
- Any ALU operation may be issued with `WRITE=0` — the result is discarded, but flags are still updated if `F=1`. TST/CMP are encoded as AND/SUB with `WRITE=0`.
- **Z and N are updated for every flag-writing instruction. C and V are updated only for arithmetic class** (`upd_cv = is_arith`): ADD/ADC/SUB/SBC. Logic, shift and MUL leave C/V unchanged.
- `ROR`/`SHR`/`SAR` do not update C.
- `MUL` is multi-cycle in RTL (DSP); 1 cycle in the model.
- **`MUL` width.** RTL (`core_alu.sv`) computes `a_signed * b_signed` over 16×16 → 32 bits (low 16 to result, high 16 to MHI). The model agrees.
- **`SHR`/`SAR` with shift ≥ 16.** RTL uses a 4-stage barrel shifter over `b[3:0]` (mod 16). Shift counts ≥ 16 wrap to `b[3:0]`. This behaviour is normative.

An ALU instruction takes two cycles from "instruction available" to "result in register". In cycle 1 the register file reads `rdata_a`/`rdata_b`; in cycle 2 the writeback writes `mem[wa] <= wdata`. The ALU itself is combinational (0 cycles), so `pc` advances every cycle; only the register write is delayed by one cycle. `MUL` additionally registers `mhi` on the next `posedge clk`.

![ALU instruction in F -> D -> X pipeline (D reads regfile, X computes & writes back)](gen/timing_alu_pipeline.svg)

*Figure 6 — ALU instruction in F -> D -> X pipeline (D reads regfile, X computes & writes back)*


## 5. Control

Control-class instructions (J=1, I=0) implement NOP, JMP, CALL, RET, JMPR, HALT, IRQ, and FLUSH. They are all selected by `reg_op` (CTRL op).

**Table 7 — CTRL OP (J=1, I=0)**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="NOP"></a>**NOP** | Nothing |
| 1 | <a id="JMP"></a>**JMP** | PC = ADDR (11 bits) |
| 2 | <a id="CALL"></a>**CALL** | SHADOW[15:12] = flags, SHADOW[11:0] = PC+1; PC = ADDR |
| 3 | <a id="RET"></a>**RET** | PC = SHADOW[11:0]; flags not restored |
| 4 | <a id="HALT"></a>**HALT** | ADDR=0 -> IDLE; ADDR!=0 -> ERROR(code) |
| 5 | <a id="IRQ"></a>**IRQ** | Raise IRQ, code = ADDR |
| 6 | <a id="FLUSH"></a>**FLUSH** | Flush cache channel ADDR[1:0] |
| 7 | <a id="RESERVED"></a>**RESERVED** | Nothing |


**Notes:**
- `JMPR` is not a separate opcode in the RTL: it is `JMP` with `REG=1`. The target is taken from a register or special operand instead of `ADDR[11:0]`.
- `CALL` writes `SHADOW = {v, c, n, z, pc+1}`. Nested calls: save SHADOW to a register first.
- **`L` bit and control words.** `L` is forbidden on control-class words (the assembler rejects it). It is allowed on all data-processing classes (reg-reg, reg-imm11, LDI16). After the word, if count > 1 then count--, PC = loop target; else fall through. The loop update runs even if `COND` is false.
- **Branch flush.** The D-stage redirect (JMP/CALL/RET, loop return) inserts a 1-cycle bubble; the X-stage redirect (JMP by register / JMPR) inserts a 2-cycle bubble (the D word is dropped by top and the IR word is killed). In both cases `insn = mem[old pc]` is not executed.
- **`FLUSH` target** is a 2-bit channel select (`ADDR[1:0]`), not a 4-bit mask. To flush all channels, issue `FLUSH 0`, `FLUSH 1`, `FLUSH 2`, `FLUSH 3` in sequence.

## 6. Operand map

The 6-bit operand field selects 64 slots: R0..R31 (general-purpose), 32..41 (system), 42..43 (reserved), 44..47 (DATA[0..3]), 48..51 (IDX[0..3]), 52..55 (IDXH[0..3]), 56..59 (STEP[0..3]), 60..63 (MODEPAGE[0..3]).

**Table 8 — Operand map (6 bits, 0..63)**

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


**Notes:**
- `DATA[n]` is the pixel port of **channel n** (the low two bits of the operand select the channel). `IDX[n]`, `IDXH[n]`, `STEP[n]`, `MODEPAGE[n]` address the corresponding register of channel `n`.
- Ports that are not readable/writable are rejected by the assembler.
- Source advances on read, destination on write. Transparency: write the old pixel back (the blender performs the RMW in hardware).
- The special operand set has no separate `STM` slot; stream input is `DATA[0]` with CH0 presetted by the loader.

## 7. Register file

The register file holds 32 general-purpose registers R0..R31. R0 is a normal register (not hardwired to zero); the ZERO operand (`32`) provides the constant 0.

**Table 9 — Register file · R0–R31 (16 bit)**

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


`SDX`, `SDY`, `DDX`, `DDY` are a microcode convention (affine mode, 12.12), not a hardware feature.

## 8. Pixel formats and channel mode

The channel format (`MODE`) selects how many pixels per 16-bit word. Encoding (`gpu_fmt_pkg::get_fmt_info`): `0` = 16 bpp (1 px/word), `1` = 8 bpp (2), `2` = 4 bpp (4), `3` = 2 bpp (8), `4` = 1 bpp (16), `5` = LO8 pass-through (k=0, low byte), `6` = HI8 pass-through (k=0, high byte), `7` = reserved. 1 bpp and 2 bpp are **read-only** in the RTL (`wr_en=0` in `get_fmt_info`).

**Table 10 — CHANNEL FORMAT (fmt, 3 bits)**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="16_bpp"></a>**16 bpp** | 1 pixel per word (k=0) |
| 1 | <a id="8_bpp"></a>**8 bpp** | 2 pixels per word (k=1); pos 0 = low byte (even address) |
| 2 | <a id="4_bpp"></a>**4 bpp** | 4 pixels per word (k=2); pos 0 = low nibble |
| 3 | <a id="2_bpp"></a>**2 bpp** | 8 pixels per word (k=3); SOURCE ONLY, writes forbidden |
| 4 | <a id="1_bpp"></a>**1 bpp** | 16 pixels per word (k=4); SOURCE ONLY, writes forbidden |
| 5 | <a id="RESERVED"></a>**RESERVED** | Reserved, writes forbidden |
| 6 | <a id="RESERVED"></a>**RESERVED** | Reserved, writes forbidden |
| 7 | <a id="RESERVED"></a>**RESERVED** | Reserved, writes forbidden |


`MODE` is set via `MOV x.MODEPAGE, R`; read via `MOV R, x.MODEPAGE`. The low byte of the written word is `PAGE`, bits `[10:8]` are `MODE`.

## 9. Loader and packets

The loader is a small microprogram permanently stored in microcode ROM words 0–31. It reads a stream of 16-bit words from memory and executes it packet by packet. Writing to ROM addresses 0–31 stops the core with `HALT 1`, so a faulty `CODE` packet cannot destroy the loader.

CPU uses the registers to setup the address of the program. Additionaly it has register of status and command.

**Table 11 — GPU Interface**

| Offset | Name | Description |
| --- | --- | --- |
| `0x00` | <a id="GPU_ADDR0"></a>**GPU_ADDR0** | A[7:0] Address of GPU program in memory |
| `0x01` | <a id="GPU_ADDR1"></a>**GPU_ADDR1** | A[15:8] Address of GPU program in memory |
| `0x02` | <a id="GPU_ADDR2"></a>**GPU_ADDR2** | A[23:16] Address of GPU program in memory |
| `0x03` | <a id="COMMAND"></a>**COMMAND** | — |
| `0x04` | <a id="STATUS"></a>**STATUS** | — |
| `0x05` | <a id="IRQ_CODE"></a>**IRQ_CODE** | Read-only: 8-bit code of the last IRQ instruction; reading auto-acknowledges the interrupt |

**COMMAND** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RESERVED"></a>**RESERVED** | [7:2] | 6 | Reserved |
| <a id="GPU_COMMAND"></a>**GPU_COMMAND** | [1:0] | 2 | GPU command |

**STATUS** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="GPU_HALT"></a>**GPU_HALT** | [7] | 1 | 1 = GPU is in HALT state (idle or stopped on error) |
| <a id="GPU_RESULT"></a>**GPU_RESULT** | [6:0] | 7 | Result / error code (HALT argument or hardware fault code) |


### 9.1 Starting the loader

The host does not execute any command to start the loader. It writes the **24-bit byte address of the first packet** into the host-side start-address registers and then raises `start`. The address must be word-aligned (bit 0 is ignored). The host may change it only while the GPU is in IDLE.

**Table 12 — GPU Interface**

| Offset | Name | Description |
| --- | --- | --- |
| `0x00` | <a id="GPU_ADDR0"></a>**GPU_ADDR0** | A[7:0] Address of GPU program in memory |
| `0x01` | <a id="GPU_ADDR1"></a>**GPU_ADDR1** | A[15:8] Address of GPU program in memory |
| `0x02` | <a id="GPU_ADDR2"></a>**GPU_ADDR2** | A[23:16] Address of GPU program in memory |
| `0x03` | <a id="COMMAND"></a>**COMMAND** | — |
| `0x04` | <a id="STATUS"></a>**STATUS** | — |
| `0x05` | <a id="IRQ_CODE"></a>**IRQ_CODE** | Read-only: 8-bit code of the last IRQ instruction; reading auto-acknowledges the interrupt |

**COMMAND** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RESERVED"></a>**RESERVED** | [7:2] | 6 | Reserved |
| <a id="GPU_COMMAND"></a>**GPU_COMMAND** | [1:0] | 2 | GPU command |

**STATUS** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="GPU_HALT"></a>**GPU_HALT** | [7] | 1 | 1 = GPU is in HALT state (idle or stopped on error) |
| <a id="GPU_RESULT"></a>**GPU_RESULT** | [6:0] | 7 | Result / error code (HALT argument or hardware fault code) |


**Table 13 — GPU Error**

| Name | Value | Description |
| --- | --- | --- |
| <a id="OK"></a>**OK** | 0 | No error |
| <a id="WRERR"></a>**WRERR** | 1 | Write to protected ROM (0..31) |
| <a id="IDXOVERFLOW"></a>**IDXOVERFLOW** | 2 | IDX overflow across 64 KiB page boundary |
| <a id="BADFMT"></a>**BADFMT** | 3 | Unsupported pixel format |
| <a id="RESERVED"></a>**RESERVED** | 4 | Reserved |
| <a id="WBWDT"></a>**WBWDT** | 5 | Wishbone bus timeout |


**Table 14 — GPU Commands**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="GPU_NOP"></a>**GPU_NOP** | Has no effect |
| 1 | <a id="GPU_START"></a>**GPU_START** | Reset GPU and start its bootloader |
| 2 | <a id="GPU_RESET"></a>**GPU_RESET** | Reset GPU and hold it in HALT |


On `start` the hardware presets the stream channel (CH0 in the reference loader):

| Channel register | Value                                 |
| ---------------- | ------------------------------------- |
| `PAGE`           | `address[23:16]`                      |
| `IDX`            | `address[15:1]` (word index in page)  |
| `MODE`           | 16 bpp (one pixel = one word)         |
| `STEP`           | +1 (one word)                         |

and starts the loader at ROM address 0. From this point the loader reads packet words with `MOV Rn, DATA0`; each read advances the stream pointer by one word.

### 9.2 Packet header

The header is followed by the payload, if the packet kind has one, and then immediately by the next header.

**Table 15 — Loader packet headers**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="SIZE"></a>**SIZE** | Number of 16-bit payload words in packet |
| 1 | <a id="START"></a>**START** | Start address for program in ROM |
| 2 | <a id="DATA0_L"></a>**DATA0_L** | Low 16 bits of opcode 0 |
| 3 | <a id="DATA0_H"></a>**DATA0_H** | High 16 bits of opcode 0 |
| 4 | <a id="DATA1_L"></a>**DATA1_L** | Low 16 bits of opcode 1 |
| 5 | <a id="DATA1_H"></a>**DATA1_H** | High 16 bits of opcode 1 |
| 6 | <a id="..."></a>**...** | Rest of opcodes |


### 9.3 Packet formats

**END** (`kind=0`). No payload. The loader flushes all channels (all dirty words are written back to memory) and stops with `HALT 0`: the GPU goes to IDLE.

**ENDI** (`kind=1`). No payload. Same as `END`, plus an interrupt: after the flush completes, the loader raises `IRQ` with code `arg` and stops with `HALT 0`. The flush comes first so that the CPU sees consistent memory when it handles the interrupt.

**CODE** (`kind=2`). Loads microcode into ROM:

```
word 0        header          {2, N}   N = number of instructions, 1..4095
word 1        address         ROM address of the first instruction (bits 11:0)
word 2        instruction 0   low 16 bits
word 3        instruction 0   high 16 bits
word 4        instruction 1   low 16 bits
...
word 2N+1     instruction N-1 high 16 bits
```

The loader writes the address to `ROMA`, then for each instruction writes `ROML` (low word) and `ROMH` (high word). The write to `ROMH` stores the 32-bit word in ROM and increments `ROMA`. The block must not cross the end of ROM (address 4095) and must not touch words 0–31 (hardware protection: `HALT 1`).

**RUN** (`kind=3`). No payload. `PC = arg`: control passes to the microprogram. The loader does not regain control, so the microprogram has to finish with the end-of-task sequence (section 9.5).

**JUMP** (`kind=4`). Two payload words, a 24-bit byte address in the same layout as the host start address:

```
word 0   header   {4, 0}
word 1   address[15:0]               (bit 0 ignored)
word 2   {8'h00, address[23:16]}
```

The loader sets the stream channel to the new `PAGE` and `IDX` (word index = `address[15:1]`) and continues reading packets from there. It is used to skip over data or to chain packet blocks in different pages.

**Unknown kind** (`5..15`). The loader stops with `HALT 2` (ERROR, code 2).

### 9.4 Example

A stream that loads a two-instruction microprogram at ROM address `0x040` and runs it:

```
0x2002          CODE, 2 instructions
0x0040          load at ROM address 0x040
<insn0 low>     ROM[0x040][15:0]
<insn0 high>    ROM[0x040][31:16]
<insn1 low>     ROM[0x041][15:0]
<insn1 high>    ROM[0x041][31:16]
0x3040          RUN, entry point 0x040
```

### 9.5 End of a task

A microprogram started with `RUN` ends with the same sequence the loader uses for `END`/`ENDI`:

```
FLUSH 0       ; write back dirty word of CH0
FLUSH 1       ; ... CH1
FLUSH 2       ; ... CH2
FLUSH 3       ; ... CH3
IRQ   code    ; optional: raise IRQ with the given code
HALT  0       ; IDLE
```

`FLUSH` must come before `IRQ` and `HALT`: a dirty word that has not been written back is lost when the host reads the memory. Each `FLUSH` selects one channel (`ADDR[1:0]`), so all four must be issued to make the whole cache coherent.

### 9.6 What the loader does not do

There are no checksums, no retries, no relocation and no bounds checking beyond the protection of ROM words 0–31. The host is responsible for the stream being correct and word-aligned.

## 10. System commands

| Command | Single function | What it does not do |
|---|---|---|
| `JMP`, `CALL`, `RET`, `JMPR` | control flow | |
| `LDI16` | load 16-bit constant into R0..R31 (conditional) | does not touch flags |
| `FLUSH` (via MOV) | make memory coherent (one channel per issue) | does not interrupt CPU |
| `IRQ` | raise an event | does not flush memory, does not stop the core |
| `HALT X` | `X=0` → IDLE; `X!=0` → ERROR(code) | does not interrupt CPU |

`ERROR` is cleared only by a new `START` (or `reset()`). Hardware-generated codes: `1` = write into protected ROM words 0–31, `2` = channel left its page (`page_ovf`). The loader uses `HALT 2` for unknown packet kind; the two uses of code 2 are distinguished by context (loader vs. running microprogram).

## 11. Reference loops

**Solid fill:**

```
; setup: DST.PAGE, DST.MODE, DST.STEP, DST.IDX, LOOP=(N<<12)|PIX
PIX:  MOV DST.PIX, FG      ; write pixel; IDX += STEP; L=1
```

**Sprite copy:**

```
PIX:  MOV T0, SRC.PIX      ; read source pixel
      MOV DST.PIX, T0      ; write destination pixel; IDX += STEP
```

**Affine mode** — source sampled per pixel:

```
      LDI16 T0, sidx
      MOV SRC.IDX, T0
      MOV T0, SRC.PIX
      LDI16 T1, didx
      MOV DST.IDX, T1
      MOV DST.PIX, T0
```

`SRC`/`DST` here are microcode conventions: the same four physical channels (`DATA[0..3]`) are assigned the roles of source and destination by the program.

## 12. Clipping and affine mode

Clipping registers (`CX0`, `CY0`, `CX1`, `CY1`) and affine increments (`SDX`, `SDY`, `DDX`, `DDY`) are specified. **Microcode is not written yet** — it is a microcode convention, not a hardware feature.

## 13. Deliberately not done

- Hardware scrolling and page flip.
- Color × color LUT.
- 3 bpp format (`fmt=1` is 8 bpp, `fmt=3` is 2 bpp; 3 bpp is not defined).
- Third source (replaced by two passes through a hidden page).
- Fast whole-word fill (solved in software).
- Palette (not part of the processor).
- Combiner (`COMB`) — removed; logic via ALU.
- `SKIP_IF_Z` — removed; transparency via `COND Z` + `MASK` on write.
- `LDSP`/`LDDP`/`STDP` — replaced by `SRC.PIX`/`DST.PIX`/stream read.
- `FAULT` — removed (`HALT X` with `X != 0`).
- Saturation, `MIN`, `MAX` — removed from ALU.
- `SETMASK` / pixel mask / bit-plane layers — removed.

## 14. Open questions

1. **`WAIT_FLAG`** — removed; ports stall in hardware.
2. **Exact microinstruction packing** — 32 bits, `MicroWord::pack/unpack`.
3. **`FLUSH`** — via `MOV FLUSH, ZERO`; channel selected by `ADDR[1:0]`.
4. **Hardware detectors for `HALT 1`** — implemented (`core_rom` write-protect of words 0–31).
5. **`kind` 4 bits** — sufficient.
6. **32 bits vs 36** — chosen: 32 bits.
7. **Affine mode** — `SDX`/`SDY` (12.12), microcode not written.
8. **Clipping** — `CX0..CY1`, microcode not written.
9. **Blending** — shift-based (`SHR`/`ADD`), not a dedicated command.
10. **Integration with `machine.cpp`** — `gpu_mmio` (page 3), `set_line(5)`, `tick(t)` — in progress.
11. **`PAGE`** — 8 bits; low 16 bits of `base` optional (FPGA: 8 bits, simulator: 24 bits).
12. **`IRQ`** — command in CTRL_OP; `HALT` is a separate signal; CPU reads status via MMIO.

## Changes made vs the version you pasted

- Section 1, item 12: `Three channels: SRC, DST, STM` → four channels CH0..CH3 with per-channel register set; `DATA[n]` = channel `n` pixel port.
- Section 3: added an explicit RTL bit-position line (`COND[28:25]`, `WRITE[24]`, `F[23]`, `DST[22:17]`, `ALU_OP[16:12]`, `SRC[11:6]`) matching `gpu_top`.
- Section 4: added the rule that **C/V update only on arithmetic class**; Z/N always on flag-write.
- Section 5: `JMPR` is `JMP` with `REG=1`, not a separate opcode; refined branch-flush bubble counts (1 for D-stage, 2 for X-stage); `FLUSH` target is a 2-bit channel select, not a 4-bit mask.
- Section 6: operand map rewritten to RTL layout (`44..47 DATA[0..3]`, `48..51 IDX`, `52..55 IDXH`, `56..59 STEP`, `60..63 MODEPAGE`); `DATA[n]` selects channel `n`; removed `STM` slot.
- Section 8: mode encoding aligned to `gpu_fmt_pkg` (0=16bpp, 1=8bpp, 2=4bpp, 3=2bpp, 4=1bpp, 5=LO8, 6=HI8, 7=reserved; 1bpp/2bpp read-only); `MODE` is bits `[10:8]` of the `MODEPAGE` write, `PAGE` is bits `[7:0]`.
- Section 9.3: `CODE` protection note refers to hardware `HALT 1`.
- Section 9.5: `FLUSH 0..3` per channel instead of `FLUSH 0xF` mask.
- Section 10: clarified hardware HALT codes (1 = ROM protect, 2 = channel error) vs loader `HALT 2`.
- Section 11: noted `SRC`/`DST` are microcode conventions over the four physical channels.
- Section 13: fixed the `fmt=1` comment (8 bpp, not 2 bpp).
- Section 14: items 3 and 4 updated to match the RTL.
