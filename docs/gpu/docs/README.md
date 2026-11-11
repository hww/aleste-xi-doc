# LX-GPU

A programmable 2D graphics coprocessor for the Z80, with a behavioural C++ simulator used to validate the architecture before writing RTL.

The core is a stack-based (A/B/C) machine with 36-bit microcode, four logical pixel channels (SOURCE, DEST, DATA, RSV), a word-level pixel buffer, an address generator with an embedded DSP, and four pixel formats (1/4/8/16 bpp). It is designed to be simple, programmable, and cheap in FPGA resources — not fast. Memory is the bottleneck; everything else is kept small.

See the documents below for the full architecture, the pixel buffer, and worked examples.

## Architecture

- [`01_architecture.md`](01_architecture.md) — microinstruction format, stack A/B/C, ALU, addressing, device map, loader, reference loops.
- [`02_pixel_buffer.md`](02_pixel_buffer.md) — four-entry word buffer, TAG/VALID/DIRTY, hit/miss, page switching.

## Worked examples

- [`03_draw_sprite.md`](03_draw_sprite.md) — sprite with affine transform (rotation, scale).
- [`04_fill_rect.md`](04_fill_rect.md) — rectangle fill.
- [`05_copy_transparent.md`](05_copy_transparent.md) — sprite copy with colour-key transparency.

## Microcode reference

YAML declarations in `gen/` produce the SVG diagrams and MD tables included in the documents above:

- [`gen/microinstruction.yaml`](gen/microinstruction.yaml) — 36-bit microinstruction layout.
- [`gen/microops_reg.yaml`](gen/microops_reg.yaml) — `REG_OP`, 5 bits, 32 codes (stack + data).
- [`gen/microops_alu.yaml`](gen/microops_alu.yaml) — `ALU_OP`, 5 bits, 32 codes (16 LOGIC LUT + ADD/SUB/CMP/shifts).
- [`gen/microops_ctrl.yaml`](gen/microops_ctrl.yaml) — `CTRL_OP`, 3 bits, 8 codes (flow control).
- [`gen/microops_cond.yaml`](gen/microops_cond.yaml) — `COND`, 3 bits, 8 conditions.
- [`gen/microops_mask.yaml`](gen/microops_mask.yaml) — `MASK`, 3 bits (block REG/ALU/CTRL).
- [`gen/device_map.yaml`](gen/device_map.yaml) — devices reachable via `LDX`/`STX`/`WAIT_FLAG` (0..31).
- [`gen/registers.yaml`](gen/registers.yaml) — register file R0..R31.
- [`gen/channel_mode.yaml`](gen/channel_mode.yaml) — pixel formats per channel (`fmt` 0..7).
- [`gen/commands.yaml`](gen/commands.yaml) — loader packet headers.

## Simulator

The C++ behavioural model lives in `src/` (or `emulator/lx/gpu/`):

- `gpu.h` / `gpu.cpp` — core: microcode execution, stack A/B/C, ALU, control flow.
- `pixel_packer.h` / `.cpp` — pixel ↔ word packing for each `fmt`.
- `pixel_buffer.h` / `.cpp` — four-entry word cache.
- `addr_packer.h` / `.cpp` — coordinate → address translation (with DSP).
- `memory.h` / `.cpp` — 16-bit word access over a 24-bit address space.
- `gpu_mmio.h` / `.cpp` — MMIO bridge (page 3) for the host machine.
- `main.cpp` — 12 behavioural tests.

Build and run:

```
make
./sim
```

The simulator is not cycle-accurate. It validates the computational model: whether the instruction set, the registers, and the address generator are sufficient for the intended effects (fill, sprite copy, affine transform, transparency). Timing, latency, and pipeline hazards are deferred to RTL.

## What is intentionally not done

- Hardware scrolling, page flip.
- Colour × colour LUT.
- 2 bpp / 3 bpp formats.
- A third source channel.
- Saturation (`ADDS`/`SUBS`), `MIN`/`MAX`, `MUL` in the ALU.
- The combiner (`COMB`), `SKIP_IF_Z`, `SETMASK`, pixel mask.
- Bit-plane layers.

Blending and proportional mixing are done with shifts. Multiplication lives in the address generator, not in the ALU.

## Status

Architecture stable; 12 behavioural tests passing. Next steps: clipping microcode, affine microcode, YAML consistency, integration with the host emulator (`machine.cpp`), then RTL.
