# Pixel Engine

The pixel engine (`ch_addr_gen`, instance `u_pe`) holds a pixel index (20 bits: 15 integer, 4 fractional, 1 page-overflow) and a step (20 bits). The index defines the word (integer part) and position (fractional part); bit 19 is the page-overflow flag. The format (`MODE`) defines how many pixels per word.

## Formats

Five packed formats are supported: 1, 2, 4, 8, and 16 bpp, plus two pass-through modes (LO8/HI8). Slot 7 is reserved. The format defines `k` (shift) and `mask` (position mask). Each format has its own pixels-per-word count. 1 bpp and 2 bpp are read-only in the RTL (`wr_en=0` in `get_fmt_info`).

**Table 1 — CHANNEL FORMAT (fmt, 3 bits)**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="16_bpp"></a>**16 bpp** | 1 pixel per word (k=0) |
| 1 | <a id="8_bpp"></a>**8 bpp** | 2 pixels per word (k=1); pos 0 = low byte (even address) |
| 2 | <a id="4_bpp"></a>**4 bpp** | 4 pixels per word (k=2); pos 0 = low nibble |
| 3 | <a id="2_bpp"></a>**2 bpp** | 8 pixels per word (k=3); SOURCE ONLY, writes forbidden |
| 4 | <a id="1_bpp"></a>**1 bpp** | 16 pixels per word (k=4); SOURCE ONLY, writes forbidden |
| 5 | <a id="RESERVED"></a>**RESERVED** | Reserved, writes forbidden |
| 6 | <a id="RESERVED"></a>**RESERVED** | Reserved, writes forbidden |
| 7 | <a id="RESERVED"></a>**RESERVED** | Reserved, writes forbidden |


*Fig. 13. Pixel format modes.*

## Index and Step

The index (`reg_idx`) is 20 bits. Bits `[18:4]` are the word, bits `[3:0]` are the position, bit `[19]` is the page-overflow flag. The step (`reg_step`) is 20 bits, added to the index after each completed access. The index is loaded through a shared 23-bit signed shifter that applies `>>> k` before storing; this is why `IDX`/`IDXH`/`STEP` are written as full pixel counts. Increment occurs on `access_done_i` (which is `blend_ack` from the blender), not on any separate cache-done signal.

## Pixel Path

The pixel path goes through several stages, from index to destination register.

**Table 2 — Pixel Path Stages**

| Stage | Signal | Description |
| --- | --- | --- |
| 1 | <a id="idx_stored"></a>**idx_stored** | 19-bit index (15 integer, 4 fractional) |
| 2 | <a id="word_out"></a>**word_out** | 15-bit word (integer part) |
| 3 | <a id="gc_rdata"></a>**gc_rdata** | 16-bit data from cache |
| 4 | <a id="pb_pixel_out"></a>**pb_pixel_out** | 16-bit pixel from blender |
| 5 | <a id="wdata"></a>**wdata** | Written to destination register |


## Timing

The timing diagram below shows a single pixel read operation.

![Pixel Read Timing](gen/pixel_read_timing.svg)

The blender (`ch_blender`) is a 3-state FSM used for writes: `IDLE → RMW_READ → RMW_WRITE → IDLE`. In `IDLE` a write request (`cyc_i && stb_i && we_i`) captures `mode`, `frac` and the source pixel; `RMW_READ` reads the target word from the cache; `RMW_WRITE` blends the pixel into the word and writes it back. Reads bypass the FSM: `dat_o` is the combinatorially unpacked pixel and `ack_o = ack_i` from the cache.

![pixel_blender: combinational read; RMW write FSM (IDLE -> RMW_READ -> RMW_WRITE)](gen/timing_pixel_blender.svg)

*Fig. 14. Pixel read timing.*