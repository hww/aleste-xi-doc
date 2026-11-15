# LX Magic Sound 2 (rev. A)

**Status:** planned baseline. Tested in simulation only (FPGA toolchain, module-level tests). **Never produced sound on real hardware** — there was no code to run it on the board.
**See also:** `lx_magic_sound_rev_c.md` (working implementation), `lx_rtl_reference.md` (addresses).

**RTL:** `magic_sound_2.sv` + 6 modules (simulation only).
**Address:** page 7 (same as rev. C; see `lx_rtl_reference.md`).

---

## 0. How to read this document

This is the **planned baseline** (rev. A). It was designed and tested in simulation, but never on real hardware. It is **not** the working implementation.

The working implementation is **rev. C** (`lx_magic_sound_rev_c.md`). Where rev. A and rev. C differ, **rev. C is what exists**. Rev. A is the baseline that rev. C was measured against.

### Markers

| Marker | Meaning |
|---|---|
| **✔ By design** | An intentional decision in rev. A. |
| **⚠ Changed in rev. C** | The working implementation differs. See rev. C. |
| **⚠ Not in rev. C** | Present in rev. A, not implemented in rev. C. Desirable to return. |

---

## 1. Motivation

The original Magic Sound (1990s) had four "birth defects":

1. **Sample length limited to 64 KB.**
2. **Volume ~6 bits per channel.**
3. **No stereo.**
4. **Loop restart required the CPU.**

Magic Sound 2 (rev. A) fixes all four:

- 24-bit address space (16 MB), so samples can be arbitrarily long.
- 8-bit volume per channel (left and right), plus global volume.
- Stereo output.
- Automatic loop (`LOOP_START` / `LOOP_END`), no CPU needed.

---

## 2. Architecture

### 2.1 Channels
- **4 channels** (`NUM_CHANNELS = 4`). 8 channels would be desirable (option).

### 2.2 Sample format
- **16-bit samples** (`SW = 16`). Signed.

### 2.3 Frequency
- **96 kHz** sample rate (`SAMPLE_RATE_HZ = 96_000` in `ms2_pkg.sv`).

### 2.4 Wishbone
- **Slave:** 8-bit (CPU side).
- **Master:** **16-bit** (`SW = 16`) — for memory reads.

### 2.5 Output
- **I2S** (`ms2_i2s_tx.sv`): `i2s_bclk_o`, `i2s_lrclk_o`, `i2s_data_o`. Stereo.

### 2.6 Loop
- **Two points:** `LOOP_START` and `LOOP_END` (24 bits each).
- Automatic loop, no CPU. **Ping-pong** mode (`CH_CTRL[2]`).

### 2.7 Step
- **16.16 fixed-point** (32 bits).
- `step = (desired_frequency << 16) / sample_rate`.

### 2.8 Timer
- `TIMER_VAL` (16 bits) + `TIMER_CTRL` (8 bits). 300 Hz music timer.

### 2.9 Interrupts
- IRQ on EOF (`CH_CTRL[3]`). Timer IRQ (`IRQ_CTRL[0]`). DMA error → NMI (`IRQ_CTRL[1]`).

### 2.10 DMA error handling

When the DMA reads memory and the memory controller returns a timeout (watchdog), the sound card must:

1. Latch the error bit (`STATUS[2]` = any channel error, `STATUS[4]` = DMA error).
2. Enter an error state.
3. Signal the error (IRQ/NMI).

**✔ By design (rev. A):** error handling is part of the status and interrupt design. `DMA_ERR_CLR` (global `0x05`) clears the flags.

> **⚠ Not in rev. C:** DMA error handling is **not implemented** in rev. C. It is desirable to return it. See `lx_magic_sound_rev_c.md` §5.

---

## 3. Registers

### 3.1 Global registers
![Rev. A: Global Registers Map](gen/ms2a_global_map.svg)

*Figure 1 — Rev. A: Global Registers Map*

**Table 1 — Rev. A: Global Registers Map**

| Offset | Name | Description |
| --- | --- | --- |
| `0x00` | <a id="GLOBAL_CR"></a>**GLOBAL_CR** | — |
| `0x01` | <a id="GLOBAL_VOL_L"></a>**GLOBAL_VOL_L** | — |
| `0x02` | <a id="GLOBAL_VOL_R"></a>**GLOBAL_VOL_R** | — |
| `0x03` | <a id="STATUS"></a>**STATUS** | — |
| `0x04` | <a id="IRQ_CTRL"></a>**IRQ_CTRL** | — |
| `0x05` | <a id="DMA_ERR_CLR"></a>**DMA_ERR_CLR** | — |
| `0x10` | <a id="TIMER_VAL"></a>**TIMER_VAL** | — |
| `0x11` | <a id="TIMER_VAL_H"></a>**TIMER_VAL_H** | — |
| `0x12` | <a id="TIMER_CTRL"></a>**TIMER_CTRL** | — |

**GLOBAL_CR** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RST"></a>**RST** | [1] | 1 | Reset |
| <a id="EN"></a>**EN** | [0] | 1 | Enable |

**GLOBAL_VOL_L** (`0x01`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VOL_L"></a>**VOL_L** | [7:0] | 8 | Global left volume |

**GLOBAL_VOL_R** (`0x02`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VOL_R"></a>**VOL_R** | [7:0] | 8 | Global right volume |

**STATUS** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="TMR_IRQ"></a>**TMR_IRQ** | [5] | 1 | Timer IRQ |
| <a id="DMA_ERR"></a>**DMA_ERR** | [4] | 1 | DMA error |
| <a id="EOF"></a>**EOF** | [3] | 1 | Any EOF |
| <a id="ERR"></a>**ERR** | [2] | 1 | Any error |
| <a id="CH_ACT"></a>**CH_ACT** | [1] | 1 | Any channel active |
| <a id="ACT"></a>**ACT** | [0] | 1 | Global active |

**IRQ_CTRL** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="DMA_NMI"></a>**DMA_NMI** | [1] | 1 | DMA error NMI enable |
| <a id="TMR_EN"></a>**TMR_EN** | [0] | 1 | Timer IRQ enable |

**DMA_ERR_CLR** (`0x05`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="CLR"></a>**CLR** | [0] | 1 | Write 1 to clear |

**TIMER_VAL** (`0x10`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VAL_L"></a>**VAL_L** | [7:0] | 8 | Timer value low |

**TIMER_VAL_H** (`0x11`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VAL_H"></a>**VAL_H** | [7:0] | 8 | Timer value high |

**TIMER_CTRL** (`0x12`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="CTRL"></a>**CTRL** | [7:0] | 8 | Timer control |


**Table 2 — Rev. A: Global Registers Map**

| Offset | Name | Description |
| --- | --- | --- |
| `0x00` | <a id="GLOBAL_CR"></a>**GLOBAL_CR** | — |
| `0x01` | <a id="GLOBAL_VOL_L"></a>**GLOBAL_VOL_L** | — |
| `0x02` | <a id="GLOBAL_VOL_R"></a>**GLOBAL_VOL_R** | — |
| `0x03` | <a id="STATUS"></a>**STATUS** | — |
| `0x04` | <a id="IRQ_CTRL"></a>**IRQ_CTRL** | — |
| `0x05` | <a id="DMA_ERR_CLR"></a>**DMA_ERR_CLR** | — |
| `0x10` | <a id="TIMER_VAL"></a>**TIMER_VAL** | — |
| `0x11` | <a id="TIMER_VAL_H"></a>**TIMER_VAL_H** | — |
| `0x12` | <a id="TIMER_CTRL"></a>**TIMER_CTRL** | — |

**GLOBAL_CR** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RST"></a>**RST** | [1] | 1 | Reset |
| <a id="EN"></a>**EN** | [0] | 1 | Enable |

**GLOBAL_VOL_L** (`0x01`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VOL_L"></a>**VOL_L** | [7:0] | 8 | Global left volume |

**GLOBAL_VOL_R** (`0x02`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VOL_R"></a>**VOL_R** | [7:0] | 8 | Global right volume |

**STATUS** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="TMR_IRQ"></a>**TMR_IRQ** | [5] | 1 | Timer IRQ |
| <a id="DMA_ERR"></a>**DMA_ERR** | [4] | 1 | DMA error |
| <a id="EOF"></a>**EOF** | [3] | 1 | Any EOF |
| <a id="ERR"></a>**ERR** | [2] | 1 | Any error |
| <a id="CH_ACT"></a>**CH_ACT** | [1] | 1 | Any channel active |
| <a id="ACT"></a>**ACT** | [0] | 1 | Global active |

**IRQ_CTRL** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="DMA_NMI"></a>**DMA_NMI** | [1] | 1 | DMA error NMI enable |
| <a id="TMR_EN"></a>**TMR_EN** | [0] | 1 | Timer IRQ enable |

**DMA_ERR_CLR** (`0x05`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="CLR"></a>**CLR** | [0] | 1 | Write 1 to clear |

**TIMER_VAL** (`0x10`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VAL_L"></a>**VAL_L** | [7:0] | 8 | Timer value low |

**TIMER_VAL_H** (`0x11`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VAL_H"></a>**VAL_H** | [7:0] | 8 | Timer value high |

**TIMER_CTRL** (`0x12`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="CTRL"></a>**CTRL** | [7:0] | 8 | Timer control |


### 3.2 Channel registers
Base addresses: channel 0 = `0x20`, channel 1 = `0x30`, channel 2 = `0x40`, channel 3 = `0x50`. Each channel has 16 registers.

![Rev. A: Channel Registers Map (Base 0x20/0x30/0x40/0x50)](gen/ms2a_channel_map.svg)

*Figure 2 — Rev. A: Channel Registers Map (Base 0x20/0x30/0x40/0x50)*

**Table 3 — Rev. A: Channel Registers Map (Base 0x20/0x30/0x40/0x50)**

| Offset | Name | Description |
| --- | --- | --- |
| `0x00` | <a id="CH_CTRL"></a>**CH_CTRL** | — |
| `0x01` | <a id="START_ADDR_0"></a>**START_ADDR_0** | — |
| `0x02` | <a id="START_ADDR_1"></a>**START_ADDR_1** | — |
| `0x03` | <a id="START_ADDR_2"></a>**START_ADDR_2** | — |
| `0x04` | <a id="END_ADDR_0"></a>**END_ADDR_0** | — |
| `0x05` | <a id="END_ADDR_1"></a>**END_ADDR_1** | — |
| `0x06` | <a id="END_ADDR_2"></a>**END_ADDR_2** | — |
| `0x07` | <a id="LOOP_START_0"></a>**LOOP_START_0** | — |
| `0x08` | <a id="LOOP_START_1"></a>**LOOP_START_1** | — |
| `0x09` | <a id="LOOP_START_2"></a>**LOOP_START_2** | — |
| `0x0A` | <a id="LOOP_END_0"></a>**LOOP_END_0** | — |
| `0x0B` | <a id="LOOP_END_1"></a>**LOOP_END_1** | — |
| `0x0C` | <a id="LOOP_END_2"></a>**LOOP_END_2** | — |
| `0x0D` | <a id="STEP_0"></a>**STEP_0** | — |
| `0x0E` | <a id="STEP_1"></a>**STEP_1** | — |
| `0x0F` | <a id="STEP_2"></a>**STEP_2** | — |

**CH_CTRL** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VOL_L"></a>**VOL_L** | [7:4] | 4 | Volume L (4-bit) |
| <a id="IRQ"></a>**IRQ** | [3] | 1 | IRQ on EOF |
| <a id="VOL_R"></a>**VOL_R** | [3:0] | 4 | Volume R (4-bit) |
| <a id="PP"></a>**PP** | [2] | 1 | Ping-pong |
| <a id="LOOP"></a>**LOOP** | [1] | 1 | Loop |
| <a id="EN"></a>**EN** | [0] | 1 | Enable |

**START_ADDR_0** (`0x01`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Start address [7:0] |

**START_ADDR_1** (`0x02`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Start address [15:8] |

**START_ADDR_2** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Start address [23:16] |

**END_ADDR_0** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | End address [7:0] |

**END_ADDR_1** (`0x05`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | End address [15:8] |

**END_ADDR_2** (`0x06`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | End address [23:16] |

**LOOP_START_0** (`0x07`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Loop start [7:0] |

**LOOP_START_1** (`0x08`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Loop start [15:8] |

**LOOP_START_2** (`0x09`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Loop start [23:16] |

**LOOP_END_0** (`0x0A`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Loop end [7:0] |

**LOOP_END_1** (`0x0B`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Loop end [15:8] |

**LOOP_END_2** (`0x0C`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Loop end [23:16] |

**STEP_0** (`0x0D`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="STEP"></a>**STEP** | [7:0] | 8 | Step fraction [7:0] |

**STEP_1** (`0x0E`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="STEP"></a>**STEP** | [7:0] | 8 | Step fraction [15:8] |

**STEP_2** (`0x0F`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="STEP"></a>**STEP** | [7:0] | 8 | Step integer [23:16] |


**Table 4 — Rev. A: Channel Registers Map (Base 0x20/0x30/0x40/0x50)**

| Offset | Name | Description |
| --- | --- | --- |
| `0x00` | <a id="CH_CTRL"></a>**CH_CTRL** | — |
| `0x01` | <a id="START_ADDR_0"></a>**START_ADDR_0** | — |
| `0x02` | <a id="START_ADDR_1"></a>**START_ADDR_1** | — |
| `0x03` | <a id="START_ADDR_2"></a>**START_ADDR_2** | — |
| `0x04` | <a id="END_ADDR_0"></a>**END_ADDR_0** | — |
| `0x05` | <a id="END_ADDR_1"></a>**END_ADDR_1** | — |
| `0x06` | <a id="END_ADDR_2"></a>**END_ADDR_2** | — |
| `0x07` | <a id="LOOP_START_0"></a>**LOOP_START_0** | — |
| `0x08` | <a id="LOOP_START_1"></a>**LOOP_START_1** | — |
| `0x09` | <a id="LOOP_START_2"></a>**LOOP_START_2** | — |
| `0x0A` | <a id="LOOP_END_0"></a>**LOOP_END_0** | — |
| `0x0B` | <a id="LOOP_END_1"></a>**LOOP_END_1** | — |
| `0x0C` | <a id="LOOP_END_2"></a>**LOOP_END_2** | — |
| `0x0D` | <a id="STEP_0"></a>**STEP_0** | — |
| `0x0E` | <a id="STEP_1"></a>**STEP_1** | — |
| `0x0F` | <a id="STEP_2"></a>**STEP_2** | — |

**CH_CTRL** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VOL_L"></a>**VOL_L** | [7:4] | 4 | Volume L (4-bit) |
| <a id="IRQ"></a>**IRQ** | [3] | 1 | IRQ on EOF |
| <a id="VOL_R"></a>**VOL_R** | [3:0] | 4 | Volume R (4-bit) |
| <a id="PP"></a>**PP** | [2] | 1 | Ping-pong |
| <a id="LOOP"></a>**LOOP** | [1] | 1 | Loop |
| <a id="EN"></a>**EN** | [0] | 1 | Enable |

**START_ADDR_0** (`0x01`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Start address [7:0] |

**START_ADDR_1** (`0x02`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Start address [15:8] |

**START_ADDR_2** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Start address [23:16] |

**END_ADDR_0** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | End address [7:0] |

**END_ADDR_1** (`0x05`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | End address [15:8] |

**END_ADDR_2** (`0x06`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | End address [23:16] |

**LOOP_START_0** (`0x07`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Loop start [7:0] |

**LOOP_START_1** (`0x08`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Loop start [15:8] |

**LOOP_START_2** (`0x09`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Loop start [23:16] |

**LOOP_END_0** (`0x0A`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Loop end [7:0] |

**LOOP_END_1** (`0x0B`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Loop end [15:8] |

**LOOP_END_2** (`0x0C`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Loop end [23:16] |

**STEP_0** (`0x0D`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="STEP"></a>**STEP** | [7:0] | 8 | Step fraction [7:0] |

**STEP_1** (`0x0E`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="STEP"></a>**STEP** | [7:0] | 8 | Step fraction [15:8] |

**STEP_2** (`0x0F`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="STEP"></a>**STEP** | [7:0] | 8 | Step integer [23:16] |


---

## 4. Programming example

```asm
; Channel 0: play a 44000 Hz sample with loop
ld a, %10010001       ; enable + loop + vol L=9, vol R=1
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

; Loop start = 0x100000
ld a, 0x00
ld (0x27), a
ld a, 0x00
ld (0x28), a
ld a, 0x10
ld (0x29), a

; Loop end = 0x100FFF
ld a, 0xFF
ld (0x2A), a
ld a, 0x0F
ld (0x2B), a
ld a, 0x10
ld (0x2C), a

; Step = 44000/96000 ≈ 0.45833 (16.16)
ld a, 0xA3
ld (0x2D), a
ld a, 0x70
ld (0x2E), a
ld a, 0x00
ld (0x2F), a
ld a, 0x00
ld (0x2F + 1), a
```

---

## 5. What differs from rev. C

### ⚠ Changed in rev. C
| Aspect | Rev. A | Rev. C |
|---|---|---|
| Sample format | 16-bit only | 8/16-bit selectable |
| Frequency | 96 kHz | 48 kHz |
| Wishbone master | 16-bit | 8-bit |
| Volume location | `CH_CTRL[7:4]/[3:0]` (4+4, scaled) | `+A` / `+B` (8-bit each) |
| Ping-pong | yes | no |
| Loop | `LOOP_START` + `LOOP_END` (2 points) | `LOOP` (1 point) |
| Step | 16.16 (32-bit) | 8.16 (24-bit) |
| I2S | yes | no (analog `out_l`, `out_r`) |
| Timer | `TIMER_VAL` + `TIMER_CTRL` | `TIMER_LO` / `TIMER_HI` |
| Status | error / DMA / EOF / timer | EOF / playing (per channel) |

### ⚠ Not in rev. C
| Feature | Why desirable |
|---|---|
| **DMA error handling** | When DMA reads memory and the memory controller returns a timeout (watchdog), the sound card must latch the error, enter an error state, and signal it (IRQ/NMI). This is a **stability element**. |
| `LOOP_START` / `LOOP_END` | 2-point loop is more flexible than 1-point. |
| `PINGPONG` | Ping-pong is useful for some samples. |
| `I2S` | Digital output, useful for high-quality codecs. |

---

## 6. Open questions

1. **DMA error handling** — desirable to return. This is a stability element, not a feature. *TBD.*
2. **8 channels** — option, not required. *TBD.*
3. **I2S** — option. *TBD.*
4. **Ping-pong** — option. *TBD.*
5. **`LOOP_START` / `LOOP_END`** — option. *TBD.*

---

*End of document.*
