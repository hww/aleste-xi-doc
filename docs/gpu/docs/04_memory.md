# Memory

The processor has three memory levels: ROM (program memory), cache (4 channels), and external memory via Wishbone.

## Memory Map

The 24-bit address space is `{PAGE[7:0], WORD[14:0], 1'b0}` — 256 pages of 64 KB each. ROM is a separate BRAM (`core_rom`), not part of the Wishbone address space.

![Memory Map (24-bit physical address = {PAGE[7:0], WORD[14:0], 1'b0})](gen/memory_map.svg)

**Table 1 — Memory Map (24-bit physical address = {PAGE[7:0], WORD[14:0], 1'b0})**

| Range | Name | Size | Access | Purpose |
| --- | --- | --- | --- | --- |
| `0x000000`–`0x00FFFF` | <a id="PAGE_0x00"></a>**PAGE 0x00** | 64 KiB | rw | Page 0 (64 KB) |
| `0x010000`–`0xFEFFFF` | <a id="..."></a>**...** | 16256 KiB | rw | Pages 1..254 (each 64 KB) |
| `0xFF0000`–`0xFFFFFF` | <a id="PAGE_0xFF"></a>**PAGE 0xFF** | 64 KiB | rw | Page 255 (last 64 KB) |

**Notes:**

- In RTL addr24 = {page[7:0], word[14:0], 1'b0}. Address space is 16 MB, divided into 256 pages of 64 KB each.


## ROM

ROM stores the program. Synchronous, 1-cycle latency: the fetch output register latches `mem[fetch_addr]` on the next `posedge` while `fetch_en` is high — this is the instruction register (IR). The access port (`acc_we`/`acc_re`) shares the same BRAM: a read latches into `acc_rdata` on the next clock (valid one cycle later), a write stores on the next clock; `acc_we` has priority over `acc_re`.

## Cache

The cache is 4-channel, one word per pixel engine channel, plus a one-word posted write buffer shared by the channels. Each entry stores TAG (15 bits), DATA (16 bits), PAGE (8 bits), VALID, FULL, a 4-bit dirty mask per nibble, and the pending page change. Writes never read memory first. See the GPU cache section.

## Wishbone

The cache is a Wishbone master. It drives `wb_cyc`, `wb_stb`, `wb_we`, `wb_adr`, `wb_dat_o`, `wb_sel` (byte enables of a write) and waits for `wb_ack`. The state machine is `ST_IDLE / ST_FILL / ST_WRITEBACK`: a read miss performs `ST_FILL`, a `FLUSH` of a dirty channel performs `ST_WRITEBACK`, and any other dirty eviction goes to the write buffer, which drains on its own.

## On the Aleste LX (MiSTer)

On the Aleste LX the GPU shares the SDRAM with the CPU and video through `memory_arbiter` and `sdram_wishbone`.

- **SDRAM controller** (`OPEN_PAGE=1`):
  - one open row per bank, with no auto-precharge;
  - a request to the open row of its bank goes straight to READ/WRITE; another row costs PRECHARGE + ACTIVE;
  - writes are acknowledged 2 cycles after their command, and `wb_sel` drives DQM;
  - refresh runs in idle gaps: up to 7 refreshes can be pending, and one is forced with 4 pending, so it never delays a video read past its deadline.
- **Address map** (`memory_arbiter`):
  - bank = the two low bits of the 64 KB page (`addr[17:16]`);
  - row = `{addr[23:18], addr[15:10]}`;
  - column = `addr[9:1]`.

  Consecutive words share a 1 KB row, and consecutive pages fall in different banks: C4 → bank 0, C5 → 1, C6 → 2, C7 → 3.
- **Rule for software:** keep textures, tiles and fonts out of the banks of the framebuffers being drawn (`page & 3`). Otherwise every read of a graphic closes the row of the screen being written. Moving GPUDEMO's graphics from pages 21h–26h to 27h/28h made the tile scene 10% faster and the parallax scene 6% faster.
