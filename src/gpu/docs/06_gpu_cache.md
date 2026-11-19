# GPU Cache

The cache (`ch_cache`, instance `u_cache`) is 4-channel, one per pixel engine channel. Each channel stores TAG (15 bits), DATA (16 bits), PAGE (8 bits), VALID, DIRTY, plus a pending page-change flag and its target page.

## Structure

Each channel consists of per-channel arrays (TAG, DATA, PAGE) and the bits VALID, DIRTY, PEND, plus `pend_page` (the page value waiting to be applied). The address is 24-bit: `{PAGE[7:0], WORD[14:0], 1'b0}`. A page write is deferred: if the new page differs from the current one, `PEND` is set and the change is applied only when the entry is clean or invalid.

## FSM

The cache has three states: `ST_IDLE`, `ST_FILL`, `ST_WRITEBACK`. A combinational `flush_noop_c` handles the case when the requested channel is not dirty or not valid (no writeback needed): it invalidates the channel and drives `flush_done_c` without a Wishbone cycle.

{{auto:cache_fsm}}

## `ack`

`ack_o` is a one-cycle strobe. It is asserted **only on a hit** (`ack_r <= ch_stb_i && hit && !ack_r`). It does not stick: it clears on the next cycle regardless of `ch_stb_i`.

A cache hit produces `ack_o` one cycle after `ch_stb_i`. A cache miss does **not** assert `ack_o`: the FSM goes `ST_IDLE → ST_FILL → ST_IDLE`, performs the Wishbone read, and becomes valid; the requester must hold/re-issue `ch_stb_i` to get the hit ack. The consumer-side `access_done` in `ch_top` is `blend_ack` from the blender, not this `ack_o`. A flush of a clean or invalid channel (`flush_noop_c`) completes in one cycle without a Wishbone cycle.

{{auto:timing_gpu_cache}}