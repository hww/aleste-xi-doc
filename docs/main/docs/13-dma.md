# LX DMA / Blitter

## 0. How to read this document

LX has **two** DMA-related devices:

1. [Blitter](13-blitter.md) (`lx_dma.sv`) — 1 channel, 8-bit, copy/fill/transparent.
2. [SysDMA](13-sysdma.md) (`wb_dma.sv`) — 4 channels, 16-bit, DRQ/DACK.

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

*End of document.*