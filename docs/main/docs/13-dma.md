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

**Table 3 — Blitter Register Map (lx_dma.sv)**

| Offset | Name | Description |
| --- | --- | --- |
| `0x00` | <a id="CTRL"></a>**CTRL** | — |
| `0x01` | <a id="STATUS"></a>**STATUS** | — |
| `0x02` | <a id="SRC_0"></a>**SRC_0** | — |
| `0x03` | <a id="SRC_1"></a>**SRC_1** | — |
| `0x04` | <a id="SRC_2"></a>**SRC_2** | — |
| `0x05` | <a id="DST_0"></a>**DST_0** | — |
| `0x06` | <a id="DST_1"></a>**DST_1** | — |
| `0x07` | <a id="DST_2"></a>**DST_2** | — |
| `0x08` | <a id="WIDTH_0"></a>**WIDTH_0** | — |
| `0x09` | <a id="WIDTH_1"></a>**WIDTH_1** | — |
| `0x0A` | <a id="HEIGHT_0"></a>**HEIGHT_0** | — |
| `0x0B` | <a id="HEIGHT_1"></a>**HEIGHT_1** | — |
| `0x0C` | <a id="SSTRIDE_0"></a>**SSTRIDE_0** | — |
| `0x0D` | <a id="SSTRIDE_1"></a>**SSTRIDE_1** | — |
| `0x0E` | <a id="DSTRIDE_0"></a>**DSTRIDE_0** | — |
| `0x0F` | <a id="DSTRIDE_1"></a>**DSTRIDE_1** | — |
| `0x10` | <a id="KEY"></a>**KEY** | — |

**CTRL** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:4] | 4 | Reserved |
| <a id="IRQ"></a>**IRQ** | [3] | 1 | IRQ on done |
| <a id="MODE"></a>**MODE** | [2:1] | 2 | 0=copy, 1=fill, 2=copy+transp |
| <a id="START"></a>**START** | [0] | 1 | Start transfer |

**STATUS** (`0x01`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:1] | 7 | Reserved |
| <a id="DONE"></a>**DONE** | [0] | 1 | Done pending (W 1 = clear) |

**SRC_0** (`0x02`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Physical source [7:0] |

**SRC_1** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Physical source [15:8] |

**SRC_2** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Physical source [23:16] |

**DST_0** (`0x05`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Physical dest [7:0] |

**DST_1** (`0x06`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Physical dest [15:8] |

**DST_2** (`0x07`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Physical dest [23:16] |

**WIDTH_0** (`0x08`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="W"></a>**W** | [7:0] | 8 | Bytes per line [7:0] |

**WIDTH_1** (`0x09`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="W"></a>**W** | [7:0] | 8 | Bytes per line [15:8] |

**HEIGHT_0** (`0x0A`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="H"></a>**H** | [7:0] | 8 | Lines [7:0] |

**HEIGHT_1** (`0x0B`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="H"></a>**H** | [7:0] | 8 | Lines [15:8] |

**SSTRIDE_0** (`0x0C`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="STR"></a>**STR** | [7:0] | 8 | Source stride (signed) [7:0] |

**SSTRIDE_1** (`0x0D`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="STR"></a>**STR** | [7:0] | 8 | Source stride (signed) [15:8] |

**DSTRIDE_0** (`0x0E`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="STR"></a>**STR** | [7:0] | 8 | Dest stride (signed) [7:0] |

**DSTRIDE_1** (`0x0F`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="STR"></a>**STR** | [7:0] | 8 | Dest stride (signed) [15:8] |

**KEY** (`0x10`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="KEY"></a>**KEY** | [7:0] | 8 | Fill byte / transparent color |


**✔ By design (RTL):** the register layout matches `lx_dma.sv`.

### 1.3 Modes

# Blitter Modes (CTRL[2:1])

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="Copy"></a>**Copy** | Read from SRC, write to DST |
| 1 | <a id="Fill"></a>**Fill** | Write KEY to DST |
| 2 | <a id="Copy_with_transparent"></a>**Copy with transparent** | Read from SRC; if byte == KEY, skip the write |


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

**Table 4 — SysDMA Register Map (wb_dma.sv)**

| Offset | Name | Description |
| --- | --- | --- |
| `0x00` | <a id="SRC_ADDR_ch_"></a>**SRC_ADDR[ch]** | — |
| `0x10` | <a id="DST_ADDR_ch_"></a>**DST_ADDR[ch]** | — |
| `0x20` | <a id="COUNT_ch_"></a>**COUNT[ch]** | — |
| `0x30` | <a id="CONTROL_ch_"></a>**CONTROL[ch]** | — |
| `0x31` | <a id="STATUS_ch_"></a>**STATUS[ch]** | — |
| `0x40` | <a id="IMASK"></a>**IMASK** | — |
| `0x41` | <a id="DONE_CLEAR"></a>**DONE_CLEAR** | — |
| `0x42` | <a id="ERROR_CLEAR"></a>**ERROR_CLEAR** | — |
| `0x43` | <a id="VERSION"></a>**VERSION** | — |

**SRC_ADDR[ch]** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Source address (24 bits) |

**DST_ADDR[ch]** (`0x10`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Destination address (24 bits) |

**COUNT[ch]** (`0x20`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="COUNT"></a>**COUNT** | [7:0] | 8 | Transfer count (24 bits) |

**CONTROL[ch]** (`0x30`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:6] | 2 | Reserved |
| <a id="MODE"></a>**MODE** | [5] | 1 | 0=Demand, 1=Block |
| <a id="ENABLE"></a>**ENABLE** | [4] | 1 | Enable channel |
| <a id="DST_CTRL"></a>**DST_CTRL** | [3:2] | 2 | Dest control |
| <a id="SRC_CTRL"></a>**SRC_CTRL** | [1:0] | 2 | Source control |

**STATUS[ch]** (`0x31`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:2] | 6 | Reserved |
| <a id="ERROR"></a>**ERROR** | [1] | 1 | Transfer error |
| <a id="DONE"></a>**DONE** | [0] | 1 | Transfer done |

**IMASK** (`0x40`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:4] | 4 | Reserved |
| <a id="MASK"></a>**MASK** | [3:0] | 4 | Interrupt mask per channel |

**DONE_CLEAR** (`0x41`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:4] | 4 | Reserved |
| <a id="CLR"></a>**CLR** | [3:0] | 4 | Clear DONE flags |

**ERROR_CLEAR** (`0x42`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:4] | 4 | Reserved |
| <a id="CLR"></a>**CLR** | [3:0] | 4 | Clear ERROR flags |

**VERSION** (`0x43`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VER"></a>**VER** | [7:0] | 8 | Version / features |


**✔ By design (RTL):** `wb_dma.sv` implements these registers.

### 2.3 Modes

# SysDMA Transfer Modes

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="Demand"></a>**Demand** | Transfer driven by DRQ/DACK handshake |
| 1 | <a id="Block"></a>**Block** | Transfer entire block without handshake |


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