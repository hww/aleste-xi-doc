# Specification index

## bitfield

- [EXTPORT (FABF) — 520EX Extension](L_520EX_EXTPORT.md) — `L_520EX_EXTPORT`
- [Gate Array R0 — Palette Index](L_GA_R0.md) — `L_GA_R0`
- [Gate Array R2 — Mode, ROM Enable, LEDs](L_GA_R2.md) — `L_GA_R2`
- [MMR — RAM Memory Mapping](L_MMR.md) — `L_MMR`
- [8255 PPI Port A — PSG Data Bus](L_PPI_PORTA.md) — `L_PPI_PORTA`
- [8255 PPI Port B — VSYNC, Cassette, Printer](L_PPI_PORTB.md) — `L_PPI_PORTB`
- [8255 PPI Port C — PSG Control, Cassette, Keyboard](L_PPI_PORTC.md) — `L_PPI_PORTC`
- [RMR — Control, ROM Mapping, Graphics Mode](L_RMR.md) — `L_RMR`
- [GLOBAL_CTRL (F0h)](mmu_global_ctrl.md) — `mmu_global_ctrl`

## enum

- [Gate Array register select (D7, D6)](L_GA_REGS.md) — `L_GA_REGS`
- [PPI Manufacturer Bits (Port B bits 3–1)](L_PPI_MFG.md) — `L_PPI_MFG`
- [PSG function select (BDIR, BC1)](L_PSG_SELECT.md) — `L_PSG_SELECT`
- [Blitter Modes (CTRL[2:1])](dma_blitter_modes.md) — `dma_blitter_modes`
- [SysDMA Transfer Modes](dma_sysdma_modes.md) — `dma_sysdma_modes`
- [CRTC 6845 Ports](io_crtc_ports.md) — `io_crtc_ports`
- [FDC 765 Ports](io_fdc_ports.md) — `io_fdc_ports`
- [Gate Array Register Select (7Fxx)](io_ga_regs.md) — `io_ga_regs`
- [Legacy Software CAN](io_legacy_can.md) — `io_legacy_can`
- [Legacy Software CANNOT](io_legacy_cannot.md) — `io_legacy_cannot`
- [Legacy Device Sub-registers](io_legacy_devices.md) — `io_legacy_devices`
- [MMIO_LO Page Map](io_mmio_pages.md) — `io_mmio_pages`
- [MMIO Regions](io_mmio_regions.md) — `io_mmio_regions`
- [Native Mode Port Map](io_native_ports.md) — `io_native_ports`
- [PPI 8255 Ports](io_ppi_ports.md) — `io_ppi_ports`
- [native_mode (GLOBAL_CTRL[1])](native_mode_vals.md) — `native_mode_vals`
- [supervisor_mode (GLOBAL_CTRL[0])](supervisor_mode_vals.md) — `supervisor_mode_vals`

## regmap

- [Blitter Register Map (lx_dma.sv)](dma_blitter_map.md) — `dma_blitter_map`
- [SysDMA Register Map (wb_dma.sv)](dma_sysdma_map.md) — `dma_sysdma_map`
- [MMU Registers (Ports E0–FF)](io_mmu_ports.md) — `io_mmu_ports`
- [Internal Mapper Registers (16 × 8-bit)](mmu_mapper_regs.md) — `mmu_mapper_regs`
- [Control Registers (Ports F0–FF, E0–EF)](mmu_ports.md) — `mmu_ports`
- [PIC Register Map (wb_z80_pic.sv)](pic_regmap.md) — `pic_regmap`

## memmap

- [Logical Slots](io_slots.md) — `io_slots`
- [Logical Slots (16-bit Z80 address space)](mmu_slots.md) — `mmu_slots`

