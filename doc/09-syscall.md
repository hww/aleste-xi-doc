# LX Mode Switching Mechanisms

## 0. How to read this document

This document describes the four mode-switching mechanisms of LX:

1. **Software switching** — write to `GLOBAL_CTRL`.
2. **Hardware trap** — M1 at `0038h` / `0066h`.
3. **Syscall** — write to `F2h` (Native) / `F2xxh` (Legacy).
4. **Exit from Supervisor** — write 0 to bit 0 of `GLOBAL_CTRL`, then `RETN`.

**RTL (`gen_rtl`) is authoritative.** Where this document and the RTL
differ, the RTL wins.

### Markers

| Marker | Meaning |
|---|---|
| **✔ By design** | An intentional RTL decision. |
| **⚠ Spec:** | The old specification differs from the RTL. **RTL is authoritative.** |
| **⚠ Outdated:** | The old document may be stale. |

---

## 5.1 Software mode switching

**Port:** `GLOBAL_CTRL` = `F0h` in Native mode.

> **⚠ Spec:** Old `lx_syscall.md` said the port was `F000h` in Legacy
> mode. **This is wrong.** `F000h` does not exist. In Legacy mode, the
> only syscall port is `F2xxh` (see §5.3). There is no `GLOBAL_CTRL` in
> Legacy mode — mode control is a Native concept. **RTL is
> authoritative.**

### 5.1.1 `GLOBAL_CTRL` bit map

```
7 6 5 4 3 2 1 0
│ │ │ │ │ │ │ └─ bit 0: supervisor_mode (0 = User, 1 = Supervisor)
│ │ │ │ │ │ └─── bit 1: native_mode     (0 = Legacy, 1 = Native)
│ │ │ │ │ └───── bit 2: supervisor_hook (0 = disabled, 1 = enabled)
│ │ │ │ └─────── bit 3: reserved (must be 0)
│ │ │ └───────── bit 4: mmio_userlock   (0 = unlocked, 1 = locked)
└─┴─┴─────────── bits 5–7: reserved (must be 0)
```

**✔ By design (RTL):** `reg_ctrl_super_in = din[0]`,
`reg_ctrl_native_mode = reg_control[1]`, `reg_ctrl_trap_enabled = reg_control[2]`,
`reg_ctrl_user_lock = reg_control[4]`. This matches the RTL.

### 5.1.2 Bit descriptions

**bit 0 — `supervisor_mode`** (0 = User, 1 = Supervisor)

- Determines the current execution mode.
- In Supervisor mode, all system registers are accessible.
- In User mode, access is restricted.

**bit 1 — `native_mode`** (0 = Legacy, 1 = Native)

- Legacy mode: CPC 6128 compatibility.
- Native mode: modern LX address space and port map.
- **✔ By design:** in Supervisor mode, `native_mode` is ignored — the
  Native mechanism is always used.

**bit 2 — `supervisor_hook`** (0 = disabled, 1 = enabled)

- Enables hardware entry into Supervisor mode on M1 at `0038h` (IM 1)
  or `0066h` (NMI).
- Only active when the M1 cycle is active.
- Allows the kernel to intercept interrupt handling.

**bit 4 — `mmio_userlock`** (0 = unlocked, 1 = locked)

- **Purpose:** prevents accidental or unauthorised access to MMU ports
  from User mode.
- **Behaviour:** when set (1), access to MMU ports is blocked in User
  mode; only `F2` (syscall) is available.
- **Usage:** the kernel sets `mmio_userlock` before starting a user
  process; the user process cannot access MMU ports; only Supervisor
  mode can change this bit.
- **Motivation:** security, prevents privilege escalation.

> **⚠ Spec:** Old `lx_syscall.md` described bit 4 as "User cannot
> change `GLOBAL_CTRL`". In the RTL, `mmio_userlock` blocks **all MMU
> ports** (including `F0`), not only the mode bits. The effect is the
> same (User cannot change modes), but the mechanism is broader: the
> whole MMU port range is blocked. **RTL is authoritative.**

### 5.1.3 Constants

```asm
; GLOBAL_CTRL constants
GCTRL_SUPERVISOR  equ 0b00000001
GCTRL_NATIVE      equ 0b00000010
GCTRL_HOOK        equ 0b00000100
GCTRL_USER_LOCK   equ 0b00010000
```

### 5.1.4 Examples

```asm
; ===== Supervisor mode (kernel) =====

; Init: Native + Supervisor + Hook enabled
LD A, GCTRL_SUPERVISOR | GCTRL_NATIVE | GCTRL_HOOK  ; 00000111b
OUT (F0h), A

; Prepare to start a user process:
; 1. Clear Supervisor, keep Native, enable Lock
LD A, GCTRL_NATIVE | GCTRL_USER_LOCK  ; 00010010b
OUT (F0h), A     ; User mode, switching blocked

; Now the user cannot change the mode.

; For interrupt handling in a user process:
; 1. Enable Hook (allow Supervisor entry on interrupt)
LD A, GCTRL_NATIVE | GCTRL_HOOK | GCTRL_USER_LOCK  ; 00010110b
OUT (F0h), A

; Return to full Supervisor mode (unlock + supervisor)
LD A, GCTRL_SUPERVISOR | GCTRL_NATIVE | GCTRL_HOOK  ; 00000111b
OUT (F0h), A
```

### 5.1.5 Hardware logic for `mmio_userlock`

**✔ By design (RTL):**

```systemverilog
wire port_access_grant = supervisor_mode || !reg_ctrl_user_lock;
wire is_mmu_access = is_io_access && addr_is_mmu_space &&
                     reg_ctrl_native_mode && port_access_grant;
```

When `mmio_userlock = 1` and the CPU is in User mode, `port_access_grant = 0`,
and all MMU ports (`E0–FF`) are blocked. Only `F2` (syscall) is reachable,
because syscall is handled in a separate path (`is_syscall_access`, not
`is_mmu_access`).

> **⚠ Spec:** Old `lx_syscall.md` showed Verilog that checked
> `io_addr == GLOBAL_CTRL_PORT` and blocked writes only to `GLOBAL_CTRL`.
> The RTL blocks the whole MMU range. **RTL is authoritative.**

### 5.1.6 Practical scenarios

```asm
; Scenario 1: safe user process
; Kernel starts it:
    LD A, GCTRL_NATIVE | GCTRL_USER_LOCK
    OUT (F0h), A     ; start with protection

; User tries to cheat:
    LD A, GCTRL_SUPERVISOR | GCTRL_NATIVE
    OUT (F0h), A     ; ignored! still in User mode

; Scenario 2: trusted syscall
; User calls syscall:
    OUT (F2h), A     ; enters Supervisor
                     ; kernel temporarily lifts User Lock
                     ; handles the call
                     ; returns with Lock set

; Scenario 3: interrupt handling
; User Lock set, Hook enabled
; Interrupt arrives -> automatic transition to Supervisor
; Kernel handles -> returns to User with Lock
```

**Advantages of `mmio_userlock`:**

1. Protection against accidental changes — user code cannot switch mode.
2. Attack prevention — makes exploitation harder.
3. Determinism — guaranteed system state.
4. Simple implementation — minimal hardware cost.

---

## 5.2 Hardware trap to Supervisor mode

**Purpose:** automatic transition to Supervisor mode on interrupt or reset.

**Trigger condition:**

```
trap_trigger = (supervisor_hook == 1) ∧
               (M1_cycle_active) ∧
               (address_bus == 0038h ∨ address_bus == 0066h)
```

**✔ By design (RTL):**

```systemverilog
wire trap_condition = m1_detected & reg_ctrl_trap_enabled &
                      (cpu_a == 16'h0038 || cpu_a == 16'h0066);
```

### 5.2.1 Why `0038h` and `0066h`

1. **`0038h`** — standard Z80 IM 1 interrupt vector.
2. **`0066h`** — NMI vector, used for critical events.
3. Both are standard Z80 addresses; no extra addresses are reserved.
4. Interrupts are already a protected mechanism (controlled by EI/DI).

**Advantages:**

- Minimal hardware cost (two comparators).
- Transparent to user code.
- Natural integration with the Z80 ecosystem.

**Note:** the trap works only when `supervisor_hook = 1`. The kernel
controls when automatic entry is allowed.

---

## 5.3 Syscall

### 5.3.1 Purpose

Syscall gives user programs access to kernel functions while preserving:

1. **Security** — no arbitrary kernel code execution.
2. **Performance** — minimal overhead.
3. **Reliability** — predictable behaviour under DI/NMI.
4. **Compatibility** — works in both Native and Legacy modes.

### 5.3.2 Mechanism choice

| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| **RST instruction** | Standard, simple | DI blocks it, conflicts with Legacy code | Unreliable under DI |
| **CALL to fixed address** | Predictable | Requires reserved address, complex protection | Conflicts with Legacy memory |
| **NMI (RST 66h)** | Always works | Catastrophic events, complex nesting | Breaks NMI semantics |
| **OUT to a special port** | Atomic, works under DI, minimal hardware | Theoretical arbitrary-call risk | **Chosen: pros outweigh** |

**Final decision:** `OUT` to a special port is the best balance of
simplicity, reliability and performance.

### 5.3.3 Implementation

**Syscall ports:**

- **Native mode:** `F2h`
- **Legacy mode:** `F2xxh` (decoded by `cpu_a[15:8] == 0xF2`)

**✔ By design (RTL):**

```systemverilog
wire is_syscall_trigger_cs =
    (SYSCALL_ADDR == (reg_ctrl_native_mode ? cpu_a[7:0] : cpu_a[15:8]));
wire is_syscall_access = is_io_access && is_syscall_trigger_cs;
wire is_syscall_trigger = is_syscall_access && is_write;
```

`SYSCALL_ADDR = 8'hF2`.

> **⚠ Spec:** Old `lx_syscall.md` said "Native `F2h`, Legacy `F200h`
> (translated by hardware)". In the RTL, the same logical port `F2` is
> decoded as `F2h` in Native (`cpu_a[7:0] == 0xF2`) and as `F2xxh` in
> Legacy (`cpu_a[15:8] == 0xF2`). This is intentional. **RTL is
> authoritative.**

> **⚠ Spec:** Old `lx_syscall.md` claimed `F2h` is "outside the standard
> Z80 port range (00h-FFh)". **This is wrong.** `F2h` is inside `F0–FF`,
> which is the MMU/control port range. **RTL is authoritative.**

> **⚠ Spec:** Old `lx_syscall.md` showed Verilog that immediately set
> `supervisor_mode <= 1`, saved `pc + 3`, and jumped to
> `SYSCALL_VECTOR`. The RTL does not save PC and does not jump: it sets
> `supervisor_mode_reg <= 1` on the syscall trigger, and the Z80 continues
> normal execution (the `OUT` instruction completes, then `RET` returns
> to the caller). **RTL is authoritative.**

**Why `F2`:**

1. It is in the MMU/control port range (`F0–FF`), which is already
   reserved for LX system use.
2. It does not conflict with typical peripherals.
3. It works in both Native and Legacy modes with a single logical port.

### 5.3.4 Calling convention

**Arguments are passed in registers (not through the port):**

1. **Standard** — matches CP/M, MSX-DOS, Unix conventions.
2. **Performance** — registers are faster than ports.
3. **Convenience** — programmers are used to this model.
4. **Flexibility** — structures can be passed by pointer.

**Standard convention:**

```asm
; BEFORE syscall:
LD A, function_code    ; function code (required)
LD BC, argument1       ; 1st argument
LD DE, argument2       ; 2nd argument
LD HL, argument3       ; 3rd argument
CALL syscall_wrapper   ; invoke the wrapper

; AFTER syscall:
; A  = return code (0 = success, otherwise error)
; HL = additional result (if needed)
; Other registers are preserved
```

**Register preservation:**

- **Preserved by the kernel:** BC, DE, HL, IX, IY, AF', BC', DE', HL'
- **May change:** A (return code), HL (additional result on success)
- **FLAGS:** set according to the result

### 5.3.5 Syscall wrapper

**Required wrapper in user code:**

```asm
syscall_wrapper:
    ; This wrapper MUST always be used to invoke a syscall
    OUT (F2h), A    ; 1. Pass the function code + enter Supervisor
    RET             ; 2. Execution returns here after handling
```

**Why a wrapper:**

1. **Single entry point** — simplifies debugging and tracing.
2. **Guaranteed RET** — ensures correct return.
3. **Extension point** — can add logging, checks.
4. **Mode abstraction** — one implementation for Native/Legacy.

**WRONG (direct call):**

```asm
OUT (F2h), A  ; Danger: the next instruction depends on the implementation
```

**RIGHT (through the wrapper):**

```asm
CALL syscall_wrapper  ; guaranteed behaviour
```

### 5.3.6 Supervisor syscall handler

**Location:** fixed address in Supervisor memory (for example, `0038h`,
the IM 1 vector, where the trap lands).

> **⚠ Spec:** Old `lx_syscall.md` said the handler was at `0100h`. In
> the RTL, the trap lands at `0038h` (or `0066h` for NMI). **RTL is
> authoritative.**

**Handler structure:**

```asm
Syscall_Dispatcher:
    ; Entry conditions:
    ; - Mode: Supervisor
    ; - A: function code (from port F2)
    ; - BC, DE, HL: arguments (from user registers)
    ; - Return PC: saved on the stack (by CALL in the wrapper)

    ; Save all registers we will use
    PUSH BC
    PUSH DE
    PUSH HL
    PUSH IX
    PUSH IY
    EX AF, AF'
    EXX
    PUSH AF
    PUSH BC
    PUSH DE
    PUSH HL

    ; Dispatch by function code
    CP SYS_OPEN
    JP Z, Syscall_OpenFile
    CP SYS_READ
    JP Z, Syscall_ReadFile
    CP SYS_WRITE
    JP Z, Syscall_WriteFile
    ; ... other functions

    ; Unknown function
    LD A, ERR_UNKNOWN_FUNCTION
    JR syscall_return

Syscall_WriteFile:
    ; BC = file_handle
    ; DE = data_size
    ; HL = data_buffer

    ; 1. Validate parameters
    ; 2. Perform the operation
    ; 3. Set the return code

    LD A, 0  ; success
    ; JR syscall_return

syscall_return:
    ; Restore registers in reverse order
    POP HL
    POP DE
    POP BC
    POP AF
    EXX
    EX AF, AF'
    POP IY
    POP IX
    POP HL
    POP DE
    POP BC

    ; A contains the return code
    ; Prepare to exit Supervisor
    PUSH AF          ; save the return code
    LD A, 00000000b  ; supervisor=0 (prepare exit)
    OUT (F0h), A     ; set the exit flag
    POP AF           ; restore the return code
    RETN             ; RETN is required: it produces the M1 cycle
                     ; that the RTL uses to complete the exit
```

> **⚠ Spec:** Old `lx_syscall.md` used `RET` for the exit. The RTL
> requires `RETN` (or `RETI`), because the exit is synchronized with
> the **next M1 cycle** (`supervisor_exit_pending && m1_detected`).
> `RET` does not produce a distinguishable M1 cycle in the same way;
> `RETN` does. **RTL is authoritative.** See §5.4.

### 5.3.7 Security

**Myth:** "OUT to a port can be called from anywhere — that is a vulnerability."

**Reality:** It is a **feature**, not a bug:

1. **User code already executes arbitrarily** — if there is a
   vulnerability, an attacker can run any code.
2. **All dangerous operations are protected** — MMU ports, interrupt
   control require Supervisor mode.
3. **The syscall handler validates parameters** — access checks.
4. **Alternatives are worse** — RST/CALL require reserved memory and
   create conflicts.
5. **Analogues in modern systems** — x86 SYSCALL/INT, ARM SVC can also
   be called from anywhere.

**Additional protections:**

- Validate all syscall parameters.
- Check resource access rights.
- Restrict syscalls in critical sections.
- Audit syscall usage.

---

## 5.4 Exit from Supervisor mode

### 5.4.1 Multi-step exit process

**Problem:** cannot switch instantly out of Supervisor because:

1. The current instruction must complete.
2. The switch must be atomic.
3. Interrupts must remain possible.

**Solution:** a multi-step exit synchronized to the M1 cycle.

**Sequence:**

```asm
; 1. INITIATE EXIT (in kernel code)
LD A, 00000000b  ; supervisor=0 (other bits as needed)
OUT (F0h), A     ; set EXIT_PENDING
; Hardware: EXIT_SUPERVISOR_PENDING = 1

; 2. FINAL INSTRUCTION IN SUPERVISOR
RETN             ; executes in Supervisor mode
; Important: this instruction MUST be RETN (or RETI)

; 3. SYNCHRONIZATION (hardware)
; Wait for the next M1 cycle

; 4. SWITCH (hardware, on M1)
; supervisor_mode = 0
; Banks switch to user
; PC points to the return address in User mode

; 5. EXECUTION IN USER MODE
; The instruction after RETN executes in User mode
```

**✔ By design (RTL):**

```systemverilog
// Exit request
if (cpu_write_stb &&
    cpu_address_reg == CONTROL_REG_ADDR[4:0] &&
    !cpu_write_data_reg[0]) begin
    supervisor_exit_pending <= 1'b1;
end

// Synchronization with M1
if (supervisor_exit_pending && m1_detected) begin
    supervisor_mode_reg <= 1'b0;
    supervisor_exit_pending <= 1'b0;
end
```

### 5.4.2 Why this sequence

1. **`RETN` in Supervisor** — ensures the return stack is restored
   correctly.
2. **M1 synchronization** — natural switch point in the Z80 instruction
   cycle.
3. **Atomicity** — an interrupt cannot slip between setting the flag
   and switching.
4. **Predictability** — always the same behaviour.

### 5.4.3 Interrupts during exit

**Scenario:** `EXIT_PENDING` set, but an interrupt arrives before M1.

**Behaviour:**

1. The interrupt is handled normally (in Supervisor mode).
2. After handling, the exit continues.
3. **No race condition.**

---

## 5.5 Practical examples

### 5.5.1 Full syscall cycle

**User program:**

```asm
    ; Open file
    LD A, SYS_OPEN
    LD BC, filename_ptr
    LD DE, access_mode
    LD HL, 0          ; not used
    CALL syscall_wrapper
    OR A              ; check for error
    JR NZ, error
    LD (file_handle), BC  ; save the handle

    ; Read file
    LD A, SYS_READ
    LD BC, (file_handle)
    LD DE, buffer_size
    LD HL, buffer_ptr
    CALL syscall_wrapper
    OR A
    JR NZ, error

    ; Close file
    LD A, SYS_CLOSE
    LD BC, (file_handle)
    CALL syscall_wrapper
```

**Syscall wrapper (in the runtime library):**

```asm
syscall_wrapper:
    OUT (F2h), A    ; Native mode
    RET

syscall_wrapper_legacy:
    OUT (F200h), A  ; Legacy mode
    RET
```

### 5.5.2 Kernel interrupt handler

```asm
Interrupt_Handler_38h:
    ; Automatically in Supervisor mode
    PUSH AF
    PUSH BC
    PUSH DE
    PUSH HL

    ; Determine the interrupt source
    IN A, (INTERRUPT_STATUS)

    ; Handle...

    POP HL
    POP DE
    POP BC
    POP AF
    EI
    RETI
```

---

## 5.6 Recommendations

### 5.6.1 For kernel developers

1. Always use the standard calling convention.
2. Validate syscall parameters carefully.
3. Save and restore all registers.
4. Use `RETN` (not `RET`) for syscall return.

### 5.6.2 For application developers

1. Always use the provided `syscall_wrapper`.
2. Check return codes.
3. Do not assume register preservation (except as documented).
4. Be aware of the mode (Native/Legacy).

### 5.6.3 For driver developers

1. Trap handlers must be minimal.
2. Use syscall for complex operations.
3. Be aware of interrupt nesting.

---

## 5.7 FAQ

**Q: Why not use RST for syscall?**
**A:** DI blocks RST, which makes the system unreliable. Syscall must
always work.

**Q: What if the user calls `OUT (F2h)` not through the wrapper?**
**A:** That violates the contract. The kernel can detect it (by checking
PC) and return an error.

**Q: How is syscall reentrancy handled?**
**A:** The kernel must handle reentrant calls correctly. Use indivisible
operations.

**Q: Can syscall be called from an interrupt?**
**A:** Yes, but carefully. The kernel must handle nested calls.

**Q: What happens if a syscall occurs during exit from Supervisor?**
**A:** The syscall has priority, is handled, then the exit continues.

---

*End of document.*
```

---

## Что исправлено относительно старого `lx_syscall.md`

| Что | Было | Стало |
|---|---|---|
| `GLOBAL_CTRL` в Legacy | `F000h` | **не существует** (Legacy не имеет `GLOBAL_CTRL`; только `F2xxh` syscall) |
| Syscall handler | `0100h` | **`0038h`** (trap vector) |
| Возврат из syscall | `RET` | **`RETN`** (M1 sync) |
| «F2 вне 00-FF» | «вне диапазона» | **`F2` внутри `F0–FF`** (MMU/control range) |
| «Legacy = Native × 256» | общее правило | **только для syscall**: `F2h` → `F2xxh` |
| `saved_user_pc <= pc + 3` | есть | **нет** в RTL (обычный Z80 flow) |
| `syscall_function <= data_bus` | есть | **`reg_syscall_function`** (на `cpu_write_stb`) |
| `supervisor_mode <= 1` мгновенно | есть | **`supervisor_mode_reg <= 1`** на trigger (не мгновенно, а по clock edge) |
| `User Lock` (bit 4) | «User не может менять `GLOBAL_CTRL`» | **блокирует все MMU-порты** (`E0–FF`), не только `F0` |
| `DEFAULT GLOBAL_CTRL` | не указан | **`8'b0001_0011`** (lock=1, supervisor=1, native=1) |

**Ключевые `⚠ Spec`:** `F000h`, `0100h`, `RET`, «F2 вне 00-FF», «Legacy = Native × 256» — **всё это устарело** и исправлено по RTL.

**Ключевые `✔ By design`:** `F2`/`F2xx` decode, `mmio_userlock` блокирует все MMU-порты, `RETN` для выхода, syscall handler на `0038h`.

Файл готов к сохранению как `lx_syscall.md` (английский, RTL-authoritative).# `lx_syscall.md` — English, corrected

```markdown
# LX Mode Switching Mechanisms

**Author:** hww (LX platform)
**Status:** reference. **Corrected against RTL (`mmu_native.sv`, `gen_rtl`).**
**Scope:** software switching, trap, syscall, exit from Supervisor.

---

## 0. How to read this document

This document describes the four mode-switching mechanisms of LX:

1. **Software switching** — write to `GLOBAL_CTRL`.
2. **Hardware trap** — M1 at `0038h` / `0066h`.
3. **Syscall** — write to `F2h` (Native) / `F2xxh` (Legacy).
4. **Exit from Supervisor** — write 0 to bit 0 of `GLOBAL_CTRL`, then `RETN`.

**RTL (`gen_rtl`) is authoritative.** Where this document and the RTL
differ, the RTL wins.

### Markers

| Marker | Meaning |
|---|---|
| **✔ By design** | An intentional RTL decision. |
| **⚠ Spec:** | The old specification differs from the RTL. **RTL is authoritative.** |
| **⚠ Outdated:** | The old document may be stale. |

---

## 5.1 Software mode switching

**Port:** `GLOBAL_CTRL` = `F0h` in Native mode.

> **⚠ Spec:** Old `lx_syscall.md` said the port was `F000h` in Legacy
> mode. **This is wrong.** `F000h` does not exist. In Legacy mode, the
> only syscall port is `F2xxh` (see §5.3). There is no `GLOBAL_CTRL` in
> Legacy mode — mode control is a Native concept. **RTL is
> authoritative.**

### 5.1.1 `GLOBAL_CTRL` bit map

```
7 6 5 4 3 2 1 0
│ │ │ │ │ │ │ └─ bit 0: supervisor_mode (0 = User, 1 = Supervisor)
│ │ │ │ │ │ └─── bit 1: native_mode     (0 = Legacy, 1 = Native)
│ │ │ │ │ └───── bit 2: supervisor_hook (0 = disabled, 1 = enabled)
│ │ │ │ └─────── bit 3: reserved (must be 0)
│ │ │ └───────── bit 4: mmio_userlock   (0 = unlocked, 1 = locked)
└─┴─┴─────────── bits 5–7: reserved (must be 0)
```

**✔ By design (RTL):** `reg_ctrl_super_in = din[0]`,
`reg_ctrl_native_mode = reg_control[1]`, `reg_ctrl_trap_enabled = reg_control[2]`,
`reg_ctrl_user_lock = reg_control[4]`. This matches the RTL.

### 5.1.2 Bit descriptions

**bit 0 — `supervisor_mode`** (0 = User, 1 = Supervisor)

- Determines the current execution mode.
- In Supervisor mode, all system registers are accessible.
- In User mode, access is restricted.

**bit 1 — `native_mode`** (0 = Legacy, 1 = Native)

- Legacy mode: CPC 6128 compatibility.
- Native mode: modern LX address space and port map.
- **✔ By design:** in Supervisor mode, `native_mode` is ignored — the
  Native mechanism is always used.

**bit 2 — `supervisor_hook`** (0 = disabled, 1 = enabled)

- Enables hardware entry into Supervisor mode on M1 at `0038h` (IM 1)
  or `0066h` (NMI).
- Only active when the M1 cycle is active.
- Allows the kernel to intercept interrupt handling.

**bit 4 — `mmio_userlock`** (0 = unlocked, 1 = locked)

- **Purpose:** prevents accidental or unauthorised access to MMU ports
  from User mode.
- **Behaviour:** when set (1), access to MMU ports is blocked in User
  mode; only `F2` (syscall) is available.
- **Usage:** the kernel sets `mmio_userlock` before starting a user
  process; the user process cannot access MMU ports; only Supervisor
  mode can change this bit.
- **Motivation:** security, prevents privilege escalation.

> **⚠ Spec:** Old `lx_syscall.md` described bit 4 as "User cannot
> change `GLOBAL_CTRL`". In the RTL, `mmio_userlock` blocks **all MMU
> ports** (including `F0`), not only the mode bits. The effect is the
> same (User cannot change modes), but the mechanism is broader: the
> whole MMU port range is blocked. **RTL is authoritative.**

### 5.1.3 Constants

```asm
; GLOBAL_CTRL constants
GCTRL_SUPERVISOR  equ 0b00000001
GCTRL_NATIVE      equ 0b00000010
GCTRL_HOOK        equ 0b00000100
GCTRL_USER_LOCK   equ 0b00010000
```

### 5.1.4 Examples

```asm
; ===== Supervisor mode (kernel) =====

; Init: Native + Supervisor + Hook enabled
LD A, GCTRL_SUPERVISOR | GCTRL_NATIVE | GCTRL_HOOK  ; 00000111b
OUT (F0h), A

; Prepare to start a user process:
; 1. Clear Supervisor, keep Native, enable Lock
LD A, GCTRL_NATIVE | GCTRL_USER_LOCK  ; 00010010b
OUT (F0h), A     ; User mode, switching blocked

; Now the user cannot change the mode.

; For interrupt handling in a user process:
; 1. Enable Hook (allow Supervisor entry on interrupt)
LD A, GCTRL_NATIVE | GCTRL_HOOK | GCTRL_USER_LOCK  ; 00010110b
OUT (F0h), A

; Return to full Supervisor mode (unlock + supervisor)
LD A, GCTRL_SUPERVISOR | GCTRL_NATIVE | GCTRL_HOOK  ; 00000111b
OUT (F0h), A
```

### 5.1.5 Hardware logic for `mmio_userlock`

**✔ By design (RTL):**

```systemverilog
wire port_access_grant = supervisor_mode || !reg_ctrl_user_lock;
wire is_mmu_access = is_io_access && addr_is_mmu_space &&
                     reg_ctrl_native_mode && port_access_grant;
```

When `mmio_userlock = 1` and the CPU is in User mode, `port_access_grant = 0`,
and all MMU ports (`E0–FF`) are blocked. Only `F2` (syscall) is reachable,
because syscall is handled in a separate path (`is_syscall_access`, not
`is_mmu_access`).

> **⚠ Spec:** Old `lx_syscall.md` showed Verilog that checked
> `io_addr == GLOBAL_CTRL_PORT` and blocked writes only to `GLOBAL_CTRL`.
> The RTL blocks the whole MMU range. **RTL is authoritative.**

### 5.1.6 Practical scenarios

```asm
; Scenario 1: safe user process
; Kernel starts it:
    LD A, GCTRL_NATIVE | GCTRL_USER_LOCK
    OUT (F0h), A     ; start with protection

; User tries to cheat:
    LD A, GCTRL_SUPERVISOR | GCTRL_NATIVE
    OUT (F0h), A     ; ignored! still in User mode

; Scenario 2: trusted syscall
; User calls syscall:
    OUT (F2h), A     ; enters Supervisor
                     ; kernel temporarily lifts User Lock
                     ; handles the call
                     ; returns with Lock set

; Scenario 3: interrupt handling
; User Lock set, Hook enabled
; Interrupt arrives -> automatic transition to Supervisor
; Kernel handles -> returns to User with Lock
```

**Advantages of `mmio_userlock`:**

1. Protection against accidental changes — user code cannot switch mode.
2. Attack prevention — makes exploitation harder.
3. Determinism — guaranteed system state.
4. Simple implementation — minimal hardware cost.

---

## 5.2 Hardware trap to Supervisor mode

**Purpose:** automatic transition to Supervisor mode on interrupt or reset.

**Trigger condition:**

```
trap_trigger = (supervisor_hook == 1) ∧
               (M1_cycle_active) ∧
               (address_bus == 0038h ∨ address_bus == 0066h)
```

**✔ By design (RTL):**

```systemverilog
wire trap_condition = m1_detected & reg_ctrl_trap_enabled &
                      (cpu_a == 16'h0038 || cpu_a == 16'h0066);
```

### 5.2.1 Why `0038h` and `0066h`

1. **`0038h`** — standard Z80 IM 1 interrupt vector.
2. **`0066h`** — NMI vector, used for critical events.
3. Both are standard Z80 addresses; no extra addresses are reserved.
4. Interrupts are already a protected mechanism (controlled by EI/DI).

**Advantages:**

- Minimal hardware cost (two comparators).
- Transparent to user code.
- Natural integration with the Z80 ecosystem.

**Note:** the trap works only when `supervisor_hook = 1`. The kernel
controls when automatic entry is allowed.

---

## 5.3 Syscall

### 5.3.1 Purpose

Syscall gives user programs access to kernel functions while preserving:

1. **Security** — no arbitrary kernel code execution.
2. **Performance** — minimal overhead.
3. **Reliability** — predictable behaviour under DI/NMI.
4. **Compatibility** — works in both Native and Legacy modes.

### 5.3.2 Mechanism choice

| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| **RST instruction** | Standard, simple | DI blocks it, conflicts with Legacy code | Unreliable under DI |
| **CALL to fixed address** | Predictable | Requires reserved address, complex protection | Conflicts with Legacy memory |
| **NMI (RST 66h)** | Always works | Catastrophic events, complex nesting | Breaks NMI semantics |
| **OUT to a special port** | Atomic, works under DI, minimal hardware | Theoretical arbitrary-call risk | **Chosen: pros outweigh** |

**Final decision:** `OUT` to a special port is the best balance of
simplicity, reliability and performance.

### 5.3.3 Implementation

**Syscall ports:**

- **Native mode:** `F2h`
- **Legacy mode:** `F2xxh` (decoded by `cpu_a[15:8] == 0xF2`)

**✔ By design (RTL):**

```systemverilog
wire is_syscall_trigger_cs =
    (SYSCALL_ADDR == (reg_ctrl_native_mode ? cpu_a[7:0] : cpu_a[15:8]));
wire is_syscall_access = is_io_access && is_syscall_trigger_cs;
wire is_syscall_trigger = is_syscall_access && is_write;
```

`SYSCALL_ADDR = 8'hF2`.

> **⚠ Spec:** Old `lx_syscall.md` said "Native `F2h`, Legacy `F200h`
> (translated by hardware)". In the RTL, the same logical port `F2` is
> decoded as `F2h` in Native (`cpu_a[7:0] == 0xF2`) and as `F2xxh` in
> Legacy (`cpu_a[15:8] == 0xF2`). This is intentional. **RTL is
> authoritative.**

> **⚠ Spec:** Old `lx_syscall.md` claimed `F2h` is "outside the standard
> Z80 port range (00h-FFh)". **This is wrong.** `F2h` is inside `F0–FF`,
> which is the MMU/control port range. **RTL is authoritative.**

> **⚠ Spec:** Old `lx_syscall.md` showed Verilog that immediately set
> `supervisor_mode <= 1`, saved `pc + 3`, and jumped to
> `SYSCALL_VECTOR`. The RTL does not save PC and does not jump: it sets
> `supervisor_mode_reg <= 1` on the syscall trigger, and the Z80 continues
> normal execution (the `OUT` instruction completes, then `RET` returns
> to the caller). **RTL is authoritative.**

**Why `F2`:**

1. It is in the MMU/control port range (`F0–FF`), which is already
   reserved for LX system use.
2. It does not conflict with typical peripherals.
3. It works in both Native and Legacy modes with a single logical port.

### 5.3.4 Calling convention

**Arguments are passed in registers (not through the port):**

1. **Standard** — matches CP/M, MSX-DOS, Unix conventions.
2. **Performance** — registers are faster than ports.
3. **Convenience** — programmers are used to this model.
4. **Flexibility** — structures can be passed by pointer.

**Standard convention:**

```asm
; BEFORE syscall:
LD A, function_code    ; function code (required)
LD BC, argument1       ; 1st argument
LD DE, argument2       ; 2nd argument
LD HL, argument3       ; 3rd argument
CALL syscall_wrapper   ; invoke the wrapper

; AFTER syscall:
; A  = return code (0 = success, otherwise error)
; HL = additional result (if needed)
; Other registers are preserved
```

**Register preservation:**

- **Preserved by the kernel:** BC, DE, HL, IX, IY, AF', BC', DE', HL'
- **May change:** A (return code), HL (additional result on success)
- **FLAGS:** set according to the result

### 5.3.5 Syscall wrapper

**Required wrapper in user code:**

```asm
syscall_wrapper:
    ; This wrapper MUST always be used to invoke a syscall
    OUT (F2h), A    ; 1. Pass the function code + enter Supervisor
    RET             ; 2. Execution returns here after handling
```

**Why a wrapper:**

1. **Single entry point** — simplifies debugging and tracing.
2. **Guaranteed RET** — ensures correct return.
3. **Extension point** — can add logging, checks.
4. **Mode abstraction** — one implementation for Native/Legacy.

**WRONG (direct call):**

```asm
OUT (F2h), A  ; Danger: the next instruction depends on the implementation
```

**RIGHT (through the wrapper):**

```asm
CALL syscall_wrapper  ; guaranteed behaviour
```

### 5.3.6 Supervisor syscall handler

**Location:** fixed address in Supervisor memory (for example, `0038h`,
the IM 1 vector, where the trap lands).

> **⚠ Spec:** Old `lx_syscall.md` said the handler was at `0100h`. In
> the RTL, the trap lands at `0038h` (or `0066h` for NMI). **RTL is
> authoritative.**

**Handler structure:**

```asm
Syscall_Dispatcher:
    ; Entry conditions:
    ; - Mode: Supervisor
    ; - A: function code (from port F2)
    ; - BC, DE, HL: arguments (from user registers)
    ; - Return PC: saved on the stack (by CALL in the wrapper)

    ; Save all registers we will use
    PUSH BC
    PUSH DE
    PUSH HL
    PUSH IX
    PUSH IY
    EX AF, AF'
    EXX
    PUSH AF
    PUSH BC
    PUSH DE
    PUSH HL

    ; Dispatch by function code
    CP SYS_OPEN
    JP Z, Syscall_OpenFile
    CP SYS_READ
    JP Z, Syscall_ReadFile
    CP SYS_WRITE
    JP Z, Syscall_WriteFile
    ; ... other functions

    ; Unknown function
    LD A, ERR_UNKNOWN_FUNCTION
    JR syscall_return

Syscall_WriteFile:
    ; BC = file_handle
    ; DE = data_size
    ; HL = data_buffer

    ; 1. Validate parameters
    ; 2. Perform the operation
    ; 3. Set the return code

    LD A, 0  ; success
    ; JR syscall_return

syscall_return:
    ; Restore registers in reverse order
    POP HL
    POP DE
    POP BC
    POP AF
    EXX
    EX AF, AF'
    POP IY
    POP IX
    POP HL
    POP DE
    POP BC

    ; A contains the return code
    ; Prepare to exit Supervisor
    PUSH AF          ; save the return code
    LD A, 00000000b  ; supervisor=0 (prepare exit)
    OUT (F0h), A     ; set the exit flag
    POP AF           ; restore the return code
    RETN             ; RETN is required: it produces the M1 cycle
                     ; that the RTL uses to complete the exit
```

> **⚠ Spec:** Old `lx_syscall.md` used `RET` for the exit. The RTL
> requires `RETN` (or `RETI`), because the exit is synchronized with
> the **next M1 cycle** (`supervisor_exit_pending && m1_detected`).
> `RET` does not produce a distinguishable M1 cycle in the same way;
> `RETN` does. **RTL is authoritative.** See §5.4.

### 5.3.7 Security

**Myth:** "OUT to a port can be called from anywhere — that is a vulnerability."

**Reality:** It is a **feature**, not a bug:

1. **User code already executes arbitrarily** — if there is a
   vulnerability, an attacker can run any code.
2. **All dangerous operations are protected** — MMU ports, interrupt
   control require Supervisor mode.
3. **The syscall handler validates parameters** — access checks.
4. **Alternatives are worse** — RST/CALL require reserved memory and
   create conflicts.
5. **Analogues in modern systems** — x86 SYSCALL/INT, ARM SVC can also
   be called from anywhere.

**Additional protections:**

- Validate all syscall parameters.
- Check resource access rights.
- Restrict syscalls in critical sections.
- Audit syscall usage.

---

## 5.4 Exit from Supervisor mode

### 5.4.1 Multi-step exit process

**Problem:** cannot switch instantly out of Supervisor because:

1. The current instruction must complete.
2. The switch must be atomic.
3. Interrupts must remain possible.

**Solution:** a multi-step exit synchronized to the M1 cycle.

**Sequence:**

```asm
; 1. INITIATE EXIT (in kernel code)
LD A, 00000000b  ; supervisor=0 (other bits as needed)
OUT (F0h), A     ; set EXIT_PENDING
; Hardware: EXIT_SUPERVISOR_PENDING = 1

; 2. FINAL INSTRUCTION IN SUPERVISOR
RETN             ; executes in Supervisor mode
; Important: this instruction MUST be RETN (or RETI)

; 3. SYNCHRONIZATION (hardware)
; Wait for the next M1 cycle

; 4. SWITCH (hardware, on M1)
; supervisor_mode = 0
; Banks switch to user
; PC points to the return address in User mode

; 5. EXECUTION IN USER MODE
; The instruction after RETN executes in User mode
```

**✔ By design (RTL):**

```systemverilog
// Exit request
if (cpu_write_stb &&
    cpu_address_reg == CONTROL_REG_ADDR[4:0] &&
    !cpu_write_data_reg[0]) begin
    supervisor_exit_pending <= 1'b1;
end

// Synchronization with M1
if (supervisor_exit_pending && m1_detected) begin
    supervisor_mode_reg <= 1'b0;
    supervisor_exit_pending <= 1'b0;
end
```

### 5.4.2 Why this sequence

1. **`RETN` in Supervisor** — ensures the return stack is restored
   correctly.
2. **M1 synchronization** — natural switch point in the Z80 instruction
   cycle.
3. **Atomicity** — an interrupt cannot slip between setting the flag
   and switching.
4. **Predictability** — always the same behaviour.

### 5.4.3 Interrupts during exit

**Scenario:** `EXIT_PENDING` set, but an interrupt arrives before M1.

**Behaviour:**

1. The interrupt is handled normally (in Supervisor mode).
2. After handling, the exit continues.
3. **No race condition.**

---

## 5.5 Practical examples

### 5.5.1 Full syscall cycle

**User program:**

```asm
    ; Open file
    LD A, SYS_OPEN
    LD BC, filename_ptr
    LD DE, access_mode
    LD HL, 0          ; not used
    CALL syscall_wrapper
    OR A              ; check for error
    JR NZ, error
    LD (file_handle), BC  ; save the handle

    ; Read file
    LD A, SYS_READ
    LD BC, (file_handle)
    LD DE, buffer_size
    LD HL, buffer_ptr
    CALL syscall_wrapper
    OR A
    JR NZ, error

    ; Close file
    LD A, SYS_CLOSE
    LD BC, (file_handle)
    CALL syscall_wrapper
```

**Syscall wrapper (in the runtime library):**

```asm
syscall_wrapper:
    OUT (F2h), A    ; Native mode
    RET

syscall_wrapper_legacy:
    OUT (F200h), A  ; Legacy mode
    RET
```

### 5.5.2 Kernel interrupt handler

```asm
Interrupt_Handler_38h:
    ; Automatically in Supervisor mode
    PUSH AF
    PUSH BC
    PUSH DE
    PUSH HL

    ; Determine the interrupt source
    IN A, (INTERRUPT_STATUS)

    ; Handle...

    POP HL
    POP DE
    POP BC
    POP AF
    EI
    RETI
```

---

## 5.6 Recommendations

### 5.6.1 For kernel developers

1. Always use the standard calling convention.
2. Validate syscall parameters carefully.
3. Save and restore all registers.
4. Use `RETN` (not `RET`) for syscall return.

### 5.6.2 For application developers

1. Always use the provided `syscall_wrapper`.
2. Check return codes.
3. Do not assume register preservation (except as documented).
4. Be aware of the mode (Native/Legacy).

### 5.6.3 For driver developers

1. Trap handlers must be minimal.
2. Use syscall for complex operations.
3. Be aware of interrupt nesting.

---

## 5.7 FAQ

**Q: Why not use RST for syscall?**
**A:** DI blocks RST, which makes the system unreliable. Syscall must
always work.

**Q: What if the user calls `OUT (F2h)` not through the wrapper?**
**A:** That violates the contract. The kernel can detect it (by checking
PC) and return an error.

**Q: How is syscall reentrancy handled?**
**A:** The kernel must handle reentrant calls correctly. Use indivisible
operations.

**Q: Can syscall be called from an interrupt?**
**A:** Yes, but carefully. The kernel must handle nested calls.

**Q: What happens if a syscall occurs during exit from Supervisor?**
**A:** The syscall has priority, is handled, then the exit continues.

---

*End of document.*
