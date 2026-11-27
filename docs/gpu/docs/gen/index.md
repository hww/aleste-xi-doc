# Specification index

## bitfield

- [BUSY Register (34)](busy_bitfield.md) — `busy_bitfield`
- [CHANNEL MODE_PAGE (11 bits: MODE[2:0] + PAGE[7:0])](channel_mode_page.md) — `channel_mode_page`
- [FLAGS Register](flags_bitfield.md) — `flags_bitfield`
- [J=1 I=0 CONTROL (R=0: JMP/CALL/RET/HALT/IRQ/FLUSH)](insn_ctrl_jmp.md) — `insn_ctrl_jmp`
- [J=1 I=0 CONTROL RJUMP (R=1: JMPR)](insn_ctrl_jmpr.md) — `insn_ctrl_jmpr`
- [J=1 I=1 REG-IMM11](insn_imm11.md) — `insn_imm11`
- [J=0 I=1 LDI16](insn_ldi16.md) — `insn_ldi16`
- [J=0 I=0 REG-REG](insn_reg.md) — `insn_reg`
- [SHADOW Register Format](shadow_bitfield.md) — `shadow_bitfield`
- [ALU_CTL (16 bits, PEN bank group 2)](v2_alu_ctl_bitfield.md) — `v2_alu_ctl_bitfield`
- [Channel MODE (per channel; word written via SURF.MODE_PAGE)](v2_mode_bitfield.md) — `v2_mode_bitfield`

## enum

- [ALU OP (5 bits, class = op[4:3], fn = op[2:1], flag = op[0])](alu_ops.md) — `alu_ops`
- [CHANNEL FORMAT (fmt, 3 bits)](channel_mode.md) — `channel_mode`
- [Pixel Engine Channels (48..63)](channels.md) — `channels`
- [COND (4 bits, ARM-style)](conditions.md) — `conditions`
- [CTRL OP (J=1, I=0)](ctrl_ops.md) — `ctrl_ops`
- [DATA[0..3] (44..47)](data_regs.md) — `data_regs`
- [GPU Commands](gpu_interface_commands.md) — `gpu_interface_commands`
- [Loader packet headers](gpu_interface_package.md) — `gpu_interface_package`
- [Operand map (6 bits, 0..63)](operand_map.md) — `operand_map`
- [Pixel Path Stages](pixel_path_stages.md) — `pixel_path_stages`
- [Register file · R0–R31 (16 bit)](registers.md) — `registers`
- [System Registers (32..42, 43 reserved)](sysregs.md) — `sysregs`
- [CHANNEL FORMAT (fmt, 3 bits); W = operand width of the pixel ALU](v2_channel_format.md) — `v2_channel_format`
- [Bank 0 POS - position (per scanline). 16.16 two's complement integer / unsigned fraction](v2_operand_map_bank_0_pos.md) — `v2_operand_map_bank_0_pos`
- [Bank 1 STEP - added to position after every DATA access (per primitive)](v2_operand_map_bank_1_step.md) — `v2_operand_map_bank_1_step`
- [Bank 2 CLIP - inclusive signed clip rectangle on integer position (per window)](v2_operand_map_bank_2_clip.md) — `v2_operand_map_bank_2_clip`
- [Bank 3 PEN - pen & ALU (per primitive)](v2_operand_map_bank_3_pen.md) — `v2_operand_map_bank_3_pen`
- [Bank 4 SURF - surface (per surface)](v2_operand_map_bank_4_surf.md) — `v2_operand_map_bank_4_surf`
- [Operand map (6 bits, 0..63)](v2_operand_map_top.md) — `v2_operand_map_top`
- [Pixel ALU OP (4 bits), W-bit unsigned](v2_pixel_alu_ops.md) — `v2_pixel_alu_ops`

## encoding

- [INSTRUCTION · 32 BIT](insn.md) — `insn`

## regmap

- [GPU Interface](gpu_interface.md) — `gpu_interface`

## memmap

- [Memory Map (24-bit physical address = {PAGE[7:0], WORD[14:0], 1'b0})](memory_map.md) — `memory_map`
- [Memory Map (24-bit physical address = {PAGE[7:0], WORD[14:0], 1'b0}); 64 KB per page](v2_memory_map.md) — `v2_memory_map`

## timing

- [Pixel Read Timing](pixel_read_timing.md) — `pixel_read_timing`
- [alu: combinational compute (0 cyc), MHI registered on MUL (1 cyc)](timing_alu.md) — `timing_alu`
- [ALU instruction in F -> D -> X pipeline (D reads regfile, X computes & writes back)](timing_alu_pipeline.md) — `timing_alu_pipeline`
- [FLUSH: blocking X-stage until ST_WRITEBACK completes and flush_ack_o strobes](timing_flush.md) — `timing_flush`
- [gpu_cache: read hit (1 cyc ack), read miss (ST_IDLE -> ST_FILL -> ST_IDLE)](timing_gpu_cache.md) — `timing_gpu_cache`
- [gpu_cache: write miss on a dirty entry (post + allocate in one cycle), then a write hit](timing_gpu_cache_write.md) — `timing_gpu_cache_write`
- [microcode_rom: synchronous read on fetch_en_i (1 cyc latency, held on stall)](timing_microcode_rom.md) — `timing_microcode_rom`
- [pixel_blender: combinational read; a write is one masked cache access](timing_pixel_blender.md) — `timing_pixel_blender`
- [regfile: write mem[wa] on posedge; synchronous read on rd_en_i with write-through bypass](timing_regfile.md) — `timing_regfile`
- [fetch_unit: 3-stage pipeline F -> D -> X (1 cyc/insn, 1 bubble on D-branch/L-loop)](timing_sequencer.md) — `timing_sequencer`
- [top: DATA write (cache hit: one masked access -> ack)](timing_top_data.md) — `timing_top_data`

## fsm

- [Cache FSM](cache_fsm.md) — `cache_fsm`

## const

- [GPU Error](gpu_interface_result.md) — `gpu_interface_result`
- [Limits](limits.md) — `limits`

