# Memory

The processor has three memory levels: ROM (program memory), cache (4 channels), and external SDRAM via Wishbone.

## Memory Map

The 24-bit address space is `{PAGE[7:0], WORD[14:0], 1'b0}` — 256 pages of 128 KB each. ROM is a separate BRAM (`microcode_rom`), not part of the Wishbone address space.

{{auto:memory_map}}

## ROM

ROM stores the program. Synchronous, 1-cycle latency. The output register latches the instruction on `ack` — this is the instruction register (IR).

## Cache

The cache is 4-channel, one per pixel engine channel. It stores TAG (15 bits), DATA (16 bits), PAGE (8 bits). States and transitions are described in the GPU cache section.

## Wishbone

The cache is a Wishbone master. It drives `wb_cyc`, `wb_stb`, `wb_we`, `wb_adr`, `wb_dat_o` and waits for `wb_ack`. Dirty writeback is `C_WB_REQ`, read is `C_FILL_REQ`.