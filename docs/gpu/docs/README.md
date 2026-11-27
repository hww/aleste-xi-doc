# LX-GPU

A programmable 2D graphics coprocessor for the Z80. It has a 16-bit microcore, four logical pixel channels (SRC, DST, STM, plus reserved), a word-level cache, and five pixel formats (1, 2, 4, 8, 16 bpp). Designed to be simple, programmable, and cheap in FPGA resources — not fast. Memory is the bottleneck; everything else is kept small.

## Architecture

- [Philosophy](00_history.md) — the philosophy of programmable graphics.
- [Microinstruction](01_architecture.md) — microinstruction format, ALU, control, operand map, register file, pixel formats, loader, reference loops.
- [Registers](02_registers.md) — GPRs, system registers, pixel engine channels, DATA.
- [Channels V1](02_channels_v1.md) — GPRs, system registers, pixel engine channels, DATA (version 1).
- [Channels V2](02_channels_v2.md) — GPRs, system registers, pixel engine channels, DATA (version 2).
- [Instruction format](03_isa.md) — instruction format, ALU/CTRL opcodes, conditions.
- [Memory map](04_memory.md) — memory map, ROM, cache, Wishbone.
- [Pixel engine](05_pixel_engine.md) — pixel formats, index/step, pixel path, timing.
- [Cache](06_gpu_cache.md) — cache structure, FSM.
- [FPGA top](07_fpga_top.md) — block diagram, execution protocol.
- [Retro GFX](09_retro_gfx_rev2.md) - retro graphics effects: technical reference

## Testing

- [Demo Scenario](./10_demo_sceenario.md) - GPU Demo and Benchmark Scenario.
- [Demo Source Code](https://github.com/hww/aleste-xi-bio.../main/dos/demo) - The source code of the demo.

## Architecture (Russian)

- [История](00_history.ru.md) — the philosophy of programmable graphics.
- [Архитектура](08_guide.ru.md) — user guide.

## What is intentionally not done

- Hardware scrolling, page flip.
- Saturation (`ADDS`/`SUBS`), `MIN`/`MAX`.
- The combiner (`COMB`), `SKIP_IF_Z`, `SETMASK`, pixel mask.
- Bit-plane layers.

Blending and proportional mixing are done with shifts. Multiplication lives in the ALU, not in a separate unit.

## Status

Architecture stable. Next steps: clipping microcode, affine microcode, YAML consistency, integration with the host emulator (`machine.cpp`), then RTL.