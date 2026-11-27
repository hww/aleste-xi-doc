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
- [PRIO[ch] · 8 bits](dma_prio.md) — `dma_prio`
- [I2C_CMD · 8 bits (a write starts the operation)](i2c_cmd.md) — `i2c_cmd`
- [I2C_CTRL · 8 bits](i2c_ctrl.md) — `i2c_ctrl`
- [I2C_STATUS · 8 bits](i2c_status.md) — `i2c_status`
- [GLOBAL_CTRL (F0h)](mmu_global_ctrl.md) — `mmu_global_ctrl`
- [SLOTn_CTRL · 8 bits](slot_ctrl.md) — `slot_ctrl`
- [SLOTn_STAT · 8 bits](slot_stat.md) — `slot_stat`
- [SPIn_CMD · 8 bits (write-only; START launches a job)](spi_cmd.md) — `spi_cmd`
- [SPIn_CTRL · 8 bits](spi_ctrl.md) — `spi_ctrl`
- [SPIn_STATUS · 8 bits](spi_status.md) — `spi_status`
- [Timer F6 bit layout](timer_f6_bits.md) — `timer_f6_bits`

## enum

- [Gate Array register select (D7, D6)](L_GA_REGS.md) — `L_GA_REGS`
- [PPI Manufacturer Bits (Port B bits 3–1)](L_PPI_MFG.md) — `L_PPI_MFG`
- [PSG function select (BDIR, BC1)](L_PSG_SELECT.md) — `L_PSG_SELECT`
- [SysDMA channel allocation](alex_dma_channels.md) — `alex_dma_channels`
- [SPI transfer modes (SPI_CMD.MODE)](alex_spi_modes.md) — `alex_spi_modes`
- [SysDMA arbitration rules](dma_arb.md) — `dma_arb`
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
- [Open items](open_items.md) — `open_items`
- [PIC COMMAND opcodes (bit7 = 0)](pic_command_ops_v2.md) — `pic_command_ops_v2`
- [Connector zones and placement rules](slot_zones.md) — `slot_zones`
- [SysDMA bus load of one duplex SPI slot](spi_load.md) — `spi_load`
- [supervisor_mode (GLOBAL_CTRL[0])](supervisor_mode_vals.md) — `supervisor_mode_vals`

## regmap

- [SysDMA extension registers (ASSUMPTION: offset 0x50 is free)](alex_dma_ext.md) — `alex_dma_ext`
- [I2C controller registers (one controller, four-slot multiplexer)](alex_i2c.md) — `alex_i2c`
- [Slot control registers](alex_slots.md) — `alex_slots`
- [SPI controller registers (four instances, one per slot)](alex_spi.md) — `alex_spi`
- [Blitter Register Map (lx_dma.sv)](dma_blitter_map.md) — `dma_blitter_map`
- [SysDMA Register Map (wb_dma.sv)](dma_sysdma_map.md) — `dma_sysdma_map`
- [MMU Registers (Ports E0–FF)](io_mmu_ports.md) — `io_mmu_ports`
- [Internal Mapper Registers (16 × 8-bit)](mmu_mapper_regs.md) — `mmu_mapper_regs`
- [Control Registers (Ports F0–FF, E0–EF)](mmu_ports.md) — `mmu_ports`
- [PIC Register Map (wb_z80_pic.sv)](pic_regmap.md) — `pic_regmap`
- [PIC Register Map (lx_sys.sv)](pic_regmap_v2.md) — `pic_regmap_v2`
- [System Timer Port Map (lx_sys.sv)](timer_regmap.md) — `timer_regmap`

## memmap

- [Alex I/O port map (draft)](alex_io.md) — `alex_io`
- [Logical Slots](io_slots.md) — `io_slots`
- [Logical Slots (16-bit Z80 address space)](mmu_slots.md) — `mmu_slots`

## timing

- [I2C: START, address byte write, ACK, STOP](i2c_byte_write.md) — `i2c_byte_write`
- [Slot power-up sequence](slot_power_seq.md) — `slot_power_seq`
- [SPI mode 0: one byte exchange (per slot)](spi_mode0.md) — `spi_mode0`
- [SPI packet made of two jobs (CS_N stays low between them)](spi_packet.md) — `spi_packet`
- [Audio TDM: start of a frame (16 slots x 32 bits)](tdm_frame.md) — `tdm_frame`

## fsm

- [Slot power-up sequence](slot_power.md) — `slot_power`
- [SPI job controller](spi_job.md) — `spi_job`

## pins

- [Alex slot connector (PCIe x1, 36 contacts; key between positions 11 and 12)](alex_connector.md) — `alex_connector`

## const

- [Alex parameters](alex_params.md) — `alex_params`
- [Connector contact budget](pin_groups.md) — `pin_groups`

## connector

- [PCIe x1 — Connector's edge](alex_pcie_edge.md) — `alex_pcie_edge`

