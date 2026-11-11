
# 09 — Programmer Cheat Sheet and Init Sequence

## Canonical native-mode init sequence (linear, 4 bpp, palette indexed)

```asm
; 1. Stop display during reconfiguration (optional but recommended).
;    Clear CRTC display enable by setting R1 = 0 or R6 = 0.
ld hl, crtc_addr
ld (hl), 1          ; R1 = Horizontal Displayed
ld hl, crtc_data
ld (hl), 0

; 2. Program video geometry (native CRTC).
;    R0  = 63  (64 chars per line)     R1 = 40 (40 visible)
;    R4  = 38  (39 rows)               R6 = 25
;    R9  = 7   (8 scan lines/char)
;   These are the reset defaults, so only write the ones you change.

; 3. Point at the framebuffer (linear mode).
ld hl, crtc_addr
ld (hl), 0x13       ; R19 = High Address
ld hl, crtc_data
ld (hl), 0x00       ; A23..A16 = 0

ld hl, crtc_addr
ld (hl), 0x0C       ; R12 = Start Address H
ld hl, crtc_data
ld (hl), 0x00

ld hl, crtc_addr
ld (hl), 0x0D       ; R13 = Start Address L
ld hl, crtc_data
ld (hl), 0x00

; 4. CRTC address mode: linear, step 2 bytes, once per character, LX 64KB.
ld hl, crtc_addr
ld (hl), 0x14       ; R20
ld hl, crtc_data
ld (hl), 0b0000_0011  ; linear=1, step=2, addr_mode=003 (LX 64KB)

; 5. CRTC video control: internal bpp, 4 bpp, linear RGB palette.
ld hl, crtc_addr
ld (hl), 0x12       ; R18
ld hl, crtc_data
ld (hl), 0b0001_0010  ; linear_pixel=1, bpp_mode=10 (4bpp)

; 6. CRTC pixel rate: 8 bytes per 16 pixels (matches 4 bpp = 8 bytes/char).
ld hl, crtc_addr
ld (hl), 0x15       ; R21
ld hl, crtc_data
ld (hl), 0b01

; 7. Video mode register at 0x0140: 4 bpp linear, internal modes.
ld a, 0b0000_1100   ; bpp_mode=10, linear_mode=1, use_cpc_modes=0
ld (0x0140), a

; 8. Palette: 12-bit write mode, auto-increment on.
;    Palette control register at 0xFF0105.
ld a, 0b0010_0000   ; auto_increment=1, write_mode=00 (12-bit)
ld (0xFF0105), a
; Fill 16 entries (or 256) via palette index + data lo + data hi.

; 9. Re-enable display.
ld hl, crtc_addr
ld (hl), 1
ld hl, crtc_data
ld (hl), 40
```

## Return to full CPC compatibility

```asm
; Reset CRTC R20 to legacy sequencing.
ld hl, crtc_addr
ld (hl), 0x14
ld hl, crtc_data
ld (hl), 0x00        ; legacy MA/RA composition, addr_mode=000

; Video mode: use CPC gate array.
ld a, 0b0001_0000
ld (0x0140), a

; Palette: CPC mode.
ld a, 0b0000_0001    ; write_mode=01 (CPC)
ld (0xFF0105), a

; CPC-style palette writes at 0xBC00 with D7:D6 = 00/01/10.
```

## Quick reference — native register addresses in this build

| Address | Device | Register |
|---------|--------|----------|
| `0xFF0100` | Palette | Index |
| `0xFF0101` | Palette | Data low |
| `0xFF0102` | Palette | Data high |
| `0xFF0103` | Palette | Border low |
| `0xFF0104` | Palette | Border high |
| `0xFF0105` | Palette | Control |
| `0xFF0106` | Palette | Modifier |
| `0xFF0120` | CRTC | Address Register |
| `0xFF0121` | CRTC | Data Register |
| `0x0140` (native tag) | Pixel pipeline | Mode register |

> Native addresses are derived from the `cs_legacy` decode in `address_decoder.sv`; the pixel-pipeline register at `0x0140` is the reference-system native base from `04-pixel-pipeline.md`. If your build remaps `cs_system`/`cs_legacy`, re-derive the absolute addresses from `0xFF0000 + (sub_block << 9) + (device_slot << 5)`.

## Common pitfalls

1. **`R21` must match `bpp_mode`.** If `R21 = 00` (2 bytes/char) but `bpp_mode = 10` (4 bpp, needs 8 bytes/char), the pipeline sees only 2 bytes for 16 pixels and the line shifts.
2. **`R18` reset value is `0x00`**, not the `use_cpc_modes=1, bpp=01` claimed in the source comment. Always program R18 explicitly.
3. **`cfg_cpc_bpp_i` is tied to 0** in this build, so `use_cpc_modes=1` always selects 4 bpp.
4. **`R20[0]=1` enables the linear counter, but `cfg_linear_pixel_o` (which drives the pixel pipeline packing) is driven from `R18[4]`.** The two flags are independent: `R18[4]` selects linear *packing* inside a byte, `R20[0]` selects linear *addressing* of memory. Set both for a "modern" framebuffer.
5. **Palette contents are undefined after reset.** Fill entries before the first visible line, or leave display disabled until initialised.
6. **Legacy palette writes are read-as-zero.** Don't poll the palette to verify writes in CPC mode; check via native palette RAM reads if you need confirmation.
7. **A cycle that matches no device never ACKs** and trips the bus watchdog after ~32 bus clocks. Always check `wb_err`.
8. **CRTC R16/R17 and R5 are accepted but ignored.** Real hardware may respond, but on this implementation they do nothing.
9. **Video memory writes are not VSYNC-synced.** Swap framebuffer start registers (`R12`/`R13`/`R19`) during vertical blank if you want tear-free updates.
10. **`crtc_halt_o` stuck high** means the programmed total is too small for the fixed 720×480 HDMI grid. Software can poll this signal only if exposed by your platform glue; typically it manifests as a frozen display.

---
