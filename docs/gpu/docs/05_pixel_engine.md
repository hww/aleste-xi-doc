# Pixel Engine

The pixel engine (`pixel_engine`) holds a pixel index (19 bits: 15 integer, 4 fractional) and a step (19 bits). The index defines the word (integer part) and position (fractional part). The format (`MODE`) defines how many pixels per word.

## Formats

Five formats are supported: 1, 2, 4, 8, and 16 bpp, plus three pass-through modes (LO8/HI8/16). The format defines `k` (shift) and `mask` (position mask). Each format has its own pixels-per-word count.

**Table 3 — CHANNEL FORMAT (fmt, 3 bits)**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="1_bpp"></a>**1 bpp** | 16 pixels per word (k=4); SOURCE ONLY, writes forbidden |
| 1 | <a id="2_bpp"></a>**2 bpp** | 8 pixels per word (k=3) |
| 2 | <a id="4_bpp"></a>**4 bpp** | 4 pixels per word (k=2); pos 0 = high nibble |
| 3 | <a id="8_bpp"></a>**8 bpp** | 2 pixels per word (k=1); pos 0 = high byte |
| 4 | <a id="16_bpp"></a>**16 bpp** | 1 pixel per word (k=0) |
| 5 | <a id="PASS_LO8"></a>**PASS_LO8** | Low byte pass-through |
| 6 | <a id="PASS_HI8"></a>**PASS_HI8** | High byte pass-through |
| 7 | <a id="PASS16"></a>**PASS16** | Whole word pass-through |


*Fig. 13. Pixel format modes.*

## Index and Step

The index (`idx_stored`) is 19 bits. The upper 15 bits are the word, the lower 4 bits are the position. The step (`step_stored`) is 19 bits, added to the index after each read. Increment occurs on `pb_ack` (from the blender), not on `gc_access_done`.

## Pixel Path

The pixel path goes through several stages, from index to destination register.

**Table 4 — Pixel Path Stages**

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

*Figure 3 — Pixel Read Timing*


The blender is a 3-state FSM: `B_IDLE → B_CAPTURE → B_FREE → B_IDLE`. `start` captures the inputs, `B_CAPTURE` computes `pixel_out` / `word_out`, and `B_FREE` asserts `ack` for one cycle. Total latency from `start` to `ack` is 3 cycles.

![pixel_blender: IDLE -> CAPTURE -> FREE -> IDLE (3 cyc)](gen/timing_pixel_blender.svg)

*Figure 4 — pixel_blender: IDLE -> CAPTURE -> FREE -> IDLE (3 cyc)*


*Fig. 14. Pixel read timing.*