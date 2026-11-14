# Specification index

## bitfield

- [BUSY Register](busy_bitfield.md) — `busy_bitfield`
- [CHANNEL MODE_PAGE (11 bits: MODE[2:0] + PAGE[7:0])](channel_mode_page.md) — `channel_mode_page`
- [CTRL · 32 BIT](ctrl_reg.md) — `ctrl_reg`
- [FLAGS Register](flags_bitfield.md) — `flags_bitfield`
- [J=1 I=0 CTRL (JMP/CALL/RET/HALT/IRQ/FLUSH)](insn_ctrl_jmp.md) — `insn_ctrl_jmp`
- [J=1 I=0 CTRL (JMPR)](insn_ctrl_jmpr.md) — `insn_ctrl_jmpr`
- [J=1 I=1 REG-IMM11](insn_imm11.md) — `insn_imm11`
- [J=0 I=0 REG-REG](insn_reg.md) — `insn_reg`
- [SHADOW Register Format](shadow_bitfield.md) — `shadow_bitfield`
- [64-bit status, 2 lanes](wide.md) — `wide`

## enum

- [ALU OP (5 bits, class = op[4:3], fn = op[2:1], flag = op[0])](alu_ops.md) — `alu_ops`
- [CHANNEL FORMAT (fmt, 3 bits)](channel_mode.md) — `channel_mode`
- [Pixel Engine Channels (48..63)](channels.md) — `channels`
- [Loader packet headers](commands.md) — `commands`
- [COND (4 bits, ARM-style)](conditions.md) — `conditions`
- [CTRL OP (J=1, I=0)](ctrl_ops.md) — `ctrl_ops`
- [DATA[0..3] (40..43)](data_regs.md) — `data_regs`
- [Operand map (6 bits, 0..63)](operand_map.md) — `operand_map`
- [Pixel Path Stages](pixel_path_stages.md) — `pixel_path_stages`
- [Register file · R0–R31 (16 bit)](registers.md) — `registers`
- [System Registers (32..38, 39 reserved)](sysregs.md) — `sysregs`

## regmap

- [UART registers](uart.md) — `uart`

## memmap

- [Memory map](map.md) — `map`
- [Memory Map (24-bit physical address = {PAGE[7:0], WORD[14:0], 1'b0})](memory_map.md) — `memory_map`

## timing

- [Pixel Read Timing](pixel_read_timing.md) — `pixel_read_timing`
- [alu: combinational compute (0 cyc), MHI registered on MUL (1 cyc)](timing_alu.md) — `timing_alu`
- [ALU instruction: combinational read/compute/write within 1 cyc](timing_alu_pipeline.md) — `timing_alu_pipeline`
- [FLUSH: one-cycle en, then C_WB_REQ -> C_IDLE](timing_flush.md) — `timing_flush`
- [gpu_cache: hit (1 cyc), miss/fill (3+ cyc)](timing_gpu_cache.md) — `timing_gpu_cache`
- [microcode_rom: synchronous read, latched on ack](timing_microcode_rom.md) — `timing_microcode_rom`
- [pixel_blender: IDLE -> CAPTURE -> FREE -> IDLE (3 cyc)](timing_pixel_blender.md) — `timing_pixel_blender`
- [regfile: write mem[wa] on posedge; combinational read rdata = mem[ra]](timing_regfile.md) — `timing_regfile`
- [sequencer: PC fetch and next-PC (1 cyc per instruction)](timing_sequencer.md) — `timing_sequencer`
- [top: DATA read (3 cyc: cache + blender)](timing_top_data.md) — `timing_top_data`
- [Write cycle](wr_cycle.md) — `wr_cycle`

## fsm

- [Cache FSM](cache_fsm.md) — `cache_fsm`
- [Controller FSM](ctl.md) — `ctl`

## pins

- [Pinout](chip.md) — `chip`

## const

- [Limits](limits.md) — `limits`

