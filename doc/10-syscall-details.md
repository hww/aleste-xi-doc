# Aleste LX: Interrupts, Syscalls, Drivers, and Takeover Mode

**Consolidated document of accepted decisions, system architecture, and
rationale**

|         |                                                                                              |
|:--------|:---------------------------------------------------------------------------------------------|
| Date    | 2026-11-07                                                                                   |
| Basis   | Discussion of the IPC/syscall/asynchrony article; `aleste-lx_spec_rev2.md` specification     |
| Purpose | Record the decisions, explain how the system works, and document why these choices were made |

------------------------------------------------------------------------

## 0. How to read this document

**Status labels**

- **\[ACCEPTED\]** — a decision explicitly made by the user during the
  discussion.
- **\[RECOMMENDATION\]** — a proposal derived from accepted decisions or
  intended to close a gap; it requires confirmation.
- **\[OPEN\]** — a question that has not yet been answered.

**Terminology.** In the discussion, the word “page” referred to a 16 KB
region of the Z80 address space. This document calls it a **window**
(W0–W3, as in the specification): W0 = `0000–3FFF`, W1 = `4000–7FFF`, W2
= `8000–BFFF`, W3 = `C000–FFFF`. A **slot set** is a set of four bank
registers, one per window. Supervisor has its own set (`SUPER_SLOT`),
and User has its own set (`USER_SLOT`).

**Timing estimates** in T-states are approximate. They must be measured
on a real implementation.

------------------------------------------------------------------------

## 1. Decision summary

| No. | Decision                                                                                                                                                                                           | Status         |
|----:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------|
|   1 | Every interrupt causes a hardware transition to Supervisor and activates `SUPER_SLOT`.                                                                                                             | ACCEPTED       |
|   2 | Interrupt service routines (ISRs) reside alongside the kernel, in W0 of the Supervisor map.                                                                                                        | ACCEPTED       |
|   3 | No hardware IPC mailbox is required.                                                                                                                                                               | ACCEPTED       |
|   4 | There is exactly one syscall mechanism: the `RST 6` instruction (`0030h`). It can be disabled with the `rst6_hook` bit.                                                                            | ACCEPTED       |
|   5 | There is no `OUT (F2h),A` alias. `F2h` has been removed because it introduces a more complicated protocol with different behaviour.                                                                | ACCEPTED       |
|   6 | Supervisor memory layout: W0 contains the kernel and ISRs; W1 and W2 provide 32 KB of working memory; W3 contains the driver entry table and driver environment.                                   | ACCEPTED       |
|   7 | W0 is permanent and is not virtualized. It always maps the same physical system bank in Supervisor.                                                                                                | ACCEPTED       |
|   8 | W3 is the virtualized Supervisor window. It can contain driver entry tables, driver implementations, driver data, and specialized privileged or high-performance code.                             | ACCEPTED       |
|   9 | The Supervisor driver table contains direct jumps (`JP`) to driver methods.                                                                                                                        | ACCEPTED       |
|  10 | The same table in User contains fixed stubs with no logic: `LD A,n / RST 6 / RET`. A User-side driver implementation in W3 is unnecessary.                                                         | ACCEPTED       |
|  11 | The stubs exist for one reason: to allow the same application binary to enter Supervisor takeover mode without recompilation.                                                                      | ACCEPTED       |
|  12 | In takeover mode, the application uses W1/W2, drivers are called directly through W3, and the kernel remains in W0.                                                                                | ACCEPTED       |
|  13 | The application may request W3 environment changes, but only the kernel performs the actual bank switch, and only at a safe point.                                                                 | ACCEPTED       |
|  14 | Syscalls are not inherently “heavy processes”; they are the cost of safety and convenience.                                                                                                        | ACCEPTED       |
|  15 | Leaving Supervisor is tied to `RETN`, not to “the next M1”.                                                                                                                                        | RECOMMENDATION |
|  16 | Use IM1 and read the interrupt source from the PIC, rather than IM2.                                                                                                                               | RECOMMENDATION |
|  17 | Deferred ISR work is communicated through an event mask in kernel RAM.                                                                                                                             | RECOMMENDATION |
|  18 | Asynchronous completion is communicated through a request control block (RCB) in a shared memory region.                                                                                           | RECOMMENDATION |
|  19 | Hardware should expose read-only status indicating entry from User and the interrupt-enable state captured at the trap. The exact semantics of the latter must follow the Z80 interrupt mechanism. | RECOMMENDATION |
|  20 | Use one numbering scheme for syscall functions and driver-table entries.                                                                                                                           | RECOMMENDATION |
|  21 | `rst6_hook` is a separate bit from `supervisor_hook`.                                                                                                                                              | RECOMMENDATION |
|  22 | If `RST 6` is disabled (`rst6_hook = 0`), syscalls are unavailable. This is an intentional restriction for an isolated Legacy environment.                                                         | ACCEPTED       |

------------------------------------------------------------------------

## 2. Initial constraints

The decisions are based on several properties of the platform.

1.  **The Z80 has no privilege levels.** Supervisor mode is implemented
    by Aleste LX hardware, not by the CPU. Entry into the kernel must
    therefore be initiated by hardware, using a trap on an instruction
    fetch from a designated address.

2.  **INT is accepted only between instructions.** A single instruction
    is atomic with respect to an ISR. This is the basis for simple
    coordination between an ISR and the kernel.

3.  **`DI` masks only INT.** `RST n` and NMI are not affected by `DI`.
    `RST 6` is suitable for syscalls precisely because it is
    unconditional.

4.  **The MSX2-style mapper uses 16 KB windows** and has no access
    attributes such as read-only or no-execute. Protection is therefore
    based on privilege transitions and on controlling who can write the
    bank registers, rather than on per-memory access permissions.

5.  **Slot sets are inexpensive.** Changing the User map requires four
    port writes; switching tasks can be as little as one write to
    `USER_SLOT`. The main cost of task switching is register
    preservation, not mapper programming.

6.  **One kernel, one execution stream.** Conventional multitasking is
    limited. “Protection” means protection against mistakes and
    unintended damage, not protection against a malicious program (see
    §10).

------------------------------------------------------------------------

## 3. Supervisor memory layout

The revised layout is:

``` text
Z80 address   Window   Supervisor (SUPER_SLOT)                 User (USER_SLOT)
0000-3FFF     W0       Permanent kernel, vectors, ISRs,         Application's own
                       system stack and mutable kernel data    address space
4000-7FFF     W1       Working memory                           Application
8000-BFFF     W2       Working memory                           Application
C000-FFFF     W3       Virtualized driver environment,          Fixed syscall stubs
                       entry table, driver code and data        (no driver body required)
```

W1 and W2 provide 32 KB of simultaneously available working memory. This
is important for operations that need both a source and a destination
region mapped at once, such as memory copies, as well as graphics and
sound buffers.

### 3.1 Why this layout

- **W0 — kernel and ISRs.** The vectors `0030h` (`RST 6`), `0038h`
  (INT), and `0066h` (NMI) are located here. The kernel, interrupt
  handlers, system stack, syscall dispatcher, and mutable kernel state
  also reside here. W0 is always the same physical bank in Supervisor.
  There is no situation in which an interrupt arrives while the kernel
  code is absent.

- **W1 and W2 — working windows.** These two windows provide 32 KB for
  data and code that needs to be simultaneously accessible: graphics,
  sound, buffers, decompression, source and destination regions, and
  application data. The kernel does not impose a fixed interpretation on
  their contents.

- **W3 — driver environment.** A driver consists of its implementation
  and an entry table. In Supervisor, the table jumps directly to the
  implementation, which resides in the same W3 environment; a call
  therefore does not require a bank switch. Different W3 banks may
  provide different driver sets or specialized execution environments.

- **W3 in User — stubs only.** The User version does not need driver
  implementations. Safe memory operations belong in application
  libraries; privileged operations go through syscalls. At each public
  entry address, User has a fixed stub `LD A,n / RST 6 / RET`. It is not
  a “smart trampoline”; it simply invokes the syscall interface at a
  stable address.

### 3.2 W3 virtualization — \[ACCEPTED\]

W3 is the virtualized Supervisor environment. The physical bank selected
for W3 may change while W0 remains fixed.

A W3 environment may contain:

- the public driver entry table;
- driver implementations;
- driver-specific data and state, where appropriate;
- specialized privileged modules;
- high-performance application code that is intended to execute in
  Supervisor;
- alternative driver or runtime environments.

**Required compatibility conditions \[RECOMMENDATION\]:**

1.  **The public entry table has a stable address and ABI.** Every W3
    variant intended to be interchangeable must expose the same public
    entry addresses and compatible calling conventions. Method
    implementations and their private internal addresses may differ.

2.  **Only the kernel switches W3.** An application may request a
    different W3 environment, but it must not perform the actual
    bank-register update itself. The kernel validates and carries out
    the request.

3.  **Switching occurs only at a safe point.** The kernel must not
    replace W3 while code in the current W3 bank is executing, while an
    active stack is located in that bank, or while an outstanding
    operation still refers to its data or code. The switch routine
    itself resides in W0.

4.  **The active W3 environment must remain available for the lifetime
    of its operations.** An asynchronous driver operation must not be
    left dependent on code or state that is replaced prematurely. Its
    completion path must either use resident W0 code, retain the
    relevant W3 environment until completion, or otherwise be arranged
    so that it no longer depends on the old bank before the switch.

5.  **Stacks should not normally reside in a replaceable W3 bank.** The
    kernel/system stack is in permanent W0. Application stacks should
    use stable memory, normally W1/W2 or another region that is not
    being switched. A W3-resident stack is possible only if the kernel
    guarantees that W3 cannot be switched while that stack is active.

6.  **Mutable kernel data remains in W0.** Unlike the former
    W0-virtualization proposal, kernel variables do not need to be
    duplicated or moved to common memory. The event mask, saved stack
    pointers, ISR state, and other mutable kernel data can remain in
    permanent W0.

The cost of W3 virtualization is the need to define safe switching
points and to keep the public ABI stable. It does not require identical
kernel copies or synchronized kernel updates across physical banks.

------------------------------------------------------------------------

## 4. Interrupts

### 4.1 How interrupt entry works — \[ACCEPTED\]

1.  An INT or NMI is accepted by the Z80. The CPU pushes the return
    address onto the stack using the current User `SP`, while the User
    memory map is still active.

2.  The CPU begins fetching the vector at `0038h` (or `0066h` for NMI).
    When the hardware detects the vector fetch, with `supervisor_hook`
    enabled, it switches to Supervisor and activates `SUPER_SLOT` as
    part of that vector-fetch M1 cycle. The vector is therefore fetched
    from W0 of the kernel map.

3.  Kernel code and the ISR now execute in Supervisor. The ISR code is
    in permanent W0 and is always visible.

4.  The handler saves the User stack pointer, switches to the kernel’s
    own stack in W0, performs its work, restores the original stack
    pointer, and returns using `RETN`. The hardware recognizes the
    `RETN` instruction and switches back to `USER_SLOT` before the
    return address is read from the stack.

The hardware transition is tied to the vector fetch itself. No software
instruction at the vector address is required to cause the switch.

**Why not use a “slot 3” convention?** If the separation were only a
software convention, every ISR would have to determine which map was
active and save and restore it. Hardware selection of a separate
Supervisor slot set avoids that bookkeeping: User has its own map,
Supervisor has its own map, and the transition changes the active set
without modifying either one.

**If an interrupt arrives while Supervisor is already active** (inside
the kernel or another ISR), there is no User-to-Supervisor transition
and the stack is already a Supervisor stack. W1/W2 may have arbitrary
mappings at that moment. Therefore, the interrupt entry path and all
code that it must call unconditionally must reside in W0. Any use of W3
by an ISR must obey the W3 lifetime and switching rules in §3.2.

### 4.2 Interrupt mode — IM1 \[RECOMMENDATION\]

Use IM1, with the handler at `0038h`, and read the interrupt source
number from the PIC:

``` asm
isr_entry:                  ; 0038h in W0 of SUPER_SLOT
    ...save registers...
    IN   A,(PIC_VEC)        ; interrupt source number
    LD   L,A
    LD   H,isr_table_hi
    JP   (HL)               ; dispatch to source handler
```

**Why not IM2?** In IM2, the vector address is obtained from a table at
`I*256 + vec`, and register `I` belongs to User. An application could
point `I` at its own table and cause execution at an arbitrary address
with kernel privileges. IM1 fixes the entry point at `0038h`.

### 4.3 NMI — \[ACCEPTED\]

NMI is reserved for fatal errors. The handler’s task is to preserve what
it can and display a diagnostic screen showing the reason and, where
possible, the processor/device state at the time of the error. W0
contains enough code to produce this screen.

Clarifications \[RECOMMENDATION\]:

- NMI may arrive while `SP` still points into User memory. The handler
  must not rely on that stack; it switches to the kernel stack before
  doing substantial work.
- A cause register is needed for NMI (in the PIC or as a separate
  register); otherwise the diagnostic screen has no useful reason to
  display.

### 4.4 No hardware IPC mailbox — \[ACCEPTED\]

The original argument for an IPC mailbox was: “the kernel code may be
unavailable when an interrupt occurs.” That argument no longer applies
once an interrupt is guaranteed to switch the slot set to Supervisor and
the ISRs reside in W0.

The other proposed uses of a mailbox are also unnecessary:

- **Notifying the kernel of an event.** A pending bit in the PIC and an
  event mask in kernel RAM are sufficient (§4.5).
- **Transferring data.** Data resides in device registers or buffers,
  not in a mailbox.
- **The reverse direction (kernel → driver).** The kernel calls the
  driver directly; both execute in the same Supervisor map.

**When to reconsider.** A mailbox makes sense only if there is a second
bus master or processor (for example, ARM/HPS on MiSTer or a soft-core
CPU) that needs a communication channel to the kernel. It is not needed
in the current architecture. Section 9 of the specification (IPC
Mailbox) can therefore be marked optional or removed. It is not
implemented on MiSTer either (D06).

### 4.5 Deferred ISR work — \[RECOMMENDATION\]

The Z80 guarantees that a single instruction is atomic with respect to
an ISR. This allows a simple pattern:

``` asm
; Inside the ISR (one instruction is atomic):
    LD   HL,pending_mask
    SET  EVT_DISK,(HL)          ; mark event

; In the kernel, at a safe point:
    DI
    LD   A,(pending_mask)
    LD   (pending_mask),0       ; take and clear pending events
    EI
    ; decode bits in A: bottom half
```

The ISR only **adds** events. The kernel **takes** them under a short
`DI`-protected operation. Simultaneous occurrences coalesce through OR;
the flags are idempotent (“disk ready”, “sound buffer empty”). Payload
data is not carried in the mask. It is carried in device status or a
ring buffer, with the ISR as the sole producer.

**Rules for an ISR-safe API \[RECOMMENDATION\]:**

- An ISR calls only a short, explicitly defined list of kernel
  functions, such as `post_event`, `enqueue`, and `signal`. These
  functions reside in W0 and are re-entrant.
- Anything that could be interrupted halfway through and corrupt shared
  structures is deferred: the ISR sets a flag and the kernel performs
  the operation later.
- Banked code in W1/W2/W3 is called from an ISR only through a far-call
  mechanism that saves and restores the window it touches, and only if
  the relevant bank lifetime is guaranteed.

### 4.6 Preemption — \[OPEN\]

The Z80 does not allow User software’s `DI`, `EI`, `HALT`, or `LD I,A`
instructions to be trapped. A User application can disable interrupts,
and Supervisor mode does not prevent it. Preemptive multitasking
therefore requires an interrupt source independent of `DI` (for example,
a second non-maskable timer). For now, NMI is reserved for fatal errors.
It remains undecided whether scheduling is cooperative only or whether a
separate preemption mechanism is required (question O5).

------------------------------------------------------------------------

## 5. Syscalls

### 5.1 Calling convention — \[ACCEPTED\]

- **One entry path only.** `RST 6` (`0030h`). The trap is triggered by a
  fetch from `0030h` in User when `rst6_hook` is enabled. The Z80 itself
  pushes the return address onto the User stack before the vector fetch
  causes the hardware transition. Registers are not modified by the
  transition itself.
- **There is no `F2h` alias.** `OUT (F2h),A` has been removed as a
  separate mechanism: it has different behaviour (opcode substitution
  and implementation dependence), requires a separate port detector,
  clobbers `BC` in Legacy, and is harder to implement and debug. The
  standard `RST 6` instruction provides the required entry mechanism.
- **Calling convention:** function number in `A`; arguments in `BC`,
  `DE`, and `HL`; result in `A` (0 = success), and, when needed, in
  `HL`. `RST 6` does not clobber `BC`.

``` asm
; Call from User:
    LD   A,SYS_WRITE
    RST  30h                 ; 11 T
```

### 5.2 Why `RST 6`

- **It is not masked by `DI`.** It provides the unconditional entry that
  was originally sought through `OUT`.
- **The CPU pushes the return address itself.** `RST 6` pushes the
  return address onto the **User stack**, using the User `SP` and User
  map, because the trap occurs on the fetch from `0030h`, **after** the
  stack write. This closes Q24 (where the return address is stored: on
  the User stack, by the standard Z80 mechanism). Q22 (how the kernel
  accesses the User stack) is closed by the `RETN` exit mechanism
  (§5.5).
- **It does not clobber `BC`**, so no Legacy wrapper is needed.
- **It is shorter and faster** than a wrapper: 11 T versus `CALL` +
  `OUT` + `RET` (about 38 T).
- **Precedents:** `RST 30h` in the MSX BIOS (inter-slot call), and
  `RST 8` in ZX Spectrum ESXDOS.

### 5.3 Disable control — \[ACCEPTED\]; implementation \[RECOMMENDATION\]

A `rst6_hook` bit in `GLOBAL_CTRL` is proposed (bit 3, currently
reserved), **separate** from `supervisor_hook` (bit 2). This allows a
Legacy task to retain its own contents at `0030h`, while the kernel may
still trap `0038h` and `0066h` if desired.

**If `RST 6` is disabled (`rst6_hook = 0`), syscalls are unavailable.**
This is an intentional restriction: an application either runs in the
native environment and uses `RST 6`, or runs in an isolated Legacy
environment without syscalls. Policy: for Legacy tasks that do not use
`0030h`, `rst6_hook` may remain enabled; for those that do use it, it
must be disabled.

### 5.4 Kernel entry: hardware vector transition

The fetch from `0030h` causes the hardware to activate `SUPER_SLOT`. The
bytes at `0030h` are the kernel’s RST 6 vector in permanent W0; no
software `DI`/`JP` sequence is required to perform the transition.

The syscall entry path then:

1.  saves the User `SP` in kernel state;
2.  switches to the kernel stack in W0;
3.  saves the required registers and identifies the entry context;
4.  dispatches according to the function number in `A`.

The precise vector contents and register-save sequence are
implementation details of the W0 kernel entry code. The important
architectural point is that the map switch is performed by hardware on
the vector fetch, not by an instruction executed at `0030h`.

The interrupt-entry and syscall-entry paths must preserve the standard
Z80 semantics of the relevant instruction and interrupt source. Any
hardware status latch used to report the origin or saved
interrupt-enable state must be specified in terms of the state captured
at the actual transition, not as an ambiguous sample taken after the CPU
has already modified its flip-flops.

### 5.5 Leaving Supervisor — \[RECOMMENDATION\]

**`RETN` is the context-switch point.** The hardware recognizes `ED 45`
on the bus and switches to User, activating `USER_SLOT`, **after the
fetch of `45h` but before the stack read**. Thus `RETN` reads the return
address from the User stack, using the User map.

The kernel does **not** read the User stack. It only restores `SP` so
that the return address is at the top of that stack, then executes
`RETN`.

Sequence:

1.  The kernel restores the User `SP`, with the return address at the
    top of the stack.
2.  The kernel writes a value to `GLOBAL_CTRL` with
    `supervisor_mode = 0`. This only **arms** the exit; it does not
    itself change the active mode.
3.  The kernel restores registers (including `A`) and executes `RETN`.
4.  When the hardware sees `ED 45` on the bus, it switches to User and
    activates `USER_SLOT` after the fetch of byte `45h`, but before the
    stack read.
5.  `RETN` reads the return address **in the User map** and loads it
    into `PC`.
6.  `RETN` copies `IFF2` to `IFF1`, restoring the interrupt-enable state
    prepared by the kernel.
7.  The next instruction executes in User at the return address.

**Why this mechanism:**

- The transition is tied to `RETN`, not to “the next M1” after a
  control-register write. This removes the ambiguity in Q28: a literal
  “next M1” would trigger on the `ED` prefix byte of `RETN` itself.
- Arbitrary instructions may execute between arming the transition and
  `RETN` (for example, register restoration). Writing to `F0h` must not
  consume `A`, which may contain the syscall result.
- The return address is read from the User stack under the User map, so
  the kernel does not need special access to User memory (**Q22
  closed**).
- `RETN` copies `IFF2` to `IFF1`; the kernel prepares `IFF2` from the
  saved interrupt state before executing it.
- Z80 peripherals already recognize `RETI` in a similar bus-based way
  (`ED 4D`); the general technique is familiar.

The ordinary Z80 semantics of INT and NMI, including their effects on
`IFF1` and `IFF2`, remain in force. The hardware transition does not
replace those CPU semantics. The kernel’s entry/exit code must preserve
the appropriate state for the particular entry source.

**If `RETN` does not work as intended** (for example, because the
application has corrupted its stack and `RETN` reads the wrong address),
the result is a crash or a jump to an arbitrary location. `SP` is not
validated. Recovery is not possible. This is an intentional limitation:
the system protects against mistakes, not deliberate corruption.

### 5.6 Syscall cost — principle \[ACCEPTED\], number \[OPEN\]

A complete round trip (`RST`, entry code, stack switch, dispatch,
restoration, exit) is estimated at 200–300 T, or 50–75 μs at 4 MHz. This
is an estimate, not a measurement.

- For calls made no more than once per frame (file operations, mode
  changes, sector requests), the cost is negligible.
- For calls inside a tight loop (pixel, sprite, sample), it is
  unacceptable. Such operations should be batched (a buffer in shared
  memory and one syscall per batch) or implemented in application code,
  rather than optimized by making every operation a faster syscall.

The accepted principle is therefore: a syscall is not an inherently
heavy process; it is the price of safety and convenience. It simply must
not be placed in the hottest inner loop.

------------------------------------------------------------------------

## 6. Drivers and the entry table

### 6.1 Driver structure

A driver consists of an **implementation** (code) and an **entry table**
(one entry per method). The table is at a fixed address in W3; the
implementation is in the same W3 environment.

### 6.2 One table, two representations — \[ACCEPTED\]

|                       | Supervisor (including takeover)            | User                                                                                        |
|-----------------------|:-------------------------------------------|:--------------------------------------------------------------------------------------------|
| Table entry           | `JP` directly to the method implementation | **Stub:** `LD A,n / RST 6 / RET` (fixed, with no logic)                                     |
| What the call does    | Executes the method in the same window     | Performs a syscall                                                                          |
| Driver implementation | In W3, in the same window                  | **Not required** (safe memory operations are a library; privileged operations use syscalls) |
| Speed                 | Direct call (about 27 T for `CALL` + `JP`) | Full syscall cost                                                                           |
| Purpose               | Driver methods with one fixed ABI          | A common entry point that enables takeover without recompilation                            |

The application calls `CALL TABLE + n*K`. The contents at that address
depend on the active environment.

### 6.3 Why keep stubs if they always invoke a syscall? — \[ACCEPTED\]

They do not make calls faster. A `SYSCALL n` macro at the call site
would be sufficient by itself (18 T versus about 45 T). **The stubs
exist for one reason:** to let the same application enter Supervisor
takeover mode **without recompilation**. At the same address, User
contains a stub while takeover contains a direct jump to the driver
method. There is one binary; the kernel selects the mode.

This is consistent with the observation that in the User environment
most driver calls go through syscalls, so the application runs more
slowly. If speed is required, takeover is enabled and those same calls
become direct calls.

Secondary benefits of stubs (stable ABI, interception for tracing and
emulation, late binding) are incidental and do not by themselves justify
a separate window.

### 6.4 Table design considerations — \[RECOMMENDATION\]

1.  **Entry numbers match syscall numbers.** Use one numbering scheme
    rather than two.
2.  **The kernel does not trust the table.** A User stub resides in
    application memory. The kernel validates the function number and
    arguments just as it does for a direct `RST 6`. The table is a
    convenience, not a security boundary.
3.  **Driver state does not live in the table.** Pass context through a
    pointer (for example, `IX`) to caller-owned memory. The table page
    therefore does not change during an operation.
4.  **Window operations also use the table.** A call such as
    `map(window, handle)` is a syscall in User and a direct write to
    `BANK_n` in takeover. The application writes `CALL map_window` once
    and works in both modes.
5.  **Safe memory operations are libraries, not drivers.** Drawing,
    copying, and decompression do not require privilege and do not
    belong in the driver table; they are called from the application
    library.

------------------------------------------------------------------------

## 7. Application operating modes

| Level | Mode                         | Application location                          | Driver call mechanism              | Scheduler                                                     |
|------:|:-----------------------------|:----------------------------------------------|:-----------------------------------|:--------------------------------------------------------------|
|     0 | User (managed)               | Its own map (`USER_SLOT`)                     | Stubs → `RST 6`                    | Active                                                        |
|     1 | Takeover                     | W1/W2 (code and data)                         | Direct `CALL` through the W3 table | Disabled                                                      |
|     2 | Takeover with a W0 extension | W1/W2 plus a fragment inside a virtualized W0 | Same as takeover                   | Disabled; experimental, not part of the baseline architecture |

**Principle \[ACCEPTED\]:** Supervisor mode is not a protection boundary
against the application itself. It exists to let applications run in a
managed environment, but a user may choose to write an application that
runs entirely in Supervisor. There is therefore no contradiction between
“protected” and “direct” driver calls: they are two operating modes
selected by the kernel at the application’s request.

**Takeover is an application class, not a separate protection
mechanism.** The application explicitly requests takeover, and the
kernel changes the active environment accordingly.

The former proposal to place an application fragment in a virtualized W0
is no longer part of the baseline design. W0 is permanent system memory.
Any future mechanism that lends W0 space to an application would require
a separate architectural proposal and must not compromise the fixed
vectors or kernel state.

------------------------------------------------------------------------

## 8. Takeover

### 8.1 What it is

The `takeover` syscall permanently transfers execution to Supervisor and
establishes this map:

| Window | Contents during takeover                                                     |
|:-------|:-----------------------------------------------------------------------------|
| W0     | Permanent kernel and ISRs                                                    |
| W1, W2 | Application memory (code, data, graphics buffers, etc.)                      |
| W3     | Selected Supervisor driver environment: entry table with direct `JP` entries |

Interrupts continue to enter through `0038h` in W0. No
User-to-Supervisor trap is needed for ordinary interrupts because the
processor is already in Supervisor.

### 8.2 Why this resolves the original conflict

The original problem was that the application needs a driver table for
speed, while protection requires calls to go through syscalls. Takeover
resolves the conflict by giving the choice to the application. Speed and
protection are not forced into one mode; there are two modes. The
application explicitly agrees to give up protection and receives direct
access.

### 8.3 Conditions and consequences

1.  **The application fits in W1/W2.** For the same binary to run in
    both User and takeover, its code and data must fit within the 32 KB
    provided by W1 and W2. W0 is occupied by the kernel, and W3 contains
    the driver environment. Additional memory is obtained by switching
    W1/W2 banks (through `map(...)` in User and directly in takeover).

2.  **The scheduler is disabled.** An application in takeover
    monopolizes the processor. For the Z80 this is an honest and
    familiar mode (similar to “system takeover” on the Amiga). This must
    be stated explicitly in the documentation.

3.  **The ISR uses a kernel stack.** On entry from User, the return
    address has already been pushed onto the User stack. The handler
    saves the User `SP`, switches to the kernel stack in W0, performs
    its work, restores the saved `SP`, and returns with `RETN`. When
    already in Supervisor, the appropriate Supervisor stack is used.
    This avoids requiring a documented minimum amount of free space on
    an application stack for kernel ISR work.

4.  **Kernel calls remain available through `RST 6`.** In Supervisor,
    `RST 6` does not cause a User-to-Supervisor trap; it simply fetches
    the vector in the already active Supervisor map. The entry code
    distinguishes a User-originated trap from a call made while already
    in Supervisor and uses the appropriate return path (`RETN` for a
    User transition, ordinary `RET` where applicable).

5.  **Hardware state is the application’s responsibility.** The kernel
    does not know what the application has done to devices. Each driver
    should provide a `reset()` entry, called when takeover ends.

6.  **Exit.** The same `RST 6` mechanism (or a dedicated `end_takeover`
    syscall) restores the managed environment and returns to User using
    the sequence in §5.5.

7.  **W0 is not hardware-protected in takeover.** An application that
    redirects `BANK_0` can break the ISR. Under the “user takes
    responsibility” principle, this is acceptable. If protection is
    required, an optional hardware write-protect for `BANK_0` in this
    mode may be added.

### 8.4 W3 environment changes during takeover

An application may request a different driver environment or W3 bank,
but the actual switch is performed by the kernel. The kernel must first
reach a safe point:

- no instruction is currently executing from the W3 bank being replaced;
- no active stack resides in that bank;
- no driver call is in progress;
- no asynchronous operation still depends on code or state in that bank;
- any required driver cleanup or state handoff has completed.

The switch routine and all state needed to perform it reside in W0. Once
the new W3 bank is selected, execution resumes through the stable public
entry table and ABI.

This is a kernel-mediated environment switch, not an
application-controlled bank-register write.

### 8.5 Summary: how the modes relate

``` text
User (managed)          RST 6 → kernel → RETN              slower, managed
       |
       | takeover (same binary; same call sites)
       v
Supervisor takeover    CALL → JP → driver implementation  fast, unprotected
       |
       | request a W3 environment change
       v
Supervisor takeover    kernel switches W3 at a safe point
```

------------------------------------------------------------------------

## 9. Asynchrony and files — \[RECOMMENDATION\]

The proposed model lets the application regain control immediately and
poll a flag in its own loop. Details:

- **Request control block (RCB).** An RCB such as
  `{status, result, len}` resides in RAM. The kernel writes `status`
  when the operation completes. The application polls it while doing
  other work (for example, redrawing the screen).

- **RCB location.** It resides in a shared region mapped in both slot
  sets (similar to common memory in CP/M-3). The kernel therefore does
  not need a special mechanism to access User memory. The contents are
  not trusted, of course; the kernel validates them just as it validates
  syscall arguments.

- **Waiting.** A `HALT` loop is harmless (a conventional CPC-style
  interrupt synchronization idiom). A true sleep operation requires a
  `wait(event)` syscall.

- **Who reads the file.** The kernel and filesystem know the file
  (cluster chain). The block driver accepts a multi-sector request—“read
  N sectors into this buffer and report completion”—and advances through
  the sectors itself in its interrupt/deferred-work path. The cycle
  “read one sector, report it, wait for the kernel to request the next”
  disappears.

- **Relation to the IPC decision.** Completion reaches the kernel
  through §4.5 (event and mask), and reaches the application through the
  RCB. No mailbox is needed in this chain.

An asynchronous request also constrains W3 switching: the kernel must
not replace a W3 environment while an outstanding request still depends
on that environment’s code or private data.

------------------------------------------------------------------------

## 10. Security: what is and is not protected

**What this model provides:**

- In User mode, the application cannot change the active map, access
  newly privileged ports, or start DMA if the relevant ports are locked
  (`mmio_userlock`).
- The only privileged entry paths are `RST 6` and the interrupt traps
  (`0038h`, `0066h`).
- The kernel does not depend on the state in which the application left
  W1/W2: the kernel and ISRs reside in W0 of Supervisor.
- If `RST 6` is disabled (`rst6_hook = 0`), syscalls are unavailable.
  This is an intentional restriction for an isolated Legacy environment.

**What is not protected:**

- The Z80 does not allow trapping User instructions
  `DI`/`EI`/`HALT`/`LD I,A`; an application in User can disable
  interrupts (§4.6).
- In takeover, the application owns the whole machine, including the
  ability to damage W0 (§8.3).
- Protection between banks is implemented through map selection, not
  memory access attributes.
- DMA addresses physical memory directly; it has not yet been defined
  who may start it and under what restrictions (Q33).
- `SP` is not validated. If the application corrupts it, `RETN` may jump
  to an invalid address, causing a crash.
- Whether a separate “unlock” mechanism from the specification (`0xFE`)
  is needed in the presence of takeover remains undecided (O6).

Documentation wording: this is protection against **mistakes** and
**unintended damage**, not against a deliberate attack.

------------------------------------------------------------------------

## 11. Rejected alternatives and why

| Alternative                                                                    | Reason for rejection                                                                                                                                                                                                                                                                                                  |
|:-------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Hardware IPC mailbox                                                           | It solves a problem that does not exist: with hardware traps and ISRs in W0, kernel code is always visible. Deferred work is handled through an event mask.                                                                                                                                                           |
| Map hash or “random index”                                                     | Needed only in a design where the kernel does not know which map is active. With separate slot sets, each side has its own map.                                                                                                                                                                                       |
| Save and restore the map in every ISR                                          | Expensive and unnecessary: the Supervisor slot set is selected by hardware.                                                                                                                                                                                                                                           |
| `OUT (F2h),A` as a syscall alias                                               | A separate mechanism with different behaviour (opcode substitution and implementation dependence), a separate port detector, `BC` clobbering in Legacy, and greater implementation/debugging complexity than one `RST 6` instruction. Its purpose is unclear because `RST 6` already provides the required mechanism. |
| User trampolines with logic (some methods work locally, others issue syscalls) | They either duplicate syscall functionality or perform work that can be done without a driver (as an application library). A User-side W3 driver body is unnecessary. Only fixed stubs remain.                                                                                                                        |
| IM2                                                                            | Register `I` belongs to User; IM2 is less safe than IM1.                                                                                                                                                                                                                                                              |
| Direct driver calls for every application                                      | This removes the distinction between managed and trusted applications. Takeover provides the same speed, but only after an explicit request.                                                                                                                                                                          |
| Virtualizing W0 and duplicating the kernel                                     | It complicates mutable kernel state and the fixed vector area. The baseline architecture instead keeps W0 permanent and virtualizes W3.                                                                                                                                                                               |
| Application code extension inside W0                                           | It conflicts with the invariant that W0 is permanent system memory. It is not part of the baseline architecture.                                                                                                                                                                                                      |

------------------------------------------------------------------------

## 12. Impact on the specification and MiSTer

### 12.1 Changes to `aleste-lx_spec_rev2.md`

| Section                | Change                                                                                                                                             |
|:-----------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------|
| §2.2 `GLOBAL_CTRL`     | Bit 3 = `rst6_hook`, separate from `supervisor_hook` (bit 2); define status bits for “entry from User” and any captured interrupt state precisely. |
| §7.2 Trap              | Add address `0030h` (controlled by `rst6_hook`). Clarify that the slot-set transition occurs on the vector fetch.                                  |
| §7.3 Syscall           | Rewrite: the **only** path is `RST 6`; `F2h` is **removed**; `rst6_hook` is the only syscall enable/disable bit.                                   |
| §7.4 Exit              | Replace “next M1” with recognition of `RETN` (switch after fetch of `45h`, before stack read); closes Q28 and Q22.                                 |
| §8 Security            | Document User and takeover modes; W0 remains permanent; W3 is virtualized. Reassess the role of unlock/`0xFE`.                                     |
| §9 IPC Mailbox         | Mark optional or remove.                                                                                                                           |
| Memory map / slot sets | Specify permanent W0, working W1/W2, and virtualized W3; define the stable W3 public table ABI and kernel-only safe switching.                     |
| New section            | “Drivers and entry table” (table format, two representations—direct table and stubs—ABI, common numbering).                                        |
| New section            | “Takeover” (conditions, exit, and kernel-mediated W3 environment changes).                                                                         |

### 12.2 Questions closed or made obsolete

| Question                                     | Resolution                                                                                                                                                                                        |
|:---------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Q24** (where the return address is pushed) | Closed by `RST 6`: the return address is pushed onto the User stack by the standard Z80 mechanism, before the vector-fetch transition.                                                            |
| **Q22** (access to the User stack)           | Closed by `RETN`: the switch occurs after fetch of `45h` and before the stack read; `RETN` reads the return address under the User map. The kernel does not need direct access to the User stack. |
| **Q28** (leaving Supervisor)                 | Closed by `RETN`: the switch is tied to `ED 45`, not to “the next M1”.                                                                                                                            |
| **Q27** (Legacy wrapper `F200h`)             | Closed: `F2h` is removed; a Legacy task either uses `RST 6` or does not use syscalls.                                                                                                             |
| **Q21, Q29, Q30**                            | Addressed by the revised entry and exit model.                                                                                                                                                    |
| **Q34–Q36**                                  | Made unnecessary by the decision to remove IPC.                                                                                                                                                   |
| W0 virtualization questions                  | Obsolete in the baseline architecture: W0 is permanent and W3 is virtualized instead.                                                                                                             |

### 12.3 MiSTer

The current implementation does not have `supervisor_hook` (D01, D09),
so some decisions (interrupt trap, `RST 6`) cannot be implemented there
without changes:

| Decision                             | Required implementation change                                                                          |
|:-------------------------------------|:--------------------------------------------------------------------------------------------------------|
| ISR in W0 Supervisor after interrupt | Trap on `0038h`/`0066h`, i.e. resolve D09.                                                              |
| `RST 6` as syscall                   | Comparator for `0030h` and the `rst6_hook` bit.                                                         |
| Exit via `RETN`                      | Detect `ED 45` on the bus (after fetch of `45h`, before stack read).                                    |
| Takeover                             | Slot sets and Supervisor mode on request; an interrupt trap is not required once already in Supervisor. |
| W3 virtualization                    | Kernel-controlled selection of the W3 bank, with safe-point rules.                                      |
| IPC                                  | Not required (it is not implemented in the current implementation either, D06).                         |
| `F2h`                                | Removed from the specification; implementation support is not required.                                 |

------------------------------------------------------------------------

## 13. Open questions

| No. | Question                                                                                                                                                | Why it matters                                                                                                                              |
|:----|:--------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------|
| O1  | What is the exact size and address of the W3 driver entry table (a dedicated region or the last 256 bytes of an application bank)?                      | Determines how much memory remains for the W3 environment (§6).                                                                             |
| O2  | What is the exact W3 switching protocol and safe-point API?                                                                                             | Ensures that code, stacks, driver state, and asynchronous operations are no longer using the old bank when it is replaced (§3.2, §8.4, §9). |
| O3  | Is the W3 table size sufficient for all required driver methods and future ABI extensions?                                                              | Determines table layout and compatibility.                                                                                                  |
| O4  | Are any User-mode driver functions needed that do not issue syscalls?                                                                                   | Determines whether the User table remains stubs only (§6.2).                                                                                |
| O5  | Preemption: cooperative scheduling only, or a second non-maskable source?                                                                               | §4.6.                                                                                                                                       |
| O6  | Is `0xFE`/unlock still needed in the presence of takeover, and in what form?                                                                            | §10.                                                                                                                                        |
| O7  | Legacy tasks: should the hook remain enabled (potentially costly at about 300 interrupts per second), be disabled, or have a separate lightweight path? | Q23.                                                                                                                                        |
| O8  | Should W0 be hardware-protected in takeover (write protection for `BANK_0`)?                                                                            | §8.3.                                                                                                                                       |
| O9  | Is a “level 4” required, in which the application takes W0 as well and can return only by reset?                                                        | §8.                                                                                                                                         |
| O10 | Measure the real cost of a syscall round trip (`RST 6` and return).                                                                                     | §5.6.                                                                                                                                       |
| O11 | Do Q05 (bank width), Q19 (`MMU_EXT` address), and similar specification questions remain open?                                                          | They determine whether the architecture described above is implementable.                                                                   |

The Z80 interrupt-entry and return semantics are not treated here as a
separate architectural debate: INT and NMI retain their standard CPU
behaviour. The hardware specification must, however, define precisely
when it changes the slot set and what state, if any, it latches for the
kernel.

------------------------------------------------------------------------

## 14. One-paragraph conclusion

An interrupt causes a hardware transition to Supervisor at vector fetch;
the kernel and ISRs reside in permanent W0 and are therefore always
visible, so no hardware mailbox is required. Syscalls use exactly one
mechanism, `RST 6`; the `F2h` alias has been removed because it
introduces a more complicated protocol with different behaviour. `RST 6`
pushes the return address onto the User stack (Q24), and `RETN` reads it
under the User map because the hardware switches back after fetching
`45h` but before reading the stack (Q22). W1 and W2 provide 32 KB of
working memory. W3 contains the driver entry table and a virtualized
driver environment: in Supervisor the table jumps directly to method
implementations, while in User it consists of fixed stubs that invoke
syscalls. The same binary can therefore run in managed User mode or in
takeover mode without recompilation; in takeover, the application uses
direct driver calls, the kernel remains in W0, and W3 changes only on a
kernel request at a safe point. W0 is never virtualized in the baseline
architecture. If `RST 6` is disabled, syscalls are unavailable—an
intentional restriction for an isolated Legacy environment. If `RETN`
reads a corrupted return address, the result is a crash; recovery is not
guaranteed.
