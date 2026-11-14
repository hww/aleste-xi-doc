# Memory

The processor has three memory levels: ROM (program memory), cache (4 channels), and external SDRAM via Wishbone.

## Memory Map

The 24-bit address space is `{PAGE[7:0], WORD[14:0], 1'b0}` — 256 pages of 128 KB each. ROM is a separate BRAM (`microcode_rom`), not part of the Wishbone address space.

![Memory Map (24-bit physical address = {PAGE[7:0], WORD[14:0], 1'b0})](gen/memory_map.svg)

*Figure 2 — Memory Map (24-bit physical address = {PAGE[7:0], WORD[14:0], 1'b0})*

**Table 2 — Memory Map (24-bit physical address = {PAGE[7:0], WORD[14:0], 1'b0})**

| Range | Name | Size | Access | Purpose |
| --- | --- | --- | --- | --- |
| `0x000000`–`0x01FFFF` | <a id="PAGE_0x00"></a>**PAGE 0x00** | 128 KiB | rw | Page 0 (128 KB, 2 bytes per word × 65536 words) |
| `0x020000`–`0xFDFFFF` | <a id="..."></a>**...** | 16128 KiB | rw | Pages 1..254 (each 128 KB) |
| `0xFE0000`–`0xFFFFFF` | <a id="PAGE_0xFF"></a>**PAGE 0xFF** | 128 KiB | rw | Page 255 (last 128 KB) |

**Notes:**

- В RTL addr24 = {page[7:0], word[14:0], 1'b0}. Адресное пространство — 16 МБ, разбито на 256 страниц по 128 КБ. Отдельных ROM/DATA/SDRAM регионов в wb_adr нет — ROM это microcode_rom (отдельная BRAM, не в wb-пространстве).


## ROM

ROM stores the program. Synchronous, 1-cycle latency. The output register latches the instruction on `ack` — this is the instruction register (IR).

## Cache

The cache is 4-channel, one per pixel engine channel. It stores TAG (15 bits), DATA (16 bits), PAGE (8 bits). States and transitions are described in the GPU cache section.

## Wishbone

The cache is a Wishbone master. It drives `wb_cyc`, `wb_stb`, `wb_we`, `wb_adr`, `wb_dat_o` and waits for `wb_ack`. Dirty writeback is `C_WB_REQ`, read is `C_FILL_REQ`.