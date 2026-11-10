# LX DMA / Blitter

## 0. How to read this document

LX has **two** DMA-related devices:

1. **Blitter** (`lx_dma.sv`) — 1 channel, 8-bit, copy/fill/transparent.
2. **SysDMA** (`wb_dma.sv`) — 4 channels, 16-bit, DRQ/DACK.

This document describes **both**, separately. It does **not** contain
addresses; addresses are in `lx_rtl_reference.md` §2.

### Markers

| Marker | Meaning |
|---|---|
| **✔ By design** | An intentional RTL decision. |
| **⚠ Spec:** | The old specification differs from the RTL. RTL is authoritative. |
| **⚠ Outdated:** | The old document may be stale. |

---

## 1. Blitter (`lx_dma.sv`)

### 1.1 Purpose

The blitter copies and fills **2D rectangles** (width, height, source
and destination strides), byte by byte, through the second bus master.
It supports **copy**, **fill** and **copy with transparent colour**.

**✔ By design (RTL):** the blitter yields the bus for one cycle after
each byte (`gap`), so the sound chip (which shares the second master)
does not run out of samples during a long copy.

### 1.2 Registers

The blitter has **17 registers**, 8 bits each, at offsets `0x00`–`0x10`
from the base address.

| Offset | Register | R/W | Purpose |
|---|---|---|---|
| `0x00` | `CTRL` | W | bit 0 = start; bits 2–1 = mode (0 copy, 1 fill, 2 copy-with-transparent); bit 3 = IRQ on done. R: bit 0 = busy; bits 3–1 = written |
| `0x01` | `STATUS` | R/W | bit 0 = done pending; W 1 = clear |
| `0x02–0x04` | `SRC` | RW | physical source address (24 bits, low first) |
| `0x05–0x07` | `DST` | RW | physical destination address (24 bits, low first) |
| `0x08–0x09` | `WIDTH` | RW | bytes per line (0 = 65536) |
| `0x0A–0x0B` | `HEIGHT` | RW | lines (0 = 1) |
| `0x0C–0x0D` | `SSTRIDE` | RW | source line stride (signed) |
| `0x0E–0x0F` | `DSTRIDE` | RW | destination line stride (signed) |
| `0x10` | `KEY` | RW | fill byte or transparent colour |

**✔ By design (RTL):** the register layout matches `lx_dma.sv`.

### 1.3 Modes

| Mode | Value | Behaviour |
|---|---|---|
| Copy | 0 | read from `SRC`, write to `DST` |
| Fill | 1 | write `KEY` to `DST` |
| Copy with transparent | 2 | read from `SRC`; if byte == `KEY`, skip the write |

### 1.4 Interrupt

`irq_o = done` — the blitter asserts an interrupt when a transfer
completes and `CTRL[3]` (IRQ on done) was set.

**✔ By design (RTL):** `irq_o = done`.

### 1.5 Bus behaviour

The blitter asserts `dma_cyc_o` and `dma_we_o` for each byte, then
deasserts for one cycle (`gap`) so that the sound chip can use the bus.

**✔ By design (RTL):** `dma_cyc_o = ((st == T_RD) || (st == T_WR)) && !gap`.

### 1.6 Physical addresses

The blitter uses **physical** 24-bit addresses. In LX mode, the memory
the CPU sees at `C00000–C0FFFF` is at `410000–41FFFF`.

**✔ By design (RTL):** comment in `lx_dma.sv`.

---

## 2. SysDMA (`wb_dma.sv`)

### 2.1 Purpose

SysDMA is a **4-channel** DMA controller with **DRQ/DACK** handshake,
**16-bit** data path, and **demand** / **block** modes. It is on the
**memory / video side** of the 16→8 bridge.

> **⚠ Spec:** Old `lx_dma.md` described SysDMA with 4 channels,
> 16-bit data, DRQ/DACK. That description matches `wb_dma.sv`, but the
> **address** and the **width** in the old document were not consistent
> with the RTL. **RTL is authoritative.**

### 2.2 Registers

SysDMA has per-channel registers and common registers. The layout is in
`wb_dma.sv`; the exact byte offsets are `TBD: verify against RTL`.

| Register | Purpose |
|---|---|
| `SRC_ADDR[ch]` | source address (24 bits) |
| `DST_ADDR[ch]` | destination address (24 bits) |
| `COUNT[ch]` | transfer count (24 bits) |
| `CONTROL[ch]` | bits: `SRC_CTRL`, `DST_CTRL`, `ENABLE`, `MODE` |
| `STATUS[ch]` | bit 0 = `DONE`, bit 1 = `ERROR` |
| `IMASK` | interrupt mask |
| `DONE_CLEAR` | clear `DONE` flags |
| `ERROR_CLEAR` | clear `ERROR` flags |
| `VERSION` | version / features |

**✔ By design (RTL):** `wb_dma.sv` implements these registers.

### 2.3 Modes

| Mode | Value | Behaviour |
|---|---|---|
| Demand | 0 | one transfer per DRQ assertion |
| Block | 1 | transfer the whole block |

### 2.4 Arbitration

Fixed priority: channel 0 > channel 1 > channel 2 > channel 3.

**✔ By design (RTL):** `for (i = 0; i < CHANNELS; i++)` in `wb_dma.sv`.

### 2.5 Bus width

SysDMA uses a **16-bit** data path. It is on the memory / video side of
the bridge.

**✔ By design (RTL):** `DATA_WIDTH = 16` in `wb_dma.sv`.

---

## 3. Which DMA is used where

| Device | Location | Width | Use |
|---|---|---|---|
| Blitter (`lx_dma.sv`) | CPU side (after bridge) | 8-bit | Rectangle copy/fill, transparent copy |
| SysDMA (`wb_dma.sv`) | Memory/video side (before bridge) | 16-bit | Block transfers, DRQ/DACK peripherals |

**✔ By design:** the two DMAs are on **different sides** of the 16→8
bridge. They are not alternatives; they serve different parts of the
system.

> **⚠ Spec:** Old `lx_dma.md` treated them as one device. They are
> **two**. **RTL is authoritative.**

---

## 4. Relation to other documents

- **Addresses:** `lx_rtl_reference.md` §2.
- **Bus widths:** `lx_rtl_reference.md` §6.
- **MMU / privileges:** `lx_mmu.md`.
- **Legacy:** `lx_io.md` §3.

---

## 5. Status

- **Reference.** Registers, bits and modes are as in the RTL
  (`lx_dma.sv`, `wb_dma.sv`).
- **Addresses** are in `lx_rtl_reference.md`.
- **⚠ Spec:** the old `lx_dma.md` treated the two DMAs as one and did
  not match the RTL. RTL is authoritative.

---

*End of document.*