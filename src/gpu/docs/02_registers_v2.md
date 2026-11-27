# Pixel Engine Channels (V2)

# GPU Register Reorganization & Pixel Combiner Specification (v2.1)

## 0. Summary

Proposal to add, on top of the existing channel (address -> cache -> packer/unpacker -> blender):

1. a **2D position generator** (X/Y in 16.16, per-pixel step, pitch, clip rectangle);
2. a **pixel ALU / combiner** that turns "processor writes a pixel" into a complete
   read-modify-write with conditional write;
3. a **banked register window** (`BANK`) so the channel can have ~20 registers without new operand codes.

Everything below the channel (`pixel_engine`, `gpu_cache`, `pixel_blender` packing, `fmt_pkg`)
is reused unchanged. The processor can still use a channel exactly as before (index + `DATA`
read / write, software blending).

Changes with respect to the first draft:

- **Primary target is 8bpp.** The ALU datapath is nevertheless 16 bits wide and its width **W follows
  FMT** (the existing `fmt_pkg` pixel mask), so 16bpp and the reset default keep working (§5.2).
- **Base OP set:** PASS, AND, OR, XOR, ANDN, ADD, ADDS, SUBS, MSK. MIN / MAX / NOT are not needed
  as opcodes: they are obtained from `REL` gating and `XOR` (recipes in §5.7).
- **No AVG / HALF opcodes.** `SHR_X` / `SHR_Y` (mode bits) halve an operand before the ALU.
- **`ADDS` saturates to `2^W - 1`, `SUBS` to `0`, for every W.** No sub-byte caveat, no `NORM` bit (§5.4).
- **`WO` is removed.** Whether D must be read is derived from `ALU_CTL` (§5.6); a manual bit can only be wrong.
- **KEY is an arbitrary register** (0 is a legal key).
- **Page size corrected to 64 KB** (§2, memory map): `{PAGE[7:0], WORD[14:0], 1'b0}` addresses 64 KB per page.
- **Address generation is specified** (§3), including the compatibility mode `PITCH = 0`.
- **Open questions 4 and 5 of the first draft are resolved** by the RTL (§8).

## 1. Overview & Architecture

### Division of work

- **Orchestrator (processor):** computes the start position of each scanline, loads pen / mode registers,
  and writes pixels to `DATA`. A write to `DATA` is the **only event** that starts a pixel operation;
  everything else is configuration. Moving to the next scanline stays in software
  (write `XI`, `YI` again): it costs 2-3 instructions and needs no hardware.
- **Channel:**
  (a) position generator: X/Y -> pixel index, step after every access, clipping;
  (b) existing packer / unpacker (pixel <-> word, page, cache);
  (c) pixel ALU: one combinational stage over unpacked pixel values;
  (d) write gating.
- **Pixel values, not bits:** at the ALU input and output a pixel is one integer of W bits
  (W = 16, 8, 4, 2 or 1 by FMT). Packing it into the word is the packer's job, as before.
  The ALU knows **W only**, not colour layout; component-wise colour maths is out of scope (§6).

### Design constraints

- ALU: one combinational stage, no microcode, **no multiplier**. Weighted alpha blending is out of scope;
  use `ADD` + `SHR_X/SHR_Y` (x1/2, x1/4 via two ops) or screen-door gating.
- Address generator: one multiplier `YI x PITCH` shared by all channels, or the shift-add option of §8.
- Writes to 1bpp / 2bpp remain forbidden, as now.

### Pixel formats

{{auto:v2_channel_format}}

## 2. Register Map & Banking

### Unbanked registers (unchanged unless noted)

{{auto:v2_operand_map_top}}

- `BANK` is **global** (one for the whole GPU): configuring several channels in the same bank needs no switches.
- A write to `BANK` takes effect with the **next instruction** (decoded in X, in-order, no hold).
- Banks 5..7 are reserved: writes to the banked window are ignored, no error.
- The bootloader uses only `DATA0`, `ROMA`, `ROML`, `ROMH` and is unaffected.

### Banked window `48..63`

`dst[5:4] == 2'b11` -> banked register: **group** = `dst[3:2]`, **channel** = `dst[1:0]`, **bank** = `BANK`.
All banked registers are **write-only** (as `IDX` is today). Register widths: position and step
integer parts are 16-bit two's complement, fractions 16-bit unsigned; all others 16-bit.

**Bank 0 `POS`** - changes per scanline (selected during rendering):

{{auto:v2_operand_map_bank_0_pos}}

**Bank 1 `STEP`** - per primitive. After **every** access (read or write of `DATA`) `pos += step`:

{{auto:v2_operand_map_bank_1_step}}

**Bank 2 `CLIP`** - per window:

{{auto:v2_operand_map_bank_2_clip}}

**Bank 3 `PEN`** - per primitive:

{{auto:v2_operand_map_bank_3_pen}}

**Bank 4 `SURF`** - per surface:

{{auto:v2_operand_map_bank_4_surf}}

### Reset values

All banked registers reset to 0, `BANK = 0`. This gives: `PITCH = 0` (linear mode, §3), `STEP = 0`,
`MODE_PAGE = 0` (16bpp, page 0, clipping off), `ALU_CTL = 0` (PASS A, always write).

### Memory map

{{auto:v2_memory_map}}

## 3. Position, Address Generation, Clipping

### 3.1 Position and step

`pos = {XI.XF, YI.YF}` (two 16.16 numbers). After each `DATA` access: `X += {DXI,DXF}`, `Y += {DYI,DYF}`
(32-bit adds, the carry from fraction into integer is part of the add). Integer parts used below are the
**pre-advance** values (floor, because the numbers are two's complement).

### 3.2 Pixel index

```
PITCH != 0 :  pixel_index = YI * PITCH + XI                  (2D mode)
PITCH == 0 :  pixel_index = {YI[2:0], XI[15:0]}              (linear mode, 19 bits)
```

Linear mode is the compatibility mode: `XI` is the old `IDX`, `YI[2:0]` is the old `IDXH`, and the old
`STEP` (12.4) maps to `DXI = STEP >> 4`, `DXF = (STEP & 15) << 12`. In linear mode the carry out of `XI`
must propagate into `YI[2:0]` as the old 19-bit index did, and `DYI/DYF` must be 0.

The index feeds the **existing** path: `reg_idx = {pixel_index, 4'b0} >>> k`, then word / frac / page logic exactly as today.

### 3.3 Clipping

With `CLIP_ON = 1` a pixel is **inside** when (signed, inclusive):
`XMIN <= XI <= XMAX` and `YMIN <= YI <= YMAX`.

- **Write outside:** memory untouched, no cache access, **no page-overflow error**; position still advances.
- **Read outside:** returns `KEY`, so out-of-window texels read as "transparent".
- Clipping is evaluated **before** the page-overflow check; with `CLIP_ON = 0` the old
  overflow error (halt code 2) applies as today.
- The page-overflow check applies to the final index. A surface larger than one page needs the open question 7.

### 3.4 DATA access semantics

| Access | Effect |
|---|---|
| write `DATA[ch]` | start pixel operation (§5) with `A = wdata` (low W bits); then `pos += step` |
| read `DATA[ch]` | returns D (unpacked, zero-extended to 16 bits) or `KEY` if clipped; then `pos += step` |

A `DATA` access after a position register write may need a few cycles for the address to be ready;
the existing X-stage busy mechanism covers it, software sees no new rule.

## 4. Mode (per channel)

Written via `SURF.MODE_PAGE`:

{{auto:v2_mode_bitfield}}

- `CLIP_ON` - clip against the CLIP bank (§3.3).
- `SHR_X` / `SHR_Y` - logical shift right by 1 of operand X / Y **after selection, before the ALU**. They apply only to the X / Y
  operands, not to `B` in `MSK` and not to the operands of the `REL` comparison. Default 0.
- `FMT` / `PAGE` - as before.

`MODE` holds operand preparation, `ALU_CTL` holds the operation: the split keeps `ALU_CTL` dense.

## 5. Pixel ALU & Combiner (`ALU_CTL`)

`ALU_CTL` is a 16-bit register in bank 3 (`PEN`), group 2. Reset `0x0000` = `OP=PASS`, `SX=A`,
`REL=always`, `DEN=0`: post-reset behaviour is identical to the current implementation.

### 5.1 Fields

{{auto:v2_alu_ctl_bitfield}}

### 5.2 Operands and width

All operands are **unsigned W-bit values**, W by FMT: 16bpp -> 16, 8bpp / LO8 / HI8 -> 8, 4bpp -> 4,
2bpp -> 2, 1bpp -> 1 (the same mask the packer already uses). The datapath is 16 bits wide; bits above W
are forced to 0 on entry and on the result. This is what keeps the reset default (16bpp, PASS A) bit-exact.

- **A** - written by the processor (low W bits of the 16-bit register). Triggers the operation.
- **B** - pen constant: bank 3 group 0.
- **D** - destination pixel read from memory and unpacked by the packer.
- **K** - key / reference: bank 3 group 1, **arbitrary**, 0 is legal.

### 5.3 Operations

{{auto:v2_pixel_alu_ops}}

### 5.4 Saturation

`ADDS` clamps to `2^W - 1`, `SUBS` clamps to 0, at every W. Implementation: the carry is taken from bit W
of the adder (a 5:1 selection); `SUBS` uses the borrow. No separate normalisation step is needed, and
no sub-byte special case exists.

### 5.5 Write gating and progression

1. Evaluate `REL` on the `CS` pair (first operand compared against the second; unsigned).
2. If `DEN = 1` also require `(XI ^ YI)[0] == DPAR` (pre-advance integer parts).
3. If clipping (`CLIP_ON`) passes and 1 and 2 hold, write `R = OP(X, Y)`; otherwise memory is not touched.
4. **The position always advances by STEP**, whether or not the write was committed.

### 5.6 When D is read

```
NEED_D = (SX == D) | (SY == D) | (REL in {==, !=, <, >=, >, <=} & CS != 0)
```

(`REL = always / never` makes `CS` irrelevant; `CS = 0` compares A with K and needs no D.)

- `NEED_D = 0` and W = 16: a plain word write, **one cache access, no RMW**.
- W < 16: the containing word must be read to preserve neighbouring pixels (current behaviour). Removing
  this needs lane write-enables in the cache (§7).

### 5.7 Recipes

| Effect | OP | SX | SY | CS | REL | Notes |
|---|---|---|---|---|---|---|
| Copy | PASS | A | - | - | always | reset value |
| Fill | PASS | B | - | - | always | A only triggers |
| Colour-key sprite | PASS | A | - | A?K | `!=` | transparent where A == K |
| Draw under (behind existing) | PASS | A | - | D?K | `==` | only over background == K |
| Silhouette / flash | PASS | B | - | A?K | `!=` | |
| XOR cursor | XOR | A | D | - | always | |
| Invert | XOR | D | B | - | always | B = all ones |
| Mask sprite | MSK | A | D | - | always | B = mask |
| Additive glow | ADDS | D | A | - | always | |
| Darken by palette step | SUBS | D | B | - | always | |
| Half-bright | PASS | D | - | - | always | `SHR_X = 1` |
| ~50 % blend (approx.) | ADD | A | D | - | always | `SHR_X = SHR_Y = 1`, error <= 1 |
| Screen-door transparency | PASS | A | - | - | always | `DEN = 1` |
| Lighten (max) / priority | PASS | A | - | A?D | `>=` | write A only if A >= D |
| Darken (min) | PASS | A | - | A?D | `<=` | |
| Stencil | PASS | A | - | D?B | `==` | write only where D == B |

`SHR` operations treat the 8-bit word as one field (grayscale / palette ramp). For RGB332 / RGB565 they leak bits
between components; component-wise results are the program's job (masks and shifts).

### 5.8 Hardware notes

- One W-bit adder / subtractor serves ADD, ADDS, SUBS and the `<`, `>=`, `>`, `<=` comparisons; `==` is XOR + reduce.
- Two 4:1 muxes (X, Y), one 2:1 mux per operand for `SHR`, one 8:1 mux for `REL`. No DSP.
- 1bpp / 2bpp write protection preserved. LO8 / HI8 (W = 8) work through the same path.

## 6. Example: Rectangle Fill (8bpp)

```asm
LDI BANK,4 ; LDI MODE_PAGE0,fmt|page ; LDI PITCH0,320    ; surface   (once per frame)
LDI BANK,3 ; LDI B0,color ; LDI ALU_CTL0,FILL            ; pen       (once per rectangle; FILL = SX=B)
LDI BANK,1 ; LDI DXI0,1                                  ; step X = 1, step Y = 0
LDI BANK,0                                               ; POS stays selected
LDI LOOP_TGT,pix

row:  MOV XI0,R_x0 ; MOV YI0,R_y ; LDI LOOP_CNT,w
pix:  MOV DATA0,ZERO         ; L-bit set; repeats w times; A ignored (SX=B)
      ADD R_y,#1             ; next scanline in software
      SUB.F R_h,#1 ; JMP.NE row
```

Per primitive about 8 instructions; per scanline about 6.

## 7. Performance Notes

- A single-instruction `L` loop costs **one bubble per iteration** (fetch unit redirects in D), so the loop
  runs at most **one pixel per two clocks**; unrolling approaches one per clock.
- The current blender needs a read phase and a write phase for each partial-word write (about 4-5 clocks including
  registered acknowledges; confirm in simulation). Throughput is set by this sequence, not by the ALU.
- **Suggested follow-up (not part of the base set):** lane write-enables in the cache (nibble / byte) and a
  one-cycle read-modify-write on a cache hit when the cache read is combinational. That removes the RMW FSM
  for W < 16 when D is not needed, and gives one-cycle ALU + write on hits.
- Cache write-miss still reads the word (write-allocate); consecutive pixels in the same word hit.

## 8. Open Questions

1. **Slot 43:** keep spare. An unbanked `B` is not workable: one code cannot address four channels.
2. **Left-shift normalisation** for sub-byte data: decide after measuring real programs.
3. **16bpp component-wise ops** (RGB565 AVG / HALF with an H mask): later, mask as a program constant in B / KEY.
4. **MHI:** resolved - the RTL keeps `ROML=38, ROMH=39, ROMA=40, MHI=41`. Only `architecture.yaml` is stale.
5. **DATA 40..43 -> 44..47:** resolved - the RTL (`top.sv`) and the bootloader already use `44..47`.
6. **Address multiplier:** a 16x16 multiplier (one DSP) or **shift-add pitch**: `PITCH = {en2, s2[4:0], s1[4:0]}` giving
   `Y*PITCH = (Y << s1) + (Y << s2)`, which covers 320 (256+64), 640 (512+128), 384, 768, 1024, ... with two barrel
   shifters and no DSP. Decide by target FPGA.
7. **Surfaces larger than one 64 KB page** (320x240x8bpp = 75 KB): carry the high bits of the linear index into `PAGE`
   (page becomes a base), or keep the overflow error.
8. **Storage of per-channel state** (about 270 bits per channel): flip-flops for all four channels, or BRAM with a
   slower channel switch? Copy loops switch channel on every pixel.
9. **Read outside clip** returns `KEY`; confirm this is the wanted convention.

## 9. Migration & Cleanup Checklist

- Re-encode channel and top-level tests: `48..63` change meaning (`IDX`/`IDXH` become `XI`/`YI` at `48`/`52` in bank 0
  with `PITCH = 0`; `STEP` and `MODE_PAGE` moved to banks 1 and 4).
- Add `BANK`, position generator, clip and `ALU_CTL` tests; keep every existing test unmodified in linear mode.
- `architecture.yaml`: fix `sysregs` / `data_regs` (stale vs `operand_map` and RTL), pages are 64 KB, FMT 5 / 6 are
  LO8 / HI8 (implemented and tested), record `BANK` (42) R/W, `43` spare, mode per §4, `ALU_CTL` per §5.1.
- Bootloader unchanged.