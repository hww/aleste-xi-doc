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

# 03 — CRTC (mc6845mod)

> Full register details are in the existing document `mc6845mod.md`. This section restates the parts that matter from a bus/memory-map perspective and points you at that document for per-bit semantics.

## Two access schemes, one register file

The CRTC exposes an Address Register + Data Register pair, exactly like a real MC6845:

* **Native decode** (`cfg_legacy_i = 0`, `wb_cs_i` asserted): `wb_adr[0]=0` selects Address Register, `wb_adr[0]=1` selects Data Register.
* **Legacy decode** (`cfg_legacy_i = 1`, `wb_tag[2] = 1`, `wb_adr[14] == WB_ADDRESS[14]`): `wb_adr[8]=0` selects Address Register, `wb_adr[8]=1` selects Data Register. `WB_ADDRESS` default is `0x6844` but only bit 14 is compared, giving a `0x4000`-sized window — the decoder places it at `0xBC00` so that bit 14 patterns match CPC wiring.

In both schemes, write the register index to Address Register, then read or write Data Register to get to R0–R21.

## Registers

* **R0–R15**: MC6845 standard — Horizontal Total/Displayed/Sync Position/Sync Widths, Vertical Total/Adjust/Displayed/Sync Position, Interlace/Skew, Max Scan, Cursor Start/End, Start Address (H/L), Cursor Address (H/L). Behaviour is 100% MC6845 except R5 (vertical adjust) and R16/R17 (light pen).
* **R18 — Video Control**: pixel depth and source selection.
* **R19 — High Address**: A23:A16 of the 24-bit video address.
* **R20 — Address Mode**: linear vs legacy addressing, step size, address rate, `cfg_addr_mode` hint.
* **R21 — Pixel Control**: byte fetch rate per character row (feeds `video_buffer.cfg_rate`).

See `mc6845mod.md` §4–§7 for bit-level definitions, and §9 for the strobe-rate table that ties `R21[1:0]` + `bpp_mode` to pixel/byte fetch rates. §13 of that document summarises what is legacy vs native.

## Observability

* `crtc_hsync_o` / `crtc_vsync_o` are interrupt sources in the CRTC domain.
* `crtc_newline_o` / `crtc_newframe_o` are HDMI-aligned — used by the scan doubler and by software that wants an exact line/frame anchor.
* `crtc_halt_o` asserts when a programmed total is reached before the next HDMI start trigger. In a working system this should never stay asserted; if polling sees it stuck, the CRTC has been programmed with a total too small for the fixed HDMI pixel grid.

## Reset defaults that matter to software

* `STANDARD="cpc"` (the build config of `video_ctrl.sv`): R0=63, R1=40, R2=46, R3=0xEE (14/14), R4=38, R6=25, R7=30, R9=7, R20=0x00.
* The current `video_ctrl.sv` ties `cfg_cpc_bpp_i` to zero and `STANDARD` to `"cpc"`, so video starts with a CPC-compatible geometry but with `bpp_mode` sourced from R18 (which resets to `0b00` = 1 bpp in this build — program R18 to override).

> The comments in `mc6845mod.sv` claim R18 resets to `use_cpc_modes=1, bpp_mode=01`, but the actual reset literal is `8'h00`. Program R18 explicitly on startup.

---

# 04 — Video Buffer Module

> This block is invisible to software except through the interaction between `cfg_rate`, the CRTC fetch rate, and memory bandwidth. The following is the software-facing summary; the original `03-video-buffer-module.md` describes the internal state machine.

## What it does

Double-buffered SDRAM → pixel pipeline stream. On each 16-pixel character interval it fetches exactly `cfg_rate`-many bytes and presents them one at a time to the pixel pipeline.

## `cfg_rate` (driven by CRTC R21[1:0])

| `cfg_rate` | Bytes per 16-px character | Typical bpp | Fetch behaviour |
|------------|---------------------------|-------------|------------------|
| `00` | 2 | 1 bpp | One 32-bit burst per character, reused for the whole row |
| `01` | 4 | 2 bpp | One burst per half-character |
| `10` | 8 | 4 bpp | Continuous fetch during DE |
| `11` | 16 | 8 bpp | Continuous fetch during DE |

Higher `cfg_rate` means higher SDRAM bandwidth consumption. At 720 visible pixels and 27 MHz pixel clock, the theoretical ceilings are ~13 MB/s, ~27 MB/s, ~54 MB/s, ~108 MB/s. The physical SDRAM provides ~200 MB/s peak, so all four modes are feasible if arbitration leaves room.

## Behaviour vs `de_i`

* When `de_i = 0`, no requests are asserted and the byte stream is zero-padded.
* When `de_i = 1`, the state machine requests 32-bit (two 16-bit words) bursts and feeds bytes out with `stb_byte_o`.
* `de_o` is a 2-pixel-clock delayed copy of `de_i` (used by the pipeline to align with `stb_pixel_i`).

## Practical constraints

* The buffer does not stall the pixel pipeline. If SDRAM cannot keep up, the output bytes are whatever was already in the buffer (i.e. visible corruption, not a bus error).
* Changing `cfg_rate` mid-frame is safe — the change takes effect on the next `stb_sync1` / `stb_sync2` boundary. Don't change it mid-character.
* The number of bytes fetched per character must match `bpp_mode` × 16, otherwise the pixel pipeline gets the wrong packing — see §05.

---

# 05 — Pixel Pipeline / Video Mode Controller

> This is the module documented in `04-pixel-pipeline.md` (register name `cfg` at native `0x0140` in the reference system). It owns the bpp / CPC-vs-linear decision.

## Control register at `0x0140` (TAG = Native IO)

```
bit 0-1  bpp_mode       00=1bpp, 01=2bpp, 10=4bpp, 11=8bpp
bit 2    linear_mode    0=CPC-style interleave, 1=linear packing
bit 3    reserved        write 0
bit 4    use_cpc_modes   0=use bpp_mode, 1=CPC Gate Array graphic_mode
bit 5-7  reserved        write 0
```

## Behaviour

* **`use_cpc_modes = 1`**: ignore `bpp_mode`/`linear_mode`, use the CPC Gate Array `graphic_mode[1:0]`:
  * `00` = Mode 0 (16 colors, 4 bpp, CPC interleaved)
  * `01` = Mode 1 (4 colors, 2 bpp, CPC interleaved)
  * `10` = Mode 2 (2 colors, 1 bpp, linear)
  * `11` = Mode 3 (16 colors, 4 bpp, CPC interleaved)
* **`use_cpc_modes = 0`**: use `bpp_mode` directly. `linear_mode` selects packing:
  * 1 bpp — linear only
  * 2 bpp — linear or CPC interleaved
  * 4 bpp — linear or CPC interleaved
  * 8 bpp — linear only (CPC interleave is meaningless at byte-per-pixel)

## Byte → pixel expansion

| bpp | Pixels per byte | Linear bit order | CPC interleave |
|-----|-----------------|------------------|----------------|
| 1 | 8 | MSB first | same as linear (Mode 2) |
| 2 | 4 | `[7:6][5:4][3:2][1:0]` | `[7,3][6,2][5,1][4,0]` |
| 4 | 2 | `[7:4][3:0]` | `[1,5,3,7][0,4,2,6]` |
| 8 | 1 | full byte | — |

CPC interleave matches real CPC hardware behaviour: pixels are sourced from bit-columns of two consecutive bytes, with the low-bit plane first.

## Interaction with the CRTC and video buffer

For correct display you must keep **three settings consistent**:

1. `bpp_mode` at `0x0140` (how many bits per pixel).
2. `R21[1:0]` in the CRTC (how many bytes per character are fetched).
3. Total visible byte count on the row (`R1` × bytes-per-character) ≤ SDRAM framebuffer size.

If `R21` fetch rate does not match `bpp_mode` × 16 pixels, the pipeline will see a wrong number of bytes per character and the image will shift horizontally.

## Mode change synchronisation

The pipeline latches `cfg_bpp_i` / `cfg_linear_i` on `stb_byte_i` (the memory fetch strobe), so writing the mode register mid-scanline is safe — the change takes effect at the next fetched byte. **However**, the CRTC does not automatically track the new bpp; a full mode switch requires updating `0x0140` *and* `R18`/`R21` within the same vertical blank to avoid tearing.

The `video_ctrl.sv` build in this tree **ties `cfg_cpc_bpp_i` to 0**, so `use_cpc_modes = 1` always selects mode 0 here. Program `bpp_mode` with `use_cpc_modes = 0` if you need anything other than 4 bpp.

## Reset state

`use_cpc_modes = 1`, `bpp_mode = 01`, `linear_mode = 0`.

---

# 06 — Color Palette

> Full documentation lives in `05-palette.md`. This section is the programmer-facing excerpt.

## Native register map (TAG = Native, base `0xFF0100` in this build)

| Offset | Name | R/W | Purpose |
|--------|------|-----|---------|
| `0x00` | Palette index | R/W | Selects palette entry (or border in CPC mode) |
| `0x01` | Palette data low | R/W | Low byte of color; also the single write port in CPC/MSX/YJK modes |
| `0x02` | Palette data high | R/W | High byte, 12-bit mode only |
| `0x03` | Border color low | R/W | Border low byte |
| `0x04` | Border color high | R/W | Border high byte |
| `0x05` | Control | R/W | See below |
| `0x06` | Modifier | R/W | OR/XOR mask applied to pixel index before lookup |

## Control register (`0x05`)

```
bit 0-1  palette_write_mode  00=12-bit, 01=CPC, 10=MSX, 11=YJK
bit 2-4  reserved
bit 5    auto_increment      1 = increment palette index after a data write
bit 6    modifier_type       0=OR, 1=XOR
bit 7    modifier_enable     1 = apply modifier to incoming pixel index
```

## Legacy CPC access (`0xBC00`, TAG = Legacy, D7 = 0)

Three Gate Array register classes, selected by D7:D6 of the data byte:

| D7:D6 | Function | Data bits |
|-------|----------|-----------|
| `00` | Set palette index | 5-bit index, bit 4 = border flag |
| `01` | Write palette color | 5-bit CPC hardware color (soft color 0–31) |
| `10` | Write border color | 5-bit CPC hardware color |

All three go through the CPC hardware color LUT, which preserves the "two hardware colors map to the same visual RGB" quirk of the real CPC. Reads in legacy mode return 0.

## Native color modes

* **12-bit**: direct 12-bit RGB, write low byte then high byte; auto-increment (if enabled) after the high byte write.
* **CPC**: legacy conversion via distributed ROM.
* **MSX**: 8-bit MSX2+ color index → 12-bit RGB.
* **YJK**: MSX2+ YJK space → 12-bit RGB.

## Modifier

`modifier_enable = 1` applies `mask OR idx` or `mask XOR idx` to the incoming pixel index before the palette lookup. This gives free palette banks (OR) or palette animation (XOR) without touching palette RAM.

## Border

The border color is a separate 12-bit register. In CPC legacy mode, writes through `0xBC00` (`D7:D6 = 10`) set the border through the same CPC color LUT as palette entries. In native modes, border writes are a direct 12-bit value.

## Reset state

12-bit write mode, auto-increment off, modifier disabled. Palette contents are undefined at reset — initialise before enabling display in native modes.

---

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

---

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