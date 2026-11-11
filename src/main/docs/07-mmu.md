# LX MMU: Native and Legacy Memory Management

## 0. How to read this document

This document describes the memory management unit of Aleste LX: the
operating modes, the slot/bank model, the control registers, the mode
switching mechanisms, and the reset state.

**RTL (`gen_rtl`, latest) is authoritative.** Where this document and
the RTL disagree, the RTL wins.

### Markers used in this document

| Marker | Meaning |
|---|---|
| **✔ By design** | An intentional RTL decision. Described as fact. |
| **⚠ Spec:** | The old specification (`lx_mmu7.md`, `lx_mmu5.md`, `lx_mmu6.md`) differs from the RTL. **RTL is authoritative.** |
| **⚠ Outdated:** | The old document may be stale (addresses, sizes, defaults may have changed). |
| **⚠ Carlos:** | Implemented in RTL by Carlos, but **not the LX design intent**. Acknowledged and documented; **not recommended** for LX. |

### Labels used in this document

| Label | Meaning |
|---|---|
| **Mandatory** | Required for LX. |
| **Optional** | May be implemented, may be omitted. |

---

## 1. Principles

The system is built around a Z80 processor with an extended 24-bit
physical address space (16 MB), implemented through a bank-switching
mechanism similar to MSX, but with extended functionality. It supports
two operating modes (Native and Legacy) and two privilege levels
(Supervisor and User) for backward compatibility and enhanced
functionality.

**System state:**

```
S = {supervisor_mode, native_mode, mmio_userlock}
```

---

## 2. Operating modes

### 2.1 Privilege mode

Determines the level of access to system resources.

| Mode | Description |
|---|---|
| **User Mode** | Execution of application code. Restricted access to memory slots and I/O ports. |
| **Supervisor Mode** | Execution of kernel code. Full access to all system resources. Hardware entry on trap events. After reset, the system always starts in this mode. |

### 2.2 Compatibility mode

Determines which I/O device set and memory management mechanism is
active.

| Mode | Description |
|---|---|
| **Legacy Mode** | Full hardware and software compatibility with the Amstrad CPC 6128. CPC port addressing is used. In `supervisor` mode, this setting is ignored and `native` mode is always active. |
| **Native Mode** | Extended mode with new functionality, using a modern I/O port set and a full slot-based memory mapping mechanism. |

### 2.3 Mode table

[include](gen/mmu_modes-table.md)

**Important:** In Supervisor mode, the `native_mode` bit has no effect.
Native memory and device access mechanisms are always used.

**✔ By design (RTL):** `reg_ctrl_super_in = cpu_write_data_reg[0]`,
`reg_ctrl_native_mode = reg_control[1]`. This matches spec v7 (bit 0 =
supervisor, bit 1 = native).

---

## 3. Memory organization

### 3.1 Logical and physical address spaces

- **Physical address space:** 24 bits (16 MB).
- **Z80 logical address space:** 16 bits (64 KB).
- **Logical slots:** the 64 KB logical space is divided into four
  16 KB slots:

[include](gen/mmu_slots-table.md)

### 3.2 Bank switching

An 8-bit page (bank) register maps a 16 KB logical slot into the 24-bit
physical address space. The physical address is formed as:

```
physical_address = {slot, bank, offset}
```

where `slot` is 2 bits (0–3), `bank` is 8 bits (0–255), and `offset` is
14 bits (`cpu_a[13:0]`).

**✔ By design (RTL):** `m_wb_adr_o = {current_slot, mapper_bank, cpu_a[13:0]}`
in `mmu_native.sv`. This is a **24-bit address**: 2 (slot) + 8 (bank) +
14 (offset) = 24.

> **⚠ Spec:** Old spec (v7) said `physical_address = {bank_reg[7:0], cpu_a[13:0]}`
> (16 + 8 + 14 = 38 bits, or truncated). The RTL uses `{slot, bank, offset}`,
> which is the correct 24-bit form. **RTL is authoritative.**

### 3.3 Internal mapper registers

There are **16 internal mapper registers**, organized as 4 slots × 4
pages:

[include](gen/mmu_mapper_regs-table.md)

The index is computed as:

```
mapper_index = {current_slot, cpu_page}
```

where `cpu_page` is `cpu_a[15:14]` for memory access, or `cpu_a[1:0]` for
I/O access.

**✔ By design (RTL):** `mapper_index = {current_slot, cpu_page}`,
`mapper_bank = reg_bank[mapper_index]`.

> **⚠ Spec:** Old spec (v7) said `page_index = (current_slot * 4) + (address_low_bits & 0b11)`.
> The RTL computes `{current_slot, cpu_page}`, which is the same thing
> written as a concatenation. **Matches.**

---

## 4. Control registers (Native mode)

### 4.1 Port map

All MMU control registers are at ports `F0–FF` and `E0–EF`:

[include](gen/mmu_ports-table.md)

**✔ By design (RTL):** `CONTROL_REG_ADDR = 8'hF0`, `MMIO_PAGE_ADDR = 8'hF1`,
`SYSCALL_ADDR = 8'hF2`, `CLOCK_CTRL_ADDR = 8'hF3`,
`SLOT_SUPER_ADDR = 8'hFA`, `SLOT_USER_ADDR = 8'hFB`,
`MAPPER_0_ADDR = 8'hFC` … `MAPPER_3_ADDR = 8'hFF`.

> **⚠ Spec:** Old spec (v7) placed `SUPER_SLOT` at `F9h`. RTL uses
> `FAh` (`SLOT_SUPER_ADDR = 8'hFA`). **RTL is authoritative.** See §10.

> **⚠ Spec:** Old spec (v7) placed `MMU_EXT` at `FF0080–FF00BF` (via
> MMIO window). RTL uses `E0–EF` (direct CPU ports, not via window).
> **RTL is authoritative.** See §10.

### 4.2 GLOBAL_CTRL (`F0`)

[include](gen/mmu_global_ctrl-table.md)

**✔ By design (RTL):** `reg_ctrl_super_in = din[0]`,
`reg_ctrl_native_mode = reg_control[1]`, `reg_ctrl_trap_enabled = reg_control[2]`,
`reg_ctrl_user_lock = reg_control[4]`. Matches spec v7.

> **⚠ Spec:** Old spec (v7) said `mmio_userlock` default is `0` (unlocked).
> RTL resets `reg_control = 8'b0001_0011` (lock=1, supervisor=1, native=1).
> **RTL is authoritative.** See §10.

### 4.3 MMIO_PAGE (`F1`)

7-bit register (values 0–127) selecting the MMIO_LO page. The MMIO
window is at ports `00–7F`.

Formula:

```
physical_address = 0xFF0000 + (MMIO_PAGE << 7) + A[6:0]
```

**✔ By design (RTL):** `m_wb_adr_o = {8'hFF, 2'b00, reg_mmio_page[6:0], cpu_a[6:0]}`.

### 4.4 SYSCALL (`F2`)

Port for invoking operating system commands. Write-only.

- **Native mode:** `F2h` (`cpu_a[7:0] == 0xF2`).
- **Legacy mode:** `F2xxh` (`cpu_a[15:8] == 0xF2`).

**✔ By design (RTL):** `is_syscall_trigger_cs = (SYSCALL_ADDR == (reg_ctrl_native_mode ? cpu_a[7:0] : cpu_a[15:8]))`.
Syscall is handled in `mmu_native.sv` only, because syscall is a
Supervisor-entry mechanism (a native concept). `mmu_legacy.sv` does not
handle syscall; it forwards `F2xx` to Wishbone, and `mmu_native.sv`
catches it.

**✔ By design (RTL):** the syscall port is `F2` in both modes, but
decoded differently: Native uses `cpu_a[7:0]`, Legacy uses
`cpu_a[15:8]`. This is intentional — the same logical port `F2` is
reached by `F2h` in Native and by `F2xxh` in Legacy.

Matches spec v7 ("In Legacy Mode, accesses to `F2XXh` are automatically
redirected to the syscall port").

### 4.5 CLOCK_CTRL (`F3`)

CPU clock divider. Bits 0–3: bus clock divider used to derive the CPU
clock. Supervisor mode only.

**✔ By design (RTL):** `reg_clock = cpu_write_data_reg`,
`cpu_clock_conf = reg_clock[3:0]`.

> **⚠ Spec:** Old spec (v7) said `CLOCK_CTRL` reset is `00000111b` (7).
> RTL resets `reg_clock = 8'b0000_0010` (divide by 4). **RTL is
> authoritative.** See §10.

### 4.6 SUPER_SLOT (`FA`) / USER_SLOT (`FB`)

Each register holds four 2-bit slot numbers:

| Bits | Slot page |
|---|---|
| 1:0 | Slot page 0 (`0000-3FFF`) |
| 3:2 | Slot page 1 (`4000-7FFF`) |
| 5:4 | Slot page 2 (`8000-BFFF`) |
| 7:6 | Slot page 3 (`C000-FFFF`) |

**✔ By design (RTL):** `current_slot = reg_super_slot[cpu_page*2 +: 2]`
(in Supervisor), `reg_user_slot[cpu_page*2 +: 2]` (in User), where
`cpu_page = cpu_a[15:14]` for memory, `cpu_a[1:0]` for I/O.

> **⚠ Spec:** Old spec (v7) said `SUPER_SLOT` is a single 2-bit value.
> RTL uses a byte (four 2-bit slot pages). **RTL is authoritative.**
> See §10.

> **⚠ Spec:** Old spec (v7) said `SUPER_SLOT` reset is `0x00`. RTL
> resets `reg_super_slot = 8'hFF` (all pages → slot 3). **RTL is
> authoritative.** See §10.

### 4.7 BANK_0–3 (`FC–FF`)

Select the memory page for each of the four slots, in the current slot
set. Writing to `BANK_0–3` updates `reg_bank[{current_slot, 2'b00..11}]`.

**✔ By design (RTL):** `MAPPER_0_ADDR: reg_bank[{current_slot_reg, 2'b00}] <= cpu_write_data_reg`,
etc.

### 4.8 MMU_EXT (`E0–EF`)

Extended access to the mapper state (16 registers, save/restore). CPU
only.

**✔ By design (RTL):** `5'b0????: reg_bank[cpu_a[3:0]] <= cpu_write_data_reg`
in `mmu_native.sv`. `E0` → index 0, `E1` → index 1, …, `EF` → index 15.

> **⚠ Spec:** Old spec (v7) placed `MMU_EXT` at `FF0080–FF00BF` (via
> MMIO window). RTL uses `E0–EF` (direct CPU ports). **RTL is
> authoritative.** See §10.

---

## 5. Mode switching

### 5.1 Software switching

Write to `GLOBAL_CTRL` (`F0`):

```
S ← {data[0], data[1]}
```

This sets the Supervisor and Native mode bits.

**✔ By design (RTL):** `reg_ctrl_super_in = din[0]`,
`reg_ctrl_native_mode = reg_control[1]`.

### 5.2 Hardware trap to Supervisor

Entry into privileged mode is performed by hardware when:

```
trap = (supervisor_hook == 1) ∧ (M1 active) ∧ (cpu_a == 0038h ∨ cpu_a == 0066h)
```

**✔ By design (RTL):** `trap_condition = m1_detected & reg_ctrl_trap_enabled & (cpu_a == 16'h0038 || cpu_a == 16'h0066)`.

### 5.3 Syscall

Syscall is the mechanism to enter Supervisor mode from user code. It is
handled in `mmu_native.sv`, not in `mmu_legacy.sv`, because syscall is a
Supervisor-entry mechanism (a native concept).

- **Native mode:** port `F2h` (`cpu_a[7:0] == 0xF2`).
- **Legacy mode:** port `F2xx` (`cpu_a[15:8] == 0xF2`).

**✔ By design (RTL):** syscall is handled in `mmu_native.sv` only.
`mmu_legacy.sv` does not handle syscall; it forwards `F2xx` to Wishbone.
This is intentional: syscall is a Supervisor-entry mechanism.

**✔ By design (RTL):** the syscall port is `F2` in both modes, but
decoded differently: Native uses `cpu_a[7:0]`, Legacy uses
`cpu_a[15:8]`. This is intentional.

**Protocol:**

- Function code: register `A`.
- Arguments: `BC` (1st), `DE` (2nd), `HL` (3rd).
- Return: `A` (status) or `HL` (result).
- Register preservation: the Supervisor handler saves and restores all
  registers except those used to return values.

**Example:**

```asm
; Prepare arguments for syscall_write (function code 0x02)
LD A, 2              ; A = function code 'write'
LD BC, file_handle   ; BC = first argument
LD DE, data_size     ; DE = second argument
LD HL, data_buffer   ; HL = third argument
CALL syscall         ; invoke wrapper
; Check result in A (0 = success, otherwise error code)
```

**Wrapper (Native):**

```asm
syscall:
    OUT (F2h), A    ; MAGIC INSTRUCTION
    RET             ; returns here after syscall
```

**Wrapper (Legacy):**

```asm
syscall_legacy:
    OUT (F200h), A  ; MAGIC INSTRUCTION
    RET
```

### 5.4 Exiting Supervisor mode

Exiting Supervisor is a multi-step process synchronized with the
processor instruction cycle:

1. **Initiation:** kernel code writes `0` to bit 0 of `GLOBAL_CTRL`
   (`F0`).
2. **Detection:** hardware sets `EXIT_SUPERVISOR_PENDING = 1`.
3. **RETN execution:** the next instruction (usually `RETN`) executes
   entirely in Supervisor mode.
4. **M1 synchronization:** hardware waits for the **next** `M1` bus
   cycle.
5. **Mode switch:** when `M1` activates, `supervisor_mode` is cleared.
6. **Instruction fetch in User mode:** the instruction at the return
   address is fetched in User mode.

**Result:** `RETN` executes in Supervisor, the following instruction
executes in User mode.

**✔ By design (RTL):** `supervisor_exit_pending` is set when
`cpu_write_stb && cpu_address_reg == CONTROL_REG_ADDR[4:0] && !cpu_write_data_reg[0]`,
and `supervisor_mode_reg <= 0` when `supervisor_exit_pending && m1_detected`.

### 5.5 Active slot selection

The active slot depends on the current privilege mode:

```
current_slot = (supervisor_mode == 1) ? SUPER_SLOT[cpu_page] : USER_SLOT[cpu_page]
```

where `cpu_page = cpu_a[15:14]` for memory, `cpu_a[1:0]` for I/O.

**✔ By design (RTL):** `current_slot = reg_super_slot[cpu_page*2 +: 2]`
(in Supervisor), `reg_user_slot[cpu_page*2 +: 2]` (in User).

> **⚠ Spec:** Old spec (v7) said `current_slot = (supervisor_mode == 1) ? SUPER_SLOT : USER_SLOT`
> (one slot register). RTL uses four 2-bit slot pages per register, and
> selects the page based on `cpu_page`. **RTL is authoritative.**
> See §10.

---

## 6. Mapper algorithm

### 6.1 Bank register write

```
mapper_index = {current_slot, cpu_page}
reg_bank[mapper_index] = data
```

**✔ By design (RTL):** `MAPPER_0_ADDR: reg_bank[{current_slot_reg, 2'b00}] <= cpu_write_data_reg`,
etc.

### 6.2 Access security policy

[include](gen/mmu_access_policy-table.md)

**✔ By design (RTL):** `port_access_grant = supervisor_mode || !reg_ctrl_user_lock`.
`is_mmu_access = is_io_access && addr_is_mmu_space && reg_ctrl_native_mode && port_access_grant`.
`is_mmio_access = is_io_access && addr_is_mmio_space && reg_ctrl_native_mode && port_access_grant`.

> **⚠ Spec:** Old spec (v7) said `mmio_userlock` default is `0` (unlocked).
> RTL resets to `1` (locked). **RTL is authoritative.** See §10.

### 6.3 `SYS_MMIO_ACCESS_REQUEST` (function code `0xFE`)

- **Purpose:** request permission for direct MMIO access.
- **Input:** `A = 0xFE`, `BC = 0x0001`.
- **Output:** `A = result` (0 = allowed, 1 = denied).
- **Behavior:** kernel verifies the application's digital signature.
  On success, sets `mmio_userlock = 0`.

**✔ By design (RTL):** not implemented in `gen_rtl` (only the syscall
mechanism is). See §10.

---

## 7. Reset state

[include](gen/mmu_reset_state-table.md)

**✔ By design (RTL):** `reg_control <= 8'b0001_0011`,
`reg_clock <= 8'b0000_0010`, `reg_super_slot <= 8'hFF`,
`reg_user_slot <= 8'h00`, `reg_bank[i] <= 8'h00`.

> **⚠ Spec:** Old spec (v7) said `GLOBAL_CTRL = 00000110b` (lock=0),
> `SUPER_SLOT = 00`, `CLOCK_CTRL = 00000111b`. RTL resets to
> `0001_0011` (lock=1), `FF`, `0000_0010`. **RTL is authoritative.**
> See §10.

---

## 8. State machine

```
S(t+1) =
    if trap_condition then
        {1, S(t).native_mode}
    else if exit_supervisor_pending & next_M1_cycle then
        {0, S(t).native_mode}
    else if io_write_to_F0h then
        {data[0], data[1]}
    else
        S(t)
```

**✔ By design (RTL):** implemented in `mmu_native.sv` (supervisor mode
and exit logic).

---

## 9. Code examples

### 9.1 Init after reset

```asm
start:
    ; System starts in Supervisor + Native mode
    LD A, 0
    OUT (FAh), A           ; SUPER_SLOT = 0
    OUT (FBh), A           ; USER_SLOT = 0
    LD A, 00000111b        ; Clock divider
    OUT (F3h), A           ; CLOCK_CTRL
    LD A, 00000010b        ; supervisor=0, native=1
    OUT (F0h), A           ; GLOBAL_CTRL
    ; Now in User Native mode
```

**✔ By design (RTL):** `SUPER_SLOT = FAh` (not `F9h`).
> **⚠ Spec:** old example used `F9h`. **RTL is authoritative.**

### 9.2 Request MMIO access

```asm
request_mmio_access:
    LD A, 0FEh             ; SYS_MMIO_ACCESS_REQUEST
    LD BC, 0001h           ; MMIO request flag
    CALL syscall
    OR A                   ; check result
    RET NZ                 ; error if A != 0
    ; mmio_userlock=0; MMIO access is now permitted
    RET
```

### 9.3 Trap handler

```asm
    ; Configure handler in Supervisor mode
    LD A, 00000111b        ; supervisor=1, native=1, trap_enabled=1
    OUT (F0h), A           ; GLOBAL_CTRL
    ; Accesses to 0038h/0066h now trigger a hardware trap
```

### 9.4 Save/restore mapper state

```asm
save_mapper_state:
    ; Save mapper state through MMU_EXT (E0-EF)
    LD HL, save_buffer
    LD A, 0E0h             ; start of MMU_EXT
    LD D, 16               ; 16 registers
.save_loop:
    OUT (A), A             ; access through MMU_EXT
    IN A, (00h)            ; (pseudocode, implementation-dependent)
    LD (HL), A
    INC HL
    INC A
    DEC D
    JR NZ, .save_loop
    RET
```

**✔ By design (RTL):** `MMU_EXT` is at `E0–EF` (direct CPU ports), not
at `FF0080–FF00BF`.
> **⚠ Spec:** old example used the MMIO window. **RTL is authoritative.**

---

## 10. Open questions

1. **`SUPER_SLOT`: `F9h` vs `FAh`.** Spec (v7) said `F9h`; RTL uses
   `FAh`. Which is correct for LX? *TBD.*
2. **`MMU_EXT` location.** Spec (v7) placed it at `FF0080–FF00BF` (via
   MMIO window); RTL uses `E0–EF` (direct CPU ports). Which is correct
   for LX? *TBD.*
3. **`mmio_userlock` default.** RTL resets to `1` (locked); spec (v7)
   said `0` (unlocked). Which is correct for LX? *TBD.*
4. **`CLOCK_CTRL` reset.** RTL resets to `2` (divide by 4); spec (v7)
   said `7`. Which is correct for LX? *TBD.*
5. **`SUPER_SLOT` reset.** RTL resets to `FF` (all pages → slot 3);
   spec (v7) said `00`. Which is correct for LX? *TBD.*
6. **`current_slot` selection.** Spec (v7) said one slot register per
   mode; RTL uses four 2-bit slot pages per register, selected by
   `cpu_page`. Which is correct for LX? *TBD.*
7. **`SYS_MMIO_ACCESS_REQUEST`.** Not implemented in `gen_rtl` (only
   the syscall mechanism is). Should LX implement it? *TBD.*
8. **D62 / MAPMOD / MSX mapper.** Implemented in `mmu_legacy.sv` (520EX
   heritage). See `lx_legacy.md` §2. **Not recommended** for LX.
9. **`physical_address` form.** Spec (v7) said `{bank, offset}`; RTL
   uses `{slot, bank, offset}`. **RTL is authoritative.** *TBD whether
   to update the spec.*

---

*End of document.*
