# LX PIC Controller

## 0. How to read this document

This document describes the **PIC** (interrupt controller): its
registers, bits, priority and INT generation. It does **not** contain
the address; the address is in `lx_rtl_reference.md` §2.

### Markers

| Marker | Meaning |
|---|---|
| **✔ By design** | An intentional RTL decision. |
| **⚠ Spec:** | The old specification differs from the RTL. RTL is authoritative. |
| **⚠ Outdated:** | The old document may be stale. |

---

## 1. Purpose

The PIC collects interrupt requests from **16 IRQ lines**, latches them,
applies a mask, and asserts `INT` to the Z80 when at least one enabled
line is pending.

**✔ By design (RTL):** `wb_z80_pic.sv` implements 16 IRQ lines,
edge-sensitive, with a priority encoder (bit 15 highest, bit 0 lowest).

> **⚠ Spec:** Old `lx_pic_controller.md` described a **hierarchical**
> controller (Master PIC + peripheral controllers, "who interrupted" vs
> "what happened"). The RTL is **flat**: 16 lines, one priority encoder.
> **RTL is authoritative.** The hierarchical description is an idea,
> not a current fact.

---

## 2. Registers

The PIC has **8 registers**, 8 bits each, at offsets `0x0`–`0x8` from
the base address.

| Offset | Register | R/W | Purpose |
|---|---|---|---|
| `0x0` | `MASK_L` | RW | Mask, lines 0–7 (1 = enabled) |
| `0x1` | `MASK_H` | RW | Mask, lines 8–15 (1 = enabled) |
| `0x2` | `VECTOR` | RW | Base vector for IM 2 |
| `0x3` | `STATUS_L` | R | Status, lines 0–7 |
| `0x4` | `STATUS_H` | R | Status, lines 8–15 |
| `0x5` | `PENDING_L` | R | Pending, lines 0–7 |
| `0x6` | `PENDING_H` | R | Pending, lines 8–15 |
| `0x7` | `CLEAR_L` | W | Clear pending, lines 0–7 (1 = clear) |
| `0x8` | `CLEAR_H` | W | Clear pending, lines 8–15 (1 = clear) |

**✔ By design (RTL):** the register layout matches `wb_z80_pic.sv`.

> **⚠ Spec:** Old `lx_pic_controller.md` described 16-bit registers and
> a different address. The RTL uses **8-bit registers** (low/high
> pairs). **RTL is authoritative.**

---

## 3. IRQ handling

### 3.1 Edge-sensitive latching

Each IRQ line is **edge-sensitive**: a rising edge (`irq_i & ~irq_i_prev`)
sets the corresponding bit in `PENDING`.

**✔ By design (RTL):** `irq_edge = irq_i & ~irq_i_prev`.

### 3.2 Priority

When multiple lines are pending and enabled, the **highest-numbered line
wins**: bit 15 has the highest priority, bit 0 the lowest.

**✔ By design (RTL):** priority encoder is a `casez` on `active_irqs`,
with bit 15 first.

### 3.3 INT generation

`INT` is asserted while any enabled line is pending, and is deasserted
when the CPU acknowledges (`int_ack_i`).

**✔ By design (RTL):** `int_req_o <= 1` when `any_irq`, `int_req_o <= 0`
when `int_ack_i`.

---

## 4. Interrupt vector (IM 2)

The `VECTOR` register holds the base vector for IM 2 mode. The RTL does
not generate the vector automatically; the CPU reads the `PENDING`
registers and the kernel dispatches.

**✔ By design (RTL):** `irq_vector` is a single 8-bit register,
default `0xFF` (RST 38h).

---

## 5. Relation to other documents

- **Address:** `lx_rtl_reference.md` §2.
- **MMU / privileges:** `lx_mmu.md`.
- **Trap to Supervisor:** `lx_mmu.md` §5.2 (the PIC is one of the
  sources; the trap mechanism itself is in the MMU).

---

## 6. Status

- **Reference.** Registers, bits and priority are as in the RTL
  (`wb_z80_pic.sv`).
- **Address** is in `lx_rtl_reference.md`.
- **⚠ Spec:** the old hierarchical description and the 16-bit registers
  do not match the RTL. RTL is authoritative.

---

*End of document.*