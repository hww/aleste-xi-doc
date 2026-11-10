
# 08 — Memory Arbiter and Video DMA

## Arbiters

There are two arbiter levels:

1. **`wb_arbiter.sv`** — top-level fan-out of CPU-side Wishbone to palette / CRTC / memory. Combinational; every device sees the cycle, first `grant_i` wins.
2. **`memory_arbiter.sv`** — shares the physical SDRAM between:
   * the video fetch engine (`video_req_i`, 16-bit reads at line-request boundaries),
   * CPU Wishbone to memory (`wb_*`, tag `001`),
   * a future GPU interface (`gpu_*`, tied off in this build).

## Priority

In the current RTL the state machine checks video request **first**, then CPU, then GPU. Video requests are "sticky": once a video burst is issued it completes two 16-bit words before any CPU request is considered. On a busy scanline the CPU can therefore see SDRAM latency, but not starvation — the video request is finite (2 words).

Software-visible effects:

* CPU memory reads and writes are wait-stated against video fetch. There is no separate "video is now consuming" flag; the effect shows up as variable latency.
* The internal WB→SDRAM latency (ACK seen by the CPU) is dominated by the arbiter + SDRAM controller. A CPU transaction that arrives just after a video burst starts will wait roughly one burst worth of SDRAM cycles (tens of nanoseconds).

## Memory layout as seen by software

For the video engine to fetch the right bytes:

* In **linear mode**, the framebuffer is a flat byte array starting at `{R19, R12, R13}`. Each row consumes `R1 × (16×bpp)/8` bytes, and the linear counter increments per character-boundary crossing. Effectively each visible row is a contiguous span of `R1 × bytesPerCharacter` bytes.
* In **legacy mode**, the byte address is computed from MA/RA using the CPC interleave — code that wants a linear image must pre-scramble data into the CPC layout, or switch to linear mode.

## Concurrency hazards

* **Reading SDRAM while it is being fetched by the video engine** is safe — arbitration serialises access.
* **Writing SDRAM from CPU while the same bytes are being fetched** is not synchronised with display. The write will take effect on the next video fetch; the CPU may see one or more frames of the old value before the change becomes visible.
* There is no VSYNC-gated write protection. Double-buffering must be implemented in software by swapping `R12/R13/R19` at VSYNC.

## Video request rate

`video_req` toggles at `stb_sync1` / `stb_sync2` boundaries and is qualified by the DE state (see the video buffer doc). At 27 MHz pixel clock and 16 pixels per character, the request rate is:

| `cfg_rate` | Requests per character | Approx. peak bandwidth |
|------------|------------------------|------------------------|
| 00 | 1 (at sync1) | ~6.75 MB/s |
| 01 | 2 (sync1 + sync2) | ~13.5 MB/s |
| 10 | continuous during DE | ~54 MB/s |
| 11 | continuous during DE | ~108 MB/s |
