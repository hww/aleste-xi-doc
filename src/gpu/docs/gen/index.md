# Specification index

## bitfield

- [BUSY Register](busy_bitfield.md) — `busy_bitfield`
- [CHANNEL MODE_PAGE (11 bits, логическая склейка MODE[2:0] + PAGE[7:0])](channel_mode_page.md) — `channel_mode_page`
- [CTRL · 32 BIT](ctrl_reg.md) — `ctrl_reg`
- [FLAGS Register](flags_bitfield.md) — `flags_bitfield`
- [INSTRUCTION · 32 BIT · J=1 I=0 CONTROL](insn_ctrl.md) — `insn_ctrl`
- [INSTRUCTION · 32 BIT · J=1 I=1 REG-IMM12 (d = d op imm)](insn_imm12.md) — `insn_imm12`
- [INSTRUCTION · 32 BIT · J=0 I=1 LDI24 (R[DST] = imm24)](insn_ldi24.md) — `insn_ldi24`
- [INSTRUCTION · 32 BIT · J=0 I=0 REG-REG (d = d op s)](insn_reg.md) — `insn_reg`
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

## encoding

- [INSTRUCTION · 32 BIT](insn.md) — `insn`

## regmap

- [UART registers](uart.md) — `uart`

## memmap

- [Memory map](map.md) — `map`
- [Memory Map (24-bit physical address = {PAGE[7:0], WORD[14:0], 1'b0})](memory_map.md) — `memory_map`

## timing

- [Pixel Read Timing](pixel_read_timing.md) — `pixel_read_timing`
- [alu: combinational compute (0 cyc), MHI registered on MUL (1 cyc)](timing_alu.md) — `timing_alu`
- [ALU instruction: read (t1), compute (comb, 0 cyc), write (t2), result holds (t3)](timing_alu_pipeline.md) — `timing_alu_pipeline`
- [gpu_cache: hit (1 cyc), miss/fill (3+ cyc)](timing_gpu_cache.md) — `timing_gpu_cache`
- [microcode_rom: synchronous read latched on ack; data holds during stall](timing_microcode_rom.md) — `timing_microcode_rom`
- [pixel_blender: IDLE -> CAPTURE -> FREE -> IDLE (3 cyc)](timing_pixel_blender.md) — `timing_pixel_blender`
- [regfile: write mem_R5 (t2), read q_a (t2), bypass (t1, same-cycle)](timing_regfile.md) — `timing_regfile`
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

