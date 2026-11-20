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

{{auto:dma_sysdma_map}}

**✔ By design (RTL):** `wb_dma.sv` implements these registers.

### 2.3 Modes

[include](gen/dma_sysdma_modes.md)

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