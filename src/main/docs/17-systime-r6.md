# Alesta LX Hardware System Timer

## Technical Specification for FPGA Implementation

**Revision 6**

---

## 1. Purpose and Scope

This document defines the requirements for the hardware system timer of the Alesta LX platform based on the Z80 CPU and FPGA.

The timer generates timed interrupt requests with 1 µs resolution. It provides software with a hardware source of monotonic time and a mechanism for generating interval requests.

Core functions of the hardware block:

* free-running 16-bit real-time counter `RT`;
* 1 MHz counter resolution;
* absolute target timestamp register `COMPARE`;
* cyclic comparison of current time against the target timestamp;
* interrupt request generation to channel 6 of the PIC;
* coherent access to 16-bit values over the 8-bit Z80 data bus;
* blocking of maskable interrupt (`INT`) delivery while the supervisor writes `COMPARE` (`F4 -> F5`), with a 32 µs hardware timeout;
* hardware privilege enforcement on register writes.

This document describes only the hardware implementation of the timer and its interfaces. Software event queues, schedulers, game handlers, and software interrupt dispatchers are outside the scope of this specification.

## 2. Key Parameters

| Parameter | Value |
| --- | --- |
| `RT` counter width | 16 bits |
| Counter frequency | 1 MHz |
| Time resolution | 1 µs |
| Counting mode | Continuous, modulo 65536 |
| Full wrap-around period | 65.536 ms |
| Maximum unambiguous scheduling horizon | Less than 32.768 ms |
| Compare register width | 16 bits |
| CPU interface | 8-bit Z80 I/O |
| Number of I/O ports | 3 |
| Interrupt controller | External PIC (channel 6 reserved for the timer) |
| `WINDOW` hardware timeout | 32 µs |

The 1 MHz clock enable must be derived from the FPGA reference clock or an appropriate hardware divider.

Real-time accuracy is determined by the reference clock accuracy; the Z80 CPU clock frequency does not define timer resolution.

## 3. Block Architecture

The timer contains the following logical elements:

1. 16-bit free-running counter `RT`.
2. 16-bit target value register `COMPARE`.
3. Two 16-bit `RT_SNAPSHOT` registers for coherent reads of `RT`, one for supervisor mode and one for user mode.
4. Low-byte buffer for writes to `COMPARE`.
5. Write window flip-flop (`WINDOW`) for `F4 -> F5` writes of `COMPARE`.
6. `WINDOW` timeout counter (32 µs).
7. Control and status register.
8. Cyclic comparison logic.
9. Request pulse generation logic for the PIC, with the `FIRED` flag (one request per commit).

The `RT` counter runs independently of timer compare enable state; disabling the timer neither stops nor resets `RT`.

## 4. Real-Time Counter `RT`

`RT` is a free-running 16-bit counter.

On each 1 MHz tick:

`RT = RT + 1`

After `0xFFFF`, the counter wraps around to `0x0000`. The full wrap-around period is 65536 µs.

The counter:

* starts from zero upon release of hardware `RESET`;
* runs continuously;
* does not stop when timer comparison is disabled;
* does not reset when a new target timestamp is written;
* is independent of PIC state and interrupt masks.

`RT` serves as the platform's hardware source of monotonic time.

## 5. Registers and Port Map

Three I/O ports are used to access the timer.

{{auto:timer_regmap}}

Port decoding is performed on the full low address byte `A7–A0`. Upper I/O address bits are ignored. This matches the standard Z80 direct I/O model where the port low byte is specified by the instruction operand and the upper byte comes from the accumulator.

Port read and write side effects execute **once per bus cycle** on a strict single-cycle strobe, not by level while `IORQ#` / `RD#` / `WR#` remain asserted. Holding `cs_i` active for several clocks does not repeat the operation.

Verify that there are no address conflicts with existing platform I/O ports.

### 5.1. Port `F4`

**Read `F4`**

1. Latches the full 16-bit `RT` atomically into the `RT_SNAPSHOT` of the current mode (supervisor or user, from the CPU privilege signal).
2. Returns the low byte of that snapshot.

A read has no other side effect: it does not open `WINDOW`.

> **✎ By design (RTL, Rev 6):** there is one snapshot per mode. A supervisor interrupt handler that reads the time between a user program's `F4` and `F5` changes only the supervisor snapshot, so the user's pair stays coherent. Because reads no longer open `WINDOW`, a user program reading `F4` in a loop cannot hold off `INT`.
>
> **⚠ Spec:** earlier Rev 6 drafts opened `WINDOW` on `F4` reads as well. User code could then block `INT` indefinitely by reading `F4` repeatedly (each read restarted the timeout). **RTL is authoritative.**

Supervisor code that shares the supervisor snapshot with its own interrupt handlers (for example a kernel time routine and the timer ISR) must read `F4 -> F5` with interrupts disabled.

**Write `F4`**

1. Stores the written byte into the temporary low-byte buffer for `COMPARE`.
2. Sets the access window flag `WINDOW = 1` (blocking `INT` delivery).
3. Resets the `WINDOW` timeout counter.
4. Leaves the active `COMPARE` register unchanged.

> **✎ By design (RTL, Rev 6):** `F4` now latches the **entire 16-bit `RT`** into `RT_SNAPSHOT`, not just the high byte into a separate `SHADOW`. This removes the race on the low-byte `0xFF -> 0x00` rollover: both `F4` and `F5` read from the same snapshot, so the two bytes always describe the exact same instant.
>
> **⚠ Spec:** Rev 5 described `F4` latching only the high byte into `SHADOW`. Rev 6 replaces `SHADOW` with the full `RT_SNAPSHOT`. **RTL is authoritative.**

### 5.2. Port `F5`

**Read `F5`**

1. Returns the high byte of the current mode's `RT_SNAPSHOT`.

If `F5` is read without a preceding read of `F4`, the last stored snapshot of that mode is returned; the live `RT` is not substituted. A read of `F5` does not change `WINDOW`.

**Write `F5`**

1. Writes the incoming byte into the upper half of `COMPARE`.
2. Takes the lower half from the temporary buffer populated by the `F4` write.
3. Commits the full 16-bit value atomically.
4. Clears the access window flag (`WINDOW = 0`), unblocking `INT` delivery.
5. Sets timer comparison state to `ARMED = 1`.
6. Enables timer comparison (`ENABLE = 1`).
7. Clears `FIRED` (a new commit may request once more).
8. Performs an immediate comparison check against the newly committed target.

Writing `F5` is the final step of programming a target timestamp.

> **✎ By design (RTL):** `F5` write unconditionally sets `ARMED = 1` and `ENABLE = 1`. A subsequent `F6` write clearing `ENABLE` is not "sticky" against a later `F5` commit: a new commit re-enables the comparator. This is the intended behavior: programming a new target always starts a new armed comparison.

### 5.3. Port `F6` — Control and Status

`F6` combines status reads and control writes.

{{auto:timer_f6_bits}}

Writes to `F6` are permitted only in supervisor mode. Only bit 0 is used on write; all other bits are ignored.

**`ENABLE`**

* `0` — timer comparison is disabled; new timer requests are suppressed;
* `1` — timer comparison is enabled.

Clearing `ENABLE` does not stop `RT` and does not clear `COMPARE`. When re-enabled, comparison resumes against the retained target.

**`ARMED`**

Indicates that a target timestamp has been committed to `COMPARE`. Cleared on hardware `RESET`; set upon completion of an `F5` write.

**`WINDOW`**

Indicates that a `COMPARE` write is in progress (`F4` has been written, `F5` has not yet been written). See §8 for the hardware timeout.

**`FIRED`**

Set when the timer sends its request to the PIC; cleared by the next `F5` commit. While `FIRED = 1`, no further request is generated for the same target, so each commit produces at most one request.

**`DUE`**

Reflects the current logical comparison state. This is a diagnostic status bit, not a pending-interrupt flag. While no target has been configured (`ARMED = 0`), `DUE` is held at `0` (`DUE = ARMED & ~delta[15]`).

`Pending` and `Repeat` states reside exclusively in the PIC.

Upon hardware `RESET`:

* `ENABLE = 0`;
* `ARMED = 0`;
* `WINDOW = 0`;
* `DUE = 0`;
* `FIRED = 0`;
* `COMPARE = 0`;
* both `RT_SNAPSHOT` registers `= 0`.

Thus, immediately after reset, the timer is disabled, `DUE` reads as zero, and no spurious requests are sent to the PIC. The first completed `COMPARE` write via `F4`/`F5` sets `ARMED` and automatically asserts `ENABLE`. Thereafter, software may independently disable and re-enable comparison via `F6`.

## 6. Coherent 16-Bit `RT` Read

Because the Z80 uses an 8-bit data bus, reading the 16-bit `RT` value takes two operations:

1. Read `F4`.
2. Read `F5`.

Reading `F4` latches the **entire 16-bit `RT`** into the current mode's `RT_SNAPSHOT`. Reading `F5` returns the high byte of the same snapshot. Both bytes therefore reflect the exact same instant even if `RT` increments between the two instructions, including across the `0xFF -> 0x00` low-byte rollover.

The access order is mandatory: `F4` first, then `F5`.

## 7. Coherent 16-Bit Target Write

Programming a new target timestamp takes two operations:

1. Write the low byte to `F4`.
2. Write the high byte to `F5`.

The active `COMPARE` value remains unchanged until the second write completes. Writing `F5` atomically commits the full 16-bit target.

Once committed, the comparison condition is evaluated immediately; if already true, a new request pulse must be sent to the PIC regardless of the previous state of `DUE`.

## 8. Interrupt Blocking During Two-Byte Access (`WINDOW`)

The write window prevents the CPU from being interrupted between the two halves of a supervisor `COMPARE` write (`F4 -> F5`).

* `WINDOW` is set to `1` by a supervisor write of port `F4`.
* `WINDOW` is cleared to `0` by a supervisor write of port `F5`, on hardware `RESET`, and by the hardware timeout described below.
* Reads of `F4`/`F5` and user-mode writes do not affect `WINDOW` (reads are made coherent by the per-mode snapshots instead, §5.1).

While `WINDOW = 1`:

* the timer's block output prevents delivery to the CPU of **maskable interrupts (`INT` via the PIC)**;
* **`NMI` delivery is NOT blocked by `WINDOW`**;
* incoming requests from interrupt sources are not lost and remain latched in their respective controllers (the PIC continues to track `Pending` and `Repeat`);
* `RT` and the comparison logic continue operating normally.

### 8.1. Hardware timeout

**✎ By design (RTL, Rev 6):** a 32 µs hardware timeout auto-clears `WINDOW`. If software opens the window (via `F4`) and never completes it (via `F5`), the timeout releases `INT` delivery. Normal `F4 -> F5` sequences complete in a few microseconds and are unaffected. Each supervisor `F4` write resets the timeout counter.

> **⚠ Spec:** Rev 5 explicitly said "No hardware window timeout is implemented; software is responsible". Rev 6 adds the timeout to prevent a forgotten window from blocking `INT` forever. **RTL is authoritative.**

### 8.2. NMI is not blocked

**⚠ Spec:** Rev 5 stated that `WINDOW` blocks **both** `INT` and `NMI`. Rev 6 changes this: `WINDOW` blocks only maskable `INT`. `NMI` is **not** gated by `WINDOW`. Rationale: `NMI` must not depend on whether a program has forgotten to close a two-byte access window. **RTL is authoritative.**

## 9. Cyclic Comparison Algorithm

Comparison is performed modulo 65536 by interpreting the difference as a signed 16-bit integer.

Definitions:

* `C` — current `RT` value;
* `T` — target `COMPARE` value.

Difference:

`D = (C - T) mod 65536`

Target reached condition (when `ARMED = 1`):

`DUE = ARMED & (D[15] == 0)`

Reference Verilog implementation:

```verilog
wire [15:0] delta = rt_counter - compare_reg;
wire timer_due = armed_reg & (~delta[15]);
```

### 9.1. Scheduling Horizon Constraint

A target must be scheduled strictly less than 32768 ticks (32.768 ms) in the future:

`0 <= (T - C) mod 65536 < 32768`

A delta of exactly 32768 ticks is ambiguous and must not be used.

### 9.2. Examples

| `RT` (`C`) | `COMPARE` (`T`) | `ARMED` | `DUE` |
| --- | --- | --- | --- |
| 0 | 0 | 0 | 0 |
| 1000 | 2000 | 1 | 0 |
| 2000 | 2000 | 1 | 1 |
| 3000 | 2000 | 1 | 1 |
| 65530 | 5 | 1 | 0 |
| 5 | 65530 | 1 | 1 |

This algorithm handles `RT` wrap-around across `0xFFFF` seamlessly. Plain unsigned comparison (`counter >= compare`) must never be used.

## 10. Request Generation to the PIC

The timer sends interrupt requests to channel **6** of the external PIC. The electrical interface is a short request pulse (a single-cycle strobe synchronous with the block's system clock). The PIC latches the request and manages `Pending` and `Repeat` states independently; the timer contains no internal `Pending` or `Repeat` registers.

**✎ By design (RTL):** the timer request is routed to PIC channel 6. The external `irq_i[6]` input on the PIC is ignored; line 6 is reserved for the timer.

### 10.1. Request Generation Conditions

A request pulse is generated under the following conditions:

1. `DUE` transitions from `0` to `1` while `ENABLE = 1`, `ARMED = 1` and `FIRED = 0`.
2. A new target write completes via `F5` and the resulting `DUE` condition is already `1`.
3. Software sets `ENABLE = 1` (via `F6` write) while `ARMED = 1`, `DUE` is already `1` and `FIRED = 0`.

Each pulse sets `FIRED`. Condition 2 applies unconditionally regardless of the prior state of `DUE` (the commit clears `FIRED` first). No repeated request pulses are generated on subsequent clock cycles while `DUE` remains `1`.

### 10.2. Behavior with an Unchanged Target

If `COMPARE` is not updated, `DUE`:

* becomes `1` when `RT` reaches `COMPARE`;
* remains `1` for half a counter revolution;
* becomes `0` once the signed difference crosses the `0x8000` boundary;
* becomes `1` again after a full counter revolution (65.536 ms later).

The second rise of `DUE` does **not** generate a request: `FIRED` is still `1` from the first one. A one-shot target therefore requests exactly once. A periodic tick must commit a new target (for example in its handler); software that keeps time from `RT` must read it at least once per 65.536 ms revolution.

> **⚠ Spec:** without `FIRED`, the request was repeated on every revolution (65.5 ms, 131 ms...) until software wrote a new target or disabled the timer. **RTL is authoritative.**

### 10.3. `ENABLE`

When `ENABLE = 0`, no new request pulses are sent to the PIC. `RT` continues counting, `COMPARE` and `ARMED` retain their values, and the `DUE` bit in status register `F6` continues to reflect the live comparator output.

## 11. PIC Interface Contract

For each interrupt source, the PIC must implement at least two states:

* `Pending` — the source has requested an interrupt that has not yet been fully serviced;
* `Repeat` — the same source generated another request while `Pending` was still asserted (a boolean flag indicating one or more missed/queued occurrences, not an event counter).

Required semantics:

1. On a new request, if `Pending = 0`, set `Pending = 1`.
2. On a new request, if `Pending = 1`, set `Repeat = 1`.
3. On service acknowledge (PIC `CLAIM`), clear `Pending` and `Repeat`; `CLAIM` returns `Repeat` (bit 6) so that the handler knows that one or more requests were missed.
4. A request that arrives after `CLAIM` (while the channel is in service) sets `Pending` again and is delivered after `COMPLETE`.

> **⚠ Spec:** an earlier text kept `Pending = 1` on `CLAIM` when `Repeat = 1`. The PIC v2 RTL clears both and reports `Repeat` in the `CLAIM` value. **RTL is authoritative.**

Simultaneous acknowledge and new request arrival must be set-dominant so that a new request is never lost.

Interrupt masking is handled in the PIC. Masking the timer blocks delivery to the CPU without clearing `Pending` or `Repeat`.

## 12. Access Privileges

Writes to timer registers (`F4`, `F5`, `F6`) are permitted exclusively in supervisor mode. Reads are permitted in both supervisor and user modes; each mode reads its own `RT_SNAPSHOT`, and reads have no effect on `WINDOW`.

Privilege checks are enforced in hardware. Any write attempt from user mode is rejected with **zero side effects** — leaving all internal registers and `WINDOW` state untouched (a user-mode `F4` write does **not** open `WINDOW`).

The platform's general protection mechanism defines how illegal write attempts are handled.

## 13. Platform Frame Synchronization

System timer `RT` is not a frame counter and does not depend on the video subsystem clock.

The platform distinguishes:

* `VFC` — Video Frame Counter (number of hardware video frame events);
* `GFC` — Game Frame Counter (number of game frames actually processed).

Video frame interrupts must not be lost. If the game has not prepared a new frame, the video hardware may redisplay the previous frame (`VFC` increments while `GFC` and game time do not). Game counters `PT` and `FT` belong to software and are outside this hardware block.

## 14. Guarantees and Limitations

The hardware block guarantees:

* continuous `RT` operation at 1 µs resolution with clean wrap-around at `0xFFFF`;
* coherent 16-bit reads of `RT` (both bytes from the same `RT_SNAPSHOT`, one per mode);
* atomic 16-bit commits of `COMPARE`;
* zero spurious triggers after `RESET` prior to first target configuration (`ARMED = 0`);
* modulo-65536 cyclic comparison;
* request pulse generation on `DUE` rising edge, on committing an already-due target via `F5`, and on re-enabling `ENABLE` while `DUE = 1`, at most once per commit (`FIRED`);
* blocking of **maskable `INT`** delivery while `WINDOW = 1` (supervisor `F4 -> F5` writes), with a 32 µs hardware timeout;
* `NMI` is not gated by `WINDOW`;
* hardware enforcement of supervisor-only write privileges, with zero side effects on rejected writes.

The hardware block does not guarantee:

* exact Z80 interrupt response latency or ISR entry delay;
* absence of delays caused by higher-priority or concurrent interrupt sources;
* absolute time accuracy beyond the reference oscillator's tolerance;
* scheduling horizons of 32768 µs or greater.

## 15. FPGA Implementation Requirements

The FPGA engineer must implement:

1. A standalone free-running 16-bit `RT` counter driven by a 1 MHz tick enable.
2. `COMPARE`, two `RT_SNAPSHOT` registers (supervisor and user), and the low-byte write buffer.
3. Write window flip-flop `WINDOW` (set on a supervisor `F4` write, cleared on a supervisor `F5` write, `RESET`, and hardware timeout), driving the `INT` delivery block signal only (`NMI` is not gated).
4. `WINDOW` timeout counter (32 µs, reset on each supervisor `F4` write).
5. Hardware write privilege gating based on the CPU privilege mode signal, with zero side effects on rejected writes.
6. Status/control register `F6` with the specified bit layout.
7. Signed-difference cyclic comparator gated by `ARMED`.
8. Request pulse generator triggering on `DUE` rising edge, on `F5` commit with `DUE = 1`, and on `ENABLE` assertion with `DUE = 1`, gated by `FIRED` (set by each pulse, cleared by `F5`), routed to PIC channel 6.
9. Complete independence of `RT` and internal comparison logic from PIC interrupt masks.

## 16. Verification and Test Plan

Before integrating the block into the platform, verify the following:

* **`RT` counter:** 1 MHz increment rate, `0xFFFF -> 0x0000` wrap-around, continuous counting when `ENABLE = 0`, independence from `COMPARE` writes.
* **`RT` read:** `F4 -> F5` sequence across a low-byte `0xFF -> 0x00` rollover, reading `F5` without a preceding `F4`, both bytes from the same `RT_SNAPSHOT`, separate supervisor and user snapshots, no effect of reads on `WINDOW`.
* **`COMPARE` write:** atomic commit on `F5`, no change to active `COMPARE` after `F4`, automatic assertion of `ARMED = 1` and `ENABLE = 1` on first `F5` write, immediate request pulse when committing an already-due target.
* **Reset state:** verify `ENABLE = 0`, `ARMED = 0`, `WINDOW = 0`, `DUE = 0`, and zero spurious requests after `RESET`.
* **Cyclic comparison:** `C < T`, `C == T`, `C > T`, `RT` wrap-around across `0xFFFF`, `0x8000` boundary crossing, and **no** new request after a full 65.536 ms revolution (`FIRED`).
* **`ENABLE` and `F6`:** status bit reads, disabling `ENABLE = 0` while preserving `RT` and `COMPARE`, immediate request pulse on re-enabling `ENABLE = 1` while `DUE = 1`, and ignoring reserved bits.
* **Write window (`WINDOW`):** asserted on a supervisor `F4` write, cleared on a supervisor `F5` write, cleared by 32 µs hardware timeout, not affected by reads, holding off `INT` (but **not** `NMI`) while `WINDOW = 1` without losing latched requests in the controllers.
* **Privileges:** writes accepted in supervisor mode, writes completely ignored in user mode (including no effect on `WINDOW`), reads permitted in both modes.
* **PIC contract:** `Pending` and `Repeat` assertion, `CLAIM` with `Repeat = 1` and `Repeat = 0`, simultaneous request and `CLAIM` (set-dominant), and masking without losing `Pending`/`Repeat`.
* **Bus contract:** single-cycle strobe, one operation per `cs_i` assertion, `dat_o` stable while `ack_o` is asserted.

## 17. Summary Functional Model

The Alesta LX hardware system timer is an independent 1 µs monotonic time source paired with a single 16-bit absolute compare register.

Programming requires two sequential writes (`F4 -> F5`), and reading time requires two sequential reads (`F4 -> F5`) from the caller's own snapshot. Between the two writes, the `WINDOW` flag holds off maskable `INT` delivery cleanly; a 32 µs hardware timeout prevents a forgotten window from blocking `INT` forever. `NMI` is not gated by `WINDOW`. Port `F6` controls comparison enable and exposes block status.

All write operations are protected by hardware supervisor privilege checks, while interrupt masking and repeat tracking are handled by the external PIC.

*End of document.*

