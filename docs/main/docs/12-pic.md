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

**Table 2 — PIC Register Map (wb_z80_pic.sv)**

| Offset | Name | Description |
| --- | --- | --- |
| `0x00` | <a id="MASK_L"></a>**MASK_L** | — |
| `0x01` | <a id="MASK_H"></a>**MASK_H** | — |
| `0x02` | <a id="VECTOR"></a>**VECTOR** | — |
| `0x03` | <a id="STATUS_L"></a>**STATUS_L** | — |
| `0x04` | <a id="STATUS_H"></a>**STATUS_H** | — |
| `0x05` | <a id="PENDING_L"></a>**PENDING_L** | — |
| `0x06` | <a id="PENDING_H"></a>**PENDING_H** | — |
| `0x07` | <a id="CLEAR_L"></a>**CLEAR_L** | — |
| `0x08` | <a id="CLEAR_H"></a>**CLEAR_H** | — |

**MASK_L** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ_0_7"></a>**IRQ_0_7** | [7:0] | 8 | Mask, lines 0–7 (1 = enabled) |

**MASK_H** (`0x01`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ_8_15"></a>**IRQ_8_15** | [7:0] | 8 | Mask, lines 8–15 (1 = enabled) |

**VECTOR** (`0x02`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VEC"></a>**VEC** | [7:0] | 8 | Base vector for IM 2 (default 0xFF) |

**STATUS_L** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ_0_7"></a>**IRQ_0_7** | [7:0] | 8 | Status, lines 0–7 |

**STATUS_H** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ_8_15"></a>**IRQ_8_15** | [7:0] | 8 | Status, lines 8–15 |

**PENDING_L** (`0x05`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ_0_7"></a>**IRQ_0_7** | [7:0] | 8 | Pending, lines 0–7 |

**PENDING_H** (`0x06`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ_8_15"></a>**IRQ_8_15** | [7:0] | 8 | Pending, lines 8–15 |

**CLEAR_L** (`0x07`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="CLR_0_7"></a>**CLR_0_7** | [7:0] | 8 | Clear pending, lines 0–7 |

**CLEAR_H** (`0x08`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="CLR_8_15"></a>**CLR_8_15** | [7:0] | 8 | Clear pending, lines 8–15 |


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