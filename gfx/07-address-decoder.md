# 07 — Address Decoder and Bus Routing

## Decoder contract

The address decoder is a pure combinational block. It receives the system byte address and produces:

* `wb_tag[2:0]` — which physical space the cycle belongs to.
* `cs_native[7:0]` — 4 KB block selects within native space.
* `cs_system[7:0]`, `cs_legacy[7:0]` — 32-byte device slots within two of the native blocks.

### Region summary

| Region | Address | Tag | Notes |
|--------|---------|-----|-------|
| Memory | everything below `0xFF0000` and `0xFF4000–0xFFFFFF` not otherwise claimed | `001` | SDRAM |
| Native IO | `0xFF0000–0xFF3FFF` | `010` | 8 × 4 KB sub-blocks |
| Legacy IO | `0xFF4000–0xFFFFFF` | `100` | CPC `BCxx`, gate array, etc. |

> Note: `mmio_space` requires `wb_adr[23:16] == 0xFF`; `mmio_4000_FFFF` further requires `wb_adr[15] || wb_adr[14]`. The split of `cs_legacy` at `cs_native_o[1]` (block 0xFF0280) in the current file shadows some `cs_system` decodes — treat the two `cs_legacy[4..7]` lines as reserved for now, and place new native peripherals in `cs_native[3..7]` (`0xFF0180–0xFF03FF`).

## Device placement in this build

* `color_palette` — `cs_legacy[0]` (native address `0xFF0100–0xFF011F`)
* `mc6845mod` — `cs_legacy[1]` (native address `0xFF0120–0xFF013F`)
* Video mode controller — `0x0140` on TAG = Native (per `04-pixel-pipeline.md`)
* SDRAM — tag `001`, full 32 MB window

The `cfg_legacy_i` input of the palette and CRTC is currently driven from `aleste_video.sv`. When `cfg_legacy = 0`, those modules respond on their native windows; when `cfg_legacy = 1`, they additionally accept CPC legacy transactions at `0xBC00`.

## Acknowledgement and errors

* A cycle whose address matches no device never asserts ACK.
* `aleste_video.sv` has a watchdog (`wb_wdt_simple`, timeout 32 bus cycles) that asserts `wb_err` on timeout — software should treat this as a bus error.
* There is no per-device error signal exposed to software.

---
