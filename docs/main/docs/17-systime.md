# Alesta LX Hardware System Timer

## Technical Specification for FPGA Implementation

**Revision 5**

---

## 1. Purpose and Scope

This document defines the requirements for the hardware system timer of the Alesta LX platform based on the Z80 CPU and FPGA.

The timer generates timed interrupt requests with 1 µs resolution. It provides software with a hardware source of monotonic time and a mechanism for generating interval requests.

Core functions of the hardware block:

* free-running 16-bit real-time counter `RT`;


* 1 MHz counter resolution;


* absolute target timestamp register `COMPARE`;


* cyclic comparison of current time against the target timestamp;


* interrupt request generation to the Programmable Interrupt Controller (PIC);


* coherent access to 16-bit values over the 8-bit Z80 data bus;


* blocking of maskable (`INT`) and non-maskable (`NMI`) interrupt delivery during two-byte access sequences (`F4 -> F5`);


* hardware privilege enforcement on register writes.



This document describes only the hardware implementation of the timer and its interfaces. Software event queues, schedulers, game handlers, and software interrupt dispatchers are outside the scope of this specification.

## 2. Key Parameters

| Parameter | Value |
| --- | --- |
| `RT` counter width | 16 bits  |
| Counter frequency | 1 MHz  |
| Time resolution | 1 µs |
| Counting mode | Continuous, modulo 65536  |
| Full wrap-around period | 65.536 ms  |
| Maximum unambiguous scheduling horizon | Less than 32.768 ms |
| Compare register width | 16 bits |
| CPU interface | 8-bit Z80 I/O |
| Number of I/O ports | 3 |
| Interrupt controller | External platform PIC and NMI controller |

The 1 MHz clock enable must be derived from the FPGA reference clock or an appropriate hardware divider.

Real-time accuracy is determined by the reference clock accuracy; the Z80 CPU clock frequency does not define timer resolution.

## 3. Block Architecture

The timer contains the following logical elements:

1. 16-bit free-running counter `RT`.
2. 16-bit target value register `COMPARE`.
3. Shadow register `SHADOW` for coherent reads of `RT`.
4. Low-byte buffer for writes to `COMPARE`.
5. Sequential access window flip-flop (`WINDOW`) for `F4 -> F5` transactions.
6. Control and status register.
7. Cyclic comparison logic.
8. Request pulse generation logic for the PIC.

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
* is independent of PIC state, NMI controller state, and interrupt masks.

`RT` serves as the platform's hardware source of monotonic time.

## 5. Registers and Port Map

Three I/O ports are used to access the timer.

| Port | Read | Write |
| --- | --- | --- |
| `F4` | Low byte of `RT`  | Buffer low byte of `COMPARE` |
| `F5` | High byte of `SHADOW` (`RT`) | Commit high byte of `COMPARE`  |
| `F6` | Status register | Control register  |

Port decoding is performed on the lower address lines `A7–A0`; upper I/O address bits are ignored. This matches the standard Z80 direct I/O model where the port low byte is specified by the instruction operand and the upper byte comes from the accumulator.

Port read and write side effects must execute once per bus cycle on a strict Z80 bus-cycle strobe rather than by level while `IORQ#` / `RD#` / `WR#` remain asserted.

Verify that there are no address conflicts with existing platform I/O ports.

### 5.1. Port `F4`

**Read `F4**`

1. Latches the low byte of `RT` at the moment of the read.
2. Copies the corresponding high byte of `RT` into `SHADOW`.
3. Sets the access window flag `WINDOW = 1` (blocking `INT` and `NMI` delivery).
4. Returns the latched low byte of `RT`. **Write `F4**`

1. Stores the written byte into the temporary low-byte buffer for `COMPARE`.
2. Sets the access window flag `WINDOW = 1` (blocking `INT` and `NMI` delivery).
3. Leaves the active `COMPARE` register unchanged.

### 5.2. Port `F5`

**Read `F5**`

1. Returns the contents of `SHADOW`.
2. Clears the access window flag (`WINDOW = 0`), unblocking `INT` and `NMI` delivery.

If `F5` is read without a preceding read of `F4`, the last stored contents of `SHADOW` are returned; the live high byte of `RT` is not substituted.

**Write `F5**`

1. Writes the incoming byte into the upper half of `COMPARE`.
2. Takes the lower half from the temporary buffer populated by the `F4` write.
3. Commits the full 16-bit value atomically.
4. Clears the access window flag (`WINDOW = 0`), unblocking `INT` and `NMI` delivery.
5. Sets timer comparison state to `ARMED = 1`.
6. Enables timer comparison (`ENABLE = 1`).
7. Performs an immediate comparison check against the newly committed target.

Writing `F5` is the final step of programming a target timestamp.

### 5.3. Port `F6` — Control and Status

`F6` combines status reads and control writes.

Register bit layout:

| Bit | Read | Write |
| --- | --- | --- |
| 0 | `ENABLE` — timer comparison enabled  | `ENABLE` — enable/disable comparison |
| 1 | `ARMED` — target timestamp has been set  | Unused |
| 2 | `WINDOW` — sequential access window is open | Unused |
| 3 | `DUE` — current comparison condition is true | Unused |
| 4–7 | Reserved, read as `0` | Ignored |

Writes to `F6` are permitted only in supervisor mode. Only bit 0 is used on write; all other bits are ignored.

**`ENABLE`**

* `0` — timer comparison is disabled; new timer requests are suppressed;
* `1` — timer comparison is enabled.

Clearing `ENABLE` does not stop `RT` and does not clear `COMPARE`. When re-enabled, comparison resumes against the retained target.

**`ARMED`**

Indicates that a target timestamp has been committed to `COMPARE`. Cleared on hardware `RESET`; set upon completion of an `F5` write.

**`WINDOW`**

Indicates that a two-byte sequential access window is open (`F4` has been accessed, `F5` has not yet completed).

**`DUE`**

Reflects the current logical comparison state. This is a diagnostic status bit, not a pending-interrupt flag. While no target has been configured (`ARMED = 0`), `DUE` is held at `0` (`DUE = ARMED & ~delta[15]`).

`Pending` and `Repeat` states reside exclusively in the PIC.

Upon hardware `RESET`:

* `ENABLE = 0`;
* `ARMED = 0`;
* `WINDOW = 0`;
* `DUE = 0`;
* `COMPARE = 0`;
* `SHADOW = 0`.


Thus, immediately after reset, the timer is disabled, `DUE` reads as zero, and no spurious requests are sent to the PIC. The first completed `COMPARE` write via `F4`/`F5` sets `ARMED` and automatically asserts `ENABLE`. Thereafter, software may independently disable and re-enable comparison via `F6`.

## 6. Coherent 16-Bit `RT` Read

Because the Z80 uses an 8-bit data bus, reading the 16-bit `RT` value takes two operations:

1. Read `F4`.


2. Read `F5`.



Reading `F4` latches the low byte and simultaneously copies the matching high byte into `SHADOW`. Reading `F5` returns that stored high byte. Both bytes therefore reflect the exact same instant even if `RT` increments between the two instructions.

The access order is mandatory: `F4` first, then `F5`.

## 7. Coherent 16-Bit Target Write

Programming a new target timestamp takes two operations:

1. Write the low byte to `F4`.


2. Write the high byte to `F5`.



The active `COMPARE` value remains unchanged until the second write completes. Writing `F5` atomically commits the full 16-bit target.

Once committed, the comparison condition is evaluated immediately; if already true, a new request pulse must be sent to the PIC regardless of the previous state of `DUE`.

## 8. Interrupt Blocking During Two-Byte Access (`WINDOW`)

The access window prevents the CPU from being interrupted between the two halves of a sequential read or write (`F4 -> F5`).

* `WINDOW` is set to `1` on any read or write of port `F4`.


* `WINDOW` is cleared to `0` on any read or write of port `F5`, as well as on hardware `RESET`.



While `WINDOW = 1`:

* the timer's block output prevents delivery to the CPU of **both maskable interrupts (`INT` via the PIC) and non-maskable interrupts (`NMI` via the NMI controller)**;


* incoming requests from interrupt sources are not lost and remain latched in their respective controllers (the PIC continues to track `Pending` and `Repeat`);


* `RT` and the comparison logic continue operating normally.



No hardware window timeout (such as a CPU/M1 cycle counter) is implemented; software is responsible for completing the paired `F4 -> F5` sequence normally.

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

The timer sends interrupt requests to the external PIC.

The electrical interface is a short request pulse (a single-cycle strobe synchronous with the block's system clock). The PIC latches the request and manages `Pending` and `Repeat` states independently; the timer contains no internal `Pending` or `Repeat` registers.

### 10.1. Request Generation Conditions

A request pulse is generated under the following conditions:

1. `DUE` transitions from `0` to `1` while `ENABLE = 1` and `ARMED = 1`.
2. A new target write completes via `F5` and the resulting `DUE` condition is already `1`.
3. Software sets `ENABLE = 1` (via `F6` write) while `ARMED = 1` and `DUE` is already `1`.

Condition 2 applies unconditionally regardless of the prior state of `DUE`. No repeated request pulses are generated on subsequent clock cycles while `DUE` remains `1`.

### 10.2. Behavior with an Unchanged Target

If `COMPARE` is not updated, `DUE`:

* becomes `1` when `RT` reaches `COMPARE`;
* remains `1` for half a counter revolution;
* becomes `0` once the signed difference crosses the `0x8000` boundary;
* becomes `1` again after a full counter revolution (65.536 ms later).

### 10.3. `ENABLE`

When `ENABLE = 0`, no new request pulses are sent to the PIC. `RT` continues counting, `COMPARE` and `ARMED` retain their values, and the `DUE` bit in status register `F6` continues to reflect the live comparator output.

## 11. PIC Interface Contract

For each interrupt source, the PIC must implement at least two states:

* `Pending` — the source has requested an interrupt that has not yet been fully serviced;
* `Repeat` — the same source generated another request while `Pending` was still asserted (a boolean flag indicating one or more missed/queued occurrences, not an event counter).

Required semantics:

1. On a new request, if `Pending = 0`, set `Pending = 1`.
2. On a new request, if `Pending = 1`, set `Repeat = 1`.
3. On service acknowledge, if `Repeat = 1`, keep `Pending = 1` and clear `Repeat = 0`.
4. On service acknowledge, if `Repeat = 0`, clear `Pending = 0`.

Simultaneous acknowledge and new request arrival must be set-dominant so that a new request is never lost.

Interrupt masking is handled in the PIC. Masking the timer blocks delivery to the CPU without clearing `Pending` or `Repeat`.

## 12. Access Privileges

Writes to timer registers (`F4`, `F5`, `F6`) are permitted exclusively in supervisor mode. Reads are permitted in both supervisor and user modes.

Privilege checks must be enforced in hardware. Any write attempt from user mode must be rejected with zero side effects—leaving all internal registers and `WINDOW` state untouched.

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


* coherent 16-bit reads of `RT`;


* atomic 16-bit commits of `COMPARE`;


* zero spurious triggers after `RESET` prior to first target configuration (`ARMED = 0`);
* modulo-65536 cyclic comparison;


* request pulse generation on `DUE` rising edge, on committing an already-due target via `F5`, and on re-enabling `ENABLE` while `DUE = 1`;


* blocking of both `INT` and `NMI` delivery while `WINDOW = 1` (`F4 -> F5`);


* hardware enforcement of supervisor-only write privileges.



The hardware block does not guarantee:

* exact Z80 interrupt response latency or ISR entry delay;


* absence of delays caused by higher-priority or concurrent interrupt sources;


* absolute time accuracy beyond the reference oscillator's tolerance;


* scheduling horizons of 32768 µs or greater.



## 15. FPGA Implementation Requirements

The FPGA engineer must implement:

1. A standalone free-running 16-bit `RT` counter driven by a 1 MHz tick enable.


2. `COMPARE`, `SHADOW`, and low-byte write buffer registers.


3. Access window flip-flop `WINDOW` (set on `F4` read/write, cleared on `F5` read/write and `RESET`), driving the `INT` and `NMI` delivery block signal.


4. Hardware write privilege gating based on the CPU privilege mode signal.


5. Status/control register `F6` with the specified bit layout.


6. Signed-difference cyclic comparator gated by `ARMED`.


7. Request pulse generator triggering on `DUE` rising edge, on `F5` commit with `DUE = 1`, and on `ENABLE` assertion with `DUE = 1`.


8. Complete independence of `RT` and internal comparison logic from PIC interrupt masks.



## 16. Verification and Test Plan

Before integrating the block into the platform, verify the following:

* **`RT` counter:** 1 MHz increment rate, `0xFFFF -> 0x0000` wrap-around, continuous counting when `ENABLE = 0`, independence from `COMPARE` writes.


* **`RT` read:** `F4 -> F5` sequence across a low-byte `0xFF -> 0x00` rollover, reading `F5` without a preceding `F4`, clearing `WINDOW` upon `F5` read.


* **`COMPARE` write:** atomic commit on `F5`, no change to active `COMPARE` after `F4`, automatic assertion of `ARMED = 1` and `ENABLE = 1` on first `F5` write, immediate request pulse when committing an already-due target.


* **Reset state:** verify `ENABLE = 0`, `ARMED = 0`, `WINDOW = 0`, `DUE = 0`, and zero spurious requests after `RESET`.


* **Cyclic comparison:** `C < T`, `C == T`, `C > T`, `RT` wrap-around across `0xFFFF`, `0x8000` boundary crossing, and re-triggering after a full 65.536 ms revolution.


* **`ENABLE` and `F6`:** status bit reads, disabling `ENABLE = 0` while preserving `RT` and `COMPARE`, immediate request pulse on re-enabling `ENABLE = 1` while `DUE = 1`, and ignoring reserved bits.


* **Access window (`WINDOW`):** asserted on `F4` read/write, cleared on `F5` read/write, holding off both `INT` and `NMI` delivery while `WINDOW = 1` without losing latched requests in the controllers.


* **Privileges:** writes accepted in supervisor mode, writes completely ignored in user mode (including no effect on `WINDOW`), reads permitted in both modes.


* **PIC contract:** `Pending` and `Repeat` assertion, acknowledge behavior with `Repeat = 1` and `Repeat = 0`, simultaneous request and acknowledge (set-dominant), and masking without losing `Pending`/`Repeat`.



## 17. Summary Functional Model

The Alesta LX hardware system timer is an independent 1 µs monotonic time source paired with a single 16-bit absolute compare register.

Programming requires two sequential writes (`F4 -> F5`), and reading time requires two sequential reads (`F4 -> F5`). Between `F4` and `F5`, the `WINDOW` flag holds off `INT` and `NMI` delivery cleanly without hardware cycle timeouts. Port `F6` controls comparison enable and exposes block status.

All write operations are protected by hardware supervisor privilege checks, while interrupt masking and repeat tracking are handled by the external PIC.

*End of document.*