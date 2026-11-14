# Pixel Engine

The pixel engine (`pixel_engine`) holds a pixel index (19 bits: 15 integer, 4 fractional) and a step (19 bits). The index defines the word (integer part) and position (fractional part). The format (`MODE`) defines how many pixels per word.

## Formats

Five formats are supported: 1, 2, 4, 8, and 16 bpp, plus three pass-through modes (LO8/HI8/16). The format defines `k` (shift) and `mask` (position mask). Each format has its own pixels-per-word count.

{{auto:channel_mode}}

*Fig. 13. Pixel format modes.*

## Index and Step

The index (`idx_stored`) is 19 bits. The upper 15 bits are the word, the lower 4 bits are the position. The step (`step_stored`) is 19 bits, added to the index after each read. Increment occurs on `pb_ack` (from the blender), not on `gc_access_done`.

## Pixel Path

The pixel path goes through several stages, from index to destination register.

{{table:pixel_path_stages}}

## Timing

The timing diagram below shows a single pixel read operation.

{{auto:pixel_read_timing}}

The blender is a 3-state FSM: `B_IDLE → B_CAPTURE → B_FREE → B_IDLE`. `start` captures the inputs, `B_CAPTURE` computes `pixel_out` / `word_out`, and `B_FREE` asserts `ack` for one cycle. Total latency from `start` to `ack` is 3 cycles.

{{auto:timing_pixel_blender}}

*Fig. 14. Pixel read timing.*