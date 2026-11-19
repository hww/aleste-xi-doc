# Memory

The processor has three memory levels: ROM (program memory), cache (4 channels), and external memory via Wishbone.

## Memory Map

The 24-bit address space is `{PAGE[7:0], WORD[14:0], 1'b0}` — 256 pages of 128 KB each. ROM is a separate BRAM (`core_rom`), not part of the Wishbone address space.

{{auto:memory_map}}

## ROM

ROM stores the program. Synchronous, 1-cycle latency: the fetch output register latches `mem[fetch_addr]` on the next `posedge` while `fetch_en` is high — this is the instruction register (IR). The access port (`acc_we`/`acc_re`) shares the same BRAM: a read latches into `acc_rdata` on the next clock (valid one cycle later), a write stores on the next clock; `acc_we` has priority over `acc_re`.

## Cache

The cache is 4-channel, one entry per pixel engine channel. Each entry stores TAG (15 bits), DATA (16 bits), PAGE (8 bits), plus valid, dirty and pending-page-change flags. States and transitions are described in the GPU cache section.

## Wishbone

The cache is a Wishbone master. It drives `wb_cyc`, `wb_stb`, `wb_we`, `wb_adr`, `wb_dat_o` and waits for `wb_ack`. The master state machine is `ST_IDLE / ST_FILL / ST_WRITEBACK`; a dirty eviction or a `FLUSH` performs `ST_WRITEBACK`, a miss performs `ST_FILL`.