# LX PIC Controller

## 0. How to read this document

This document describes the **PIC** (interrupt controller): its
registers, bits, priority and INT generation. It does **not** contain
the address; the address is in `lx_rtl_reference.md` §2.

### Markers

| Marker | Meaning |
|---|---|
| **✎ By design** | An intentional RTL decision. |
| **⚠ Spec:** | The old specification differs from the RTL. RTL is authoritative. |
| **⚠ Outdated:** | The old document may be stale. |

---

## 1. Purpose

The PIC collects interrupt requests from **16 IRQ lines**, latches them,
applies a per-channel mask (`ENABLE`), applies per-channel priority
arbitration, and asserts `INT` to the Z80 when at least one enabled line
is pending and not already in service.

**✎ By design (RTL):** `lx_sys.sv` implements 16 IRQ lines,
edge-sensitive, with a per-channel priority field (0..7, 7 = highest)
and an `IN_SERVICE` state per channel. Arbitration picks the eligible
channel with the highest priority; ties are broken by the lowest channel
number.

> **⚠ Spec:** Old `lx_pic_controller.md` described a **hierarchical**
> controller (Master PIC + peripheral controllers, "who interrupted" vs
> "what happened"). The RTL is **flat**: 16 lines, one priority
> arbiter. **RTL is authoritative.** The hierarchical description is an
> idea, not a current fact.

**Line 6 is reserved for the internal timer** (`t_irq` from the system
timer). The external `irq_i[6]` input is ignored. All other external
lines 0–5 and 7–15 are usable by peripherals.

---

## 2. Registers

The PIC is decoded on the low 5 bits of the bus address
(`adr_i[4:0]`). The upper 3 bits must be `000` (`adr_i[7:5] == 3'b000`)
for the PIC to respond. Registers are 8 bits wide, at offsets `0x0`–`0xC`
from the base address.

{{auto:pic_regmap_v2}}

**✎ By design (RTL):** the register layout matches `lx_sys.sv`.

> **⚠ Spec:** Old `lx_pic_controller.md` described 16-bit registers and
> a different address. The RTL uses **8-bit registers** (low/high
> pairs). **RTL is authoritative.**

### 2.1. Access privileges

| Register | Read | Write |
|---|---|---|
| `COMMAND` (`+0`) | — (write-only) | **supervisor only** |
| `CLAIM` (`+1`) | both modes | — |
| `VECTOR` (`+2`) | both modes | **supervisor only** |
| `PENDING_L/H` (`+3`,`+4`) | both modes | — |
| `REPEAT_L/H` (`+5`,`+6`) | both modes | — |
| `IN_SERVICE_L/H` (`+7`,`+8`) | both modes | — |
| `ENABLE_L/H` (`+9`,`+A`) | both modes | — |
| `STATUS_L/H` (`+B`,`+C`) | both modes | — |

**✎ By design (RTL):** writes to `COMMAND` and `VECTOR` are gated by
`sup_i`. User-mode writes have **zero side effects** — the target
register, priority, and channel state are all left untouched. Reads
(including `CLAIM`) are permitted in both modes, so a user-mode
dispatcher can inspect and retire pending requests if the platform
grants it the bus.

> **⚠ Spec:** earlier documentation did not describe PIC write
> protection. RTL adds it. Platform policy may further restrict reads;
> the RTL only enforces the write side.

---

## 3. IRQ handling

### 3.1. Edge-sensitive latching

Each IRQ line is **edge-sensitive**: a rising edge sets the corresponding
bit in `PENDING`.

**✎ By design (RTL):** external IRQ lines pass through a two-flop
synchronizer before edge detection (`irq_edge = irq_sync & ~irq_prev`).
Line 6 is the internal timer request (`t_irq`), already synchronous, and
is **not** routed through the synchronizer.

### 3.2. Priority and COMMAND opcodes

Each channel has an independent 3-bit priority field, set via
`COMMAND` with bit 7 = 1:

```
COMMAND = 1 ppp cccc
          │ │   └─── channel (0..15)
          │ └─────── priority (0..7, 7 = highest)
          └───────── operand form (bit7 = 1)
```

When multiple channels are **eligible** (pending, enabled, and not
already in service), the channel with the **highest priority** wins.
Ties are broken by the **lowest channel number**.

Ordinary commands use bit 7 = 0:

```
COMMAND = 0 ooo cccc
          │ │   └─── channel (0..15)
          │ └─────── opcode (see table below)
          └───────── command form (bit7 = 0)
```

{{table:pic_command_ops_v2}}

**✎ By design (RTL):** priority only orders simultaneous requests. It
does **not** preempt an in-service channel. While a channel is in
service, it is excluded from `eligible` until `COMPLETE` is issued.
On the Z80, `DI` on interrupt entry makes this the natural model; nested
interrupts would require an explicit extension.

> **⚠ Spec:** the earlier revision used a fixed priority encoder (bit 15
> highest, bit 0 lowest) with no per-channel priority and no
> `IN_SERVICE` state. The current RTL replaces both. **RTL is
> authoritative.**

### 3.3. INT generation

`INT` is asserted while any channel is `eligible`:
`INT = |(PENDING & ENABLE & ~IN_SERVICE)`.

The CPU does **not** acknowledge through `int_ack_i` in the current
contract: `int_ack_i` is present in the interface for compatibility but
does not modify PIC state. Retirement is done by software:

- read `CLAIM` to pick and capture a channel (atomically clears its
  `PENDING`/`REPEAT` and sets `IN_SERVICE`);
- service the interrupt;
- write `COMMAND` opcode `COMPLETE` for that channel to clear
  `IN_SERVICE`.

**✎ By design (RTL):** `int_ack_i` is intentionally unused (kept in
the port list for future INTA support). See §3.5.

### 3.4. Repeat / overrun flag

Each channel carries a second state bit, `REPEAT`. It records that a
second (or further) request arrived on the same line while `PENDING`
was already asserted and had not yet been claimed. `REPEAT` is a boolean
overrun flag, not an event counter.

**✎ By design (RTL):** per channel:

- new request, `PENDING = 0` → `PENDING = 1`
- new request, `PENDING = 1` → `REPEAT = 1`
- `CLAIM` with `REPEAT = 1` → `PENDING` is cleared (the *old* request is
  consumed), `REPEAT = 0`; a new edge on the same clock is preserved as
  a fresh `PENDING`
- `CLAIM` with `REPEAT = 0` → `PENDING = 0`
- simultaneous `CLAIM` and new request → **set-dominant** (the new
  request is never lost)

`REPEAT` is exposed at `REPEAT_L`/`REPEAT_H` (`+5`/`+6`) and cleared by
`COMMAND` opcode `CLEAR_REPEAT` or `CLEAR_BOTH`. Masking a line blocks
delivery to the CPU (`INT`) but does **not** clear `PENDING` or
`REPEAT`.

This implements the PIC side of the `Pending`/`Repeat` contract from
`Alesta LX Hardware System Timer` §11.

### 3.5. Acknowledge vs. software retire

Two ways to retire a request exist in hardware:

- **`CLAIM`** (read, both modes) — atomically picks the highest-priority
  eligible channel, captures its result into the latch, clears its
  old `PENDING`/`REPEAT`, and sets `IN_SERVICE`.
- **`CLEAR_*` commands** (write `COMMAND`, supervisor only) — clear
  `PENDING` and/or `REPEAT` for a specific channel without going through
  `IN_SERVICE`.

`COMPLETE` releases `IN_SERVICE` only; it does **not** clear new pending
events that arrived during service.

**✎ By design (RTL):** the `CLAIM` result is captured into a register
(`claim_q`) at the strobe and returned on `dat_o` while `ack_o` is
asserted. This makes the returned value independent of the exact bus
cycle in which the bridge samples `dat_o`. The captured value is
`{VALID, REPEAT, 2'b00, channel}`.

If a new edge arrives on the same clock as `CLAIM`, it remains pending
as a new event; the *old* request is what `CLAIM` consumes.

> **⚠ Spec:** an earlier RTL revision used `int_ack_i` to drive the
> `Pending`/`Repeat` contract directly. The current contract separates
> CPU acknowledge (not used) from software `CLAIM` (used). Platforms
> that wire `int_ack_i` to the CPU INTA cycle should leave it unconnected
> or tie it to `0`; the PIC does not act on it.

---

## 4. Interrupt vector (IM 2)

The `VECTOR` register holds the base vector for IM 2 mode. Reset value is
`0xFF` (RST 38h).

**✎ By design (RTL):** `vector` is a single 8-bit register, reset
`0xFF` (RST 38h), written by supervisor mode only.

> **⚠ Spec:** an earlier RTL revision generated `int_vec_o = VECTOR +
> 2 * top_priority_line` in hardware. The current `LX PIC Controller`
> contract is that **the PIC does not generate the vector
> automatically**: the CPU reads `PENDING`/`REPEAT` (and `VECTOR`) and
> the kernel dispatches. If a platform still needs the hardware
> auto-vector, it must be re-added as an explicit, documented extension
> (`int_vec_o`), not assumed.

---

## 5. Bus contract

**✎ By design (RTL):** the module accepts exactly **one internal
operation per bus cycle**, regardless of how long `cs_i` stays
asserted. Internally, `bus_taken` latches the acceptance of the current
cycle; `rd`/`wr` are single-cycle strobes. When `cs_i` drops, the
module is ready for the next cycle.

Read data that depends on side-effecting reads (`CLAIM`) is captured
into a register at the strobe and returned on `dat_o` while `ack_o` is
asserted. This decouples the returned value from the exact cycle in
which the bridge samples `dat_o`.

`int_ack_i` is not used to modify PIC state. CPU acknowledge and
software `CLAIM` are separate operations.

---

## 6. Relation to other documents

- **Address:** `lx_rtl_reference.md` §2.
- **MMU / privileges:** `lx_mmu.md`.
- **Trap to Supervisor:** `lx_mmu.md` §5.2 (the PIC is one of the
  sources; the trap mechanism itself is in the MMU).
- **Timer / Pending–Repeat contract:** `Alesta LX Hardware System Timer`
  §11.

---

## 7. Status

- **Reference.** Registers, bits, priority, `IN_SERVICE`, `CLAIM`
  latch, and supervisor write protection are as in `lx_sys.sv`.
- **Address** is in `lx_rtl_reference.md`.
- **⚠ Spec:** the old hierarchical description, the 16-bit registers,
  and the `int_ack_i`-driven retirement do not match the RTL. RTL is
  authoritative.

---

*End of document.*
