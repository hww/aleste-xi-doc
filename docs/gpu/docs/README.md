# LX-GPU

A programmable 2D graphics coprocessor for the Z80. It has a 16-bit microcore, four logical pixel channels (SRC, DST, STM, plus reserved), a word-level cache, and five pixel formats (1, 2, 4, 8, 16 bpp). Designed to be simple, programmable, and cheap in FPGA resources — not fast. Memory is the bottleneck; everything else is kept small.

## Architecture

- [00_history.md](00_history.md) — the philosophy of programmable graphics.
- [01_architecture.md](01_architecture.md) — microinstruction format, ALU, control, operand map, register file, pixel formats, loader, reference loops.
- [02_registers.md](02_registers.md) — GPRs, system registers, pixel engine channels, DATA.
- [03_isa.md](03_isa.md) — instruction format, ALU/CTRL opcodes, conditions.
- [04_memory.md](04_memory.md) — memory map, ROM, cache, Wishbone.
- [05_pixel_engine.md](05_pixel_engine.md) — pixel formats, index/step, pixel path, timing.
- [06_gpu_cache.md](06_gpu_cache.md) — cache structure, FSM.
- [07_fpga_top.md](07_fpga_top.md) — block diagram, execution protocol.

## Architecture (Russian)

- [00_history.ru.md](00_history.ru.md) — the philosophy of programmable graphics.
- [08_guide.ru.md](08_guide.ru.md) — user guide.

## What is intentionally not done

- Hardware scrolling, page flip.
- Saturation (`ADDS`/`SUBS`), `MIN`/`MAX`.
- The combiner (`COMB`), `SKIP_IF_Z`, `SETMASK`, pixel mask.
- Bit-plane layers.

Blending and proportional mixing are done with shifts. Multiplication lives in the ALU, not in a separate unit.

## Status

Architecture stable. Next steps: clipping microcode, affine microcode, YAML consistency, integration with the host emulator (`machine.cpp`), then RTL.