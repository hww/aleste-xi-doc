# 02 — Memory Map and Bus Model

## Wishbone access model

All access is byte-wide. The bus carries:

| Field | Meaning |
|-------|---------|
| `wb_cyc`, `wb_stb` | Transaction select |
| `wb_we` | Write enable |
| `wb_adr[23:0]` | Address |
| `wb_dat_i/o[7:0]` | Byte data |
| `wb_tag[2:0]` | Space tag (see below) |
| `wb_ack` | Device accepted the cycle |
| `wb_grant` | Some device responded this cycle |

`wb_tag` is produced by `address_decoder.sv` from the address bits:

| Tag | Value | Address range | Space |
|-----|-------|---------------|-------|
| Memory | `3'b001` | `0x000000–0xFF3FFF` (everything that is not native IO) | SDRAM |
| Native IO | `3'b010` | `0xFF0000–0xFF3FFF` | Native MMIO |
| Legacy IO | `3'b100` | `0xFF4000–0xFFFFFF` | Legacy MMIO |

Within **Native IO** (`0xFF0000–0xFF3FFF`):

* The top-level Native block is 4 KB, further decoded into 8 sub-blocks of 512 bytes (see `cs_native_o[7:0]`).
* `cs_system` and `cs_legacy` split the first two sub-blocks into 32-byte device slots.
* Current device placement:
  * `cs_legacy[0]` → `color_palette` (base `0xFF0100` in this build)
  * `cs_legacy[1]` → `mc6845mod` (base `0xFF0120`)
  * `cs_native[0..7]` → various system blocks
* Video mode controller (from `04-pixel-pipeline.md`) sits at native base `0x0140` on TAG=01 in the reference system — i.e. `0xFF0140` in this address map.

Within **Legacy IO** (`0xFF4000–0xFFFFFF`):

* The CPC gate array and CRTC legacy addresses live here:
  * `0xBC00` → palette / Gate Array (when D7=0)
  * `0xBC01` → CRTC address register (with `wb_tag_i[2] = 1`)
  * `0xBC00` also reaches CRTC when write has `wb_tag_i[2] = 1` and `wb_adr[8] = 0` — see CRTC legacy decode in §03 §2.
* Because `mc6845mod` and `color_palette` are physically reachable via native `cs_legacy`, you can *also* access them via `0xFF0100/0xFF0120` using native two-register addressing.

## SDRAM / framebuffer

The SDRAM controller is 16-bit wide, byte-addressed Wishbone from a 24-bit address bus on the system side (see `memory_arbiter.sv`). Two 8-bit bytes per 16-bit word; `wb_sel` selects the half on writes.

Software sees SDRAM as a flat 32 MB space accessed through `wb_tag=001`. The video DMA reads through the same physical port with its own dedicated arbitration, so an ordinary CPU read at the same address competes with video fetch (arbiter priorities: video > WB > GPU in the current RTL — video is serviced first when both are pending).

## Address composition for video DMA

The 24-bit address presented to SDRAM by the video engine is produced by the CRTC:

* **Legacy address mode** (`R20[0] = 0`):
  ```
  crtc_ext_addr_o = {R19[7:0], MA[13:12], RA[3:0], MA[9:0], 1'b0}
  ```
  This is the CPC-style bit layout: MA and RA are interleaved to form the byte address, and R19 supplies A23:A16. A0 is always zero (16-bit aligned) — the video engine fetches a 16-bit word.
* **Linear mode** (`R20[0] = 1`):
  ```
  crtc_ext_addr_o = {R19[7:0], linear_counter[15:0]}
  ```
  `linear_counter` is initialised from `{R12, R13}` at each VSYNC and then advances on `stb_sync1_o` (and optionally `stb_sync2_o`), by `R20[1] ? 4 : 2` bytes.

The exact frame layout (how many bytes correspond to one character row) depends on `R0`, `R1`, `R9`, and `R20[1:0]`. See §03 §8 for the counter logic.

## Write/read isolation

The Wishbone arbiter (`wb_arbiter.sv`) is purely combinational: every device sees every cycle, and whichever device asserts `grant_i` wins. Palette wins over CRTC, CRTC wins over memory. This means:

* Reading from a palette address *never* triggers a CRTC read, even if the address also matches a CRTC decode window.
* Memory reads (tag=001) never reach palette/CRTC — they are routed only through `memory_arbiter`.
* Access that matches none of palette/CRTC/memory simply never asserts ACK; a watchdog in `aleste_video.sv` generates a bus error after a bounded number of cycles. Software should treat this as a bus fault.

---
