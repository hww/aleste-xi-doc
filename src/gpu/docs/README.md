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
