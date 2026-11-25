# Pixel Engine

The pixel engine (`ch_addr_gen`, instance `u_pe`) holds a pixel index (20 bits: 15 integer, 4 fractional, 1 page-overflow) and a step (20 bits). The index defines the word (integer part) and position (fractional part); bit 19 is the page-overflow flag. The format (`MODE`) defines how many pixels per word.

## Formats

Five packed formats are supported: 1, 2, 4, 8, and 16 bpp. Codes 5..7 are reserved (read like 16 bpp, writes ignored). The format defines `k` (shift) and `mask` (position mask). Each format has its own pixels-per-word count. 1 bpp and 2 bpp are read-only in the RTL (`wr_en=0` in `get_fmt_info`).

{{auto:channel_mode}}

*Fig. 13. Pixel format modes.*

## Index and Step

The index (`reg_idx`) is 20 bits. Bits `[18:4]` are the word, bits `[3:0]` are the position, bit `[19]` is the page-overflow flag. The step (`reg_step`) is 20 bits, added to the index after each completed access. The index is loaded through a shared 23-bit signed shifter that applies `>>> k` before storing; this is why `IDX`/`IDXH`/`STEP` are written as full pixel counts. Increment occurs on `access_done_i` (which is `blend_ack` from the blender), not on any separate cache-done signal.

## Pixel Path

The pixel path goes through several stages, from index to destination register.

{{table:pixel_path_stages}}

## Timing

The timing diagram below shows a single pixel read operation.

{{auto:pixel_read_timing}}

The blender (`ch_blender`) converts between the pixel and the 16-bit word. It has no state machine and does no read-modify-write:

- **Read:** the cache word is unpacked combinationally, `pixel = (word >> shift) & pix_mask`, and `ack_o` is the cache's ack.
- **Write:** a pixel write is a single cache access. The blender shifts the pixel into place (`rmw_dat_o = (pixel << shift) & mask`) and sends the mask of the bits it replaces (`rmw_msk_o = pix_mask << shift`). The cache merges the pixel into its word (see the GPU cache section); a write never reads memory first.
- **Write-protected formats** (1 bpp, 2 bpp and the reserved codes) are acknowledged after one cycle without touching the cache.
- `dat_o` carries read data only. It must not depend on the pixel being written, otherwise ALU → blender → operand mux would form a combinational loop.

{{auto:timing_pixel_blender}}

*Fig. 14. Pixel blender timing.*