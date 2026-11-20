
# Blitter (`lx_dma.sv`)

## 1.1 Purpose

The blitter copies and fills **2D rectangles** (width, height, source
and destination strides), byte by byte, through the second bus master.
It supports **copy**, **fill** and **copy with transparent colour**.

**✔ By design (RTL):** the blitter yields the bus for one cycle after
each byte (`gap`), so the sound chip (which shares the second master)
does not run out of samples during a long copy.

## 1.2 Registers

The blitter has **17 registers**, 8 bits each, at offsets `0x00`–`0x10`
from the base address.

{{auto:dma_blitter_map}}

**✔ By design (RTL):** the register layout matches `lx_dma.sv`.

## 1.3 Modes

[include](gen/dma_blitter_modes.md)

## 1.4 Interrupt

`irq_o = done` — the blitter asserts an interrupt when a transfer
completes and `CTRL[3]` (IRQ on done) was set.

**✔ By design (RTL):** `irq_o = done`.

## 1.5 Bus behaviour

The blitter asserts `dma_cyc_o` and `dma_we_o` for each byte, then
deasserts for one cycle (`gap`) so that the sound chip can use the bus.

**✔ By design (RTL):** `dma_cyc_o = ((st == T_RD) || (st == T_WR)) && !gap`.

## 1.6 Physical addresses

The blitter uses **physical** 24-bit addresses. In LX mode, the memory
the CPU sees at `C00000–C0FFFF` is at `410000–41FFFF`.

**✔ By design (RTL):** comment in `lx_dma.sv`.

*End of document.*
