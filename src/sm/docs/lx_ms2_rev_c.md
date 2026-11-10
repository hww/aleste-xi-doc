# LX Magic Sound 2 (rev. C)

**Status:** working implementation (Carlos). **Produces sound on real
hardware.**
**See also:** `lx_magic_sound_rev_a.md` (planned baseline),
`lx_rtl_reference.md` (addresses).

**RTL:** `lx_ms2.sv` (48 kHz, 8/16 bit, page 7).
**Address:** page 7 (`FF0380–FF03FF`). See `lx_rtl_reference.md`.

---

## 0. How to read this document

This is the **working implementation** (rev. C). It produces sound on
real hardware.

It differs from the **planned baseline** (rev. A). Where rev. A and
rev. C differ, **rev. C is what exists**. Rev. A is the baseline that
rev. C was measured against.

### Markers

| Marker | Meaning |
|---|---|
| **✔ By design** | An intentional decision in rev. C. |
| **✔ Improved by rev. C** | Rev. C is better than rev. A. |
| **✔ Simplified by rev. C** | Rev. C is simpler than rev. A (compromise, not worse). |
| **⚠ Not in rev. C** | Present in rev. A, not implemented in rev. C. Desirable to return. |

---

## 1. Motivation

The original Magic Sound (1990s) had four "birth defects":

1. **Sample length limited to 64 KB.**
2. **Volume ~6 bits per channel.**
3. **No stereo.**
4. **Loop restart required the CPU.**

Magic Sound 2 (rev. C) fixes all four:

- 24-bit address space (16 MB).
- 8-bit volume per channel (left and right), plus global volume.
- Stereo output.
- Automatic loop (`LOOP`), no CPU.

---

## 2. Architecture

### 2.1 Channels

- **4 channels** (`c_play[4]`, `c_start[4]`, `c_end[4]`, `c_lpos[4]`,
  `c_step[4]`, `c_vol_l[4]`, `c_vol_r[4]`).
- 8 channels would be desirable (option, not required in rev. C).

### 2.2 Sample format

- **8 or 16 bits**, selectable per channel (`CH_CTRL[2]`).
- Signed.
- 16-bit samples are little-endian.

### 2.3 Frequency

- **48 kHz** sample rate (`RATE_HZ = 48_000`).

### 2.4 Wishbone

- **Slave:** 8-bit (CPU side).
- **Master:** **8-bit** (`dma_dat_i[7:0]`) — for memory reads.

### 2.5 Output

- **Analog** `out_l`, `out_r` (16-bit signed).
- No I2S.

### 2.6 Loop

- **One point:** `LOOP` (24 bits) — where to return when `END` is
  reached.
- Automatic loop, no CPU.

### 2.7 Step

- **8.16 fixed-point** (24 bits).
- `010000h = 48 kHz` (1.0 in 8.16).

### 2.8 Timer

- `TIMER_LO` / `TIMER_HI` (16 bits) — period in 48 kHz samples.
- `160 = 300 Hz`, `960 = 50 Hz`.

### 2.9 Interrupts

- IRQ on EOF (`CH_CTRL[3]`, `IRQ_CTRL[0]`).
- Timer IRQ (`IRQ_CTRL[1]`).
- **No DMA error NMI** (not implemented).

### 2.10 DMA error handling

> **⚠ Not in rev. C.** When the DMA reads memory and the memory
> controller returns a timeout (watchdog), the sound card must latch
> the error, enter an error state, and signal it (IRQ/NMI). This is a
> **stability element**. Rev. C does not implement it. It is desirable
> to return it in a future revision.

---

## 3. Registers

### 3.1 Global registers

| Offset | Name | R/W | Bits |
|---|---|---|---|
| `0x00` | `CTRL` | RW | `[0]` enable MS2 (if not, silence and no DMA) |
| `0x01` | `VOL_L` | RW | `[7:0]` global left volume (0–255, 255 = 1) |
| `0x02` | `VOL_R` | RW | `[7:0]` global right volume |
| `0x03` | `STATUS` | R | `[3:0]` EOF per channel (sticky); `[7:4]` playing per channel |
| `0x03` | `STATUS` (write) | W | `[3:0]` 1 = clear EOF for that channel |
| `0x04` | `IRQ_CTRL` | RW | `[0]` EOF IRQ enable (channels with `CH_CTRL[3]`); `[1]` timer IRQ enable |
| `0x05` | `IRQ_STAT` | R | `[0]` EOF pending; `[1]` timer pending |
| `0x05` | `IRQ_STAT` (write) | W | `[1:0]` 1 = clear |
| `0x10` | `TIMER_LO` | RW | `[7:0]` timer period low |
| `0x11` | `TIMER_HI` | RW | `[15:8]` timer period high (0 = stopped) |

### 3.2 Channel registers

Base addresses: channel 0 = `0x20`, channel 1 = `0x30`, channel 2 =
`0x40`, channel 3 = `0x50`. Each channel has 16 registers.

| Offset | Name | R/W | Bits |
|---|---|---|---|
| `+0` | `CTRL` | RW | `[0]` play (on set, starts at START); `[1]` loop; `[2]` 16-bit samples (else 8-bit); `[3]` IRQ on EOF |
| `+1` | `START_0` | RW | `[7:0]` |
| `+2` | `START_1` | RW | `[15:8]` |
| `+3` | `START_2` | RW | `[23:16]` (applies the full 24-bit value) |
| `+4` | `END_0` | RW | `[7:0]` |
| `+5` | `END_1` | RW | `[15:8]` |
| `+6` | `END_2` | RW | `[23:16]` (applies) |
| `+7` | `LOOP_0` | RW | `[7:0]` |
| `+8` | `LOOP_1` | RW | `[15:8]` |
| `+9` | `LOOP_2` | RW | `[23:16]` (applies) |
| `+A` | `VOL_L` | RW | `[7:0]` channel left volume |
| `+B` | `VOL_R` | RW | `[7:0]` channel right volume |
| `+C` | `STEP_0` | RW | `[7:0]` (8.16, fraction) |
| `+D` | `STEP_1` | RW | `[15:8]` (fraction) |
| `+E` | `STEP_2` | RW | `[23:16]` (integer; applies the full 24-bit value) |
| `+F` | status | R | `[0]` playing; `[1]` EOF; `[7:4]` high byte of position |

### 3.3 Bit fields (summary)

| Register | Bits |
|---|---|
| `CTRL[0]` | enable MS2 |
| `STATUS[3:0]` | EOF per channel |
| `STATUS[7:4]` | playing per channel |
| `IRQ_CTRL[0]` | EOF IRQ enable |
| `IRQ_CTRL[1]` | timer IRQ enable |
| `IRQ_STAT[0]` | EOF pending |
| `IRQ_STAT[1]` | timer pending |
| `CH_CTRL[0]` | play |
| `CH_CTRL[1]` | loop |
| `CH_CTRL[2]` | 16-bit samples |
| `CH_CTRL[3]` | IRQ on EOF |
| `+F[0]` | playing |
| `+F[1]` | EOF |

---

## 4. Programming example

```asm
; Channel 0: play a 44000 Hz sample with loop
ld a, %00001011       ; play + loop + IRQ on EOF (8-bit samples)
ld (0x20), a          ; CH_CTRL

; Start address = 0x100000
ld a, 0x00
ld (0x21), a
ld a, 0x00
ld (0x22), a
ld a, 0x10
ld (0x23), a

; End address = 0x100FFF
ld a, 0xFF
ld (0x24), a
ld a, 0x0F
ld (0x25), a
ld a, 0x10
ld (0x26), a

; Loop = 0x100000
ld a, 0x00
ld (0x27), a
ld a, 0x00
ld (0x28), a
ld a, 0x10
ld (0x29), a

; Volume L / R = max
ld a, 0xFF
ld (0x2A), a
ld (0xFF)
ld (0x2B), a

; Step = 44000/48000 ≈ 0.91667 (8.16) = 0xEAAAA... 
; 0.91667 * 65536 ≈ 0xEAAA (fraction)
ld a, 0xAA
ld (0x2C), a
ld a, 0xEA
ld (0x2D), a
ld a, 0x00
ld (0x2E), a
```

---

## 5. What differs from rev. A

### ✔ Improved by rev. C

| Aspect | Rev. A | Rev. C |
|---|---|---|
| Sample format | 16-bit only | **8/16-bit selectable** |
| Wishbone master | 16-bit | **8-bit** (for 8-bit system) |
| Volume location | `CH_CTRL[7:4]/[3:0]` (4+4, scaled) | **`+A`/`+B` (8-bit each)** |

### ✔ Simplified by rev. C

| Aspect | Rev. A | Rev. C |
|---|---|---|
| Frequency | 96 kHz | 48 kHz (neutral) |
| Ping-pong | yes | **no** |
| Loop | `LOOP_START` + `LOOP_END` | **`LOOP` (1 point)** |
| Step | 16.16 | **8.16** |
| I2S | yes | **no** (analog) |
| Timer | `TIMER_VAL` + `TIMER_CTRL` | **`TIMER_LO` / `TIMER_HI`** |
| Status | error / DMA / EOF / timer | **EOF / playing per channel** |

### ⚠ Not in rev. C

| Feature | Why desirable |
|---|---|
| **DMA error handling** | When DMA reads memory and the memory controller returns a timeout (watchdog), the sound card must latch the error, enter an error state, and signal it (IRQ/NMI). This is a **stability element**. |
| `LOOP_START` / `LOOP_END` | 2-point loop is more flexible than 1-point. |
| `PINGPONG` | Ping-pong is useful for some samples. |
| `I2S` | Digital output, useful for high-quality codecs. |
| `DMA_ERR_CLR` | Clear DMA error flags. |
| `TIMER_CTRL` | Separate timer control register. |

---

## 6. Open questions

1. **DMA error handling** — desirable to return. This is a stability
   element, not a feature. *TBD.*
2. **8 channels** — option, not required. *TBD.*
3. **I2S** — option. *TBD.*
4. **Ping-pong** — option. *TBD.*
5. **`LOOP_START` / `LOOP_END`** — option. *TBD.*

---

*End of document.*
