---
title: "Aleste LX"
subtitle: "Memory Management and Expansion System"
author: "h2w"
language: en
---

# Aleste LX

## Memory Management and Expansion System

# Fundamental Principles
<a id="fundamental-principles"></a>

The system is built around a Z80 processor with an extended 24-bit
address space (16 MB), implemented through a bank-switching mechanism
similar to MSX, but with extended functionality. It supports two main
operating modes to provide backward compatibility and enhanced
functionality.

# Operating Modes
<a id="operating-modes"></a>

The system state is determined by two independent parameters: the
privilege mode and the active I/O device set.

`S = {supervisor_mode, native_mode, mmio_userlock}`

## Privilege Mode
<a id="privilege-mode"></a>

Determines the level of access to system resources.

- **User Mode**: Execution of application code. Access to memory slots
  and I/O ports is restricted.
- **Supervisor Mode**: Execution of kernel code (privileged mode).
  Full access to all system resources. Hardware entry on trap events.
  After reset, the system always starts in this mode.

## Compatibility Mode
<a id="compatibility-mode"></a>

Determines which I/O device set and memory management mechanism are
active.

- **Legacy Mode**: Full hardware and software compatibility with the
  Amstrad CPC. CPC port addressing is used. In `supervisor` mode, this
  setting is ignored and `native` mode is always active.
- **Native Mode**: Extended mode with new functionality, using a modern
  I/O port set and a full slot-based memory mapping mechanism.

## Operating Mode Table
<a id="operating-mode-table"></a>

| Mode | Supervisor | Native | Effective Mode | Description |
| --- | --- | --- | --- | --- |
| Reset | 1 | 1 | Supervisor + Native | Initial state after reset |
| Trap | 1 | Unchanged | Supervisor + (Native or Legacy) | Hardware transition to Supervisor |
| Software | From GLOBAL_CTRL | From GLOBAL_CTRL | As configured | Control through port F0h |
| User | 0 | 0 | User + Legacy | CPC compatibility |
| User | 0 | 1 | User + Native | Extended operating mode |

**Important:** In Supervisor mode, the `native_mode` bit has no effect.
Native memory and device access mechanisms are always used.

# Memory Organization
<a id="memory-organization"></a>

## Logical and Physical Address Spaces
<a id="logical-and-physical-address-spaces"></a>

- **Physical address space**: 24 bits (16 MB).
- **Z80 logical address space**: 16 bits (64 KB).
- **Logical slots**: The 64 KB logical address space is divided into four
  16 KB slots:
  - **Slot 0**: 0000-3FFF (CPC RAM, base memory)
  - **Slot 1**: 4000-7FFF (CPC ROM, system firmware)
  - **Slot 2**: 8000-BFFF (user extended memory)
  - **Slot 3**: C000-FFFF (supervisor memory, privileged)
- **Bank switching**: An 8-bit page (bank) register maps a 16 KB logical
  slot into the 16 MB physical address space.

  `physical_address ` {bank_reg[7:0], cpu_a[13:0]}=

## MMIO Address Space: HI and LO Concepts
<a id="mmio-address-space-hi-and-lo"></a>

The last 64 KB of the physical address space (addresses
`FF0000h - FFFFFFh`) are reserved for memory-mapped I/O (MMIO).
This address space is logically divided into two regions:

- **`MMIO_HI` (addresses `FF4000h - FFFFFFh`)**: This region is intended
  for **emulating legacy Amstrad CPC devices**. Devices in this region are
  **hard-wired** to their physical addresses (for example, the `Gate Array`
  at `FF7F00h` and the `CRTC` at `FFBC00h`). In Legacy mode, accesses to
  CPC ports (7FXXh, BCXXh, and so on) are translated into direct accesses
  to these fixed MMIO_HI addresses using the full Z80 bus address
  `A[15:0]`.

- **`MMIO_LO` (addresses `FF0000h - FF3FFFh`, 16 KB)**: This region is
  intended for **new Aleste LX system devices** and is accessed through
  the bank-switching mechanism (window). The address space is organized
  into 128 pages of 128 bytes each.

**Important:** A device's MMIO address is part of its architectural
contract. This allows not only the CPU but also other bus masters
(such as the **DMA controller**) to access peripheral devices directly
at their fixed addresses over the high-speed Wishbone bus. This is
critical for performance. However, the MMU is not mapped into this
address space and is accessible only by the CPU.

## MMIO_LO Organization
<a id="mmio-lo-organization"></a>

**Basic principle:** 128 pages × 128 bytes = 16,384 bytes (16 KB).

**Address translation formula:**

```text
physical_address = 0xFF0000 + (MMIO_PAGE << 7) + A[6:0]
```

Where:

- `MMIO_PAGE` is a 7-bit register (values 0-127).
- `A[6:0]` represents the seven least significant CPU address bits
  (port range 00-7Fh).

**MMIO_LO device map:**

| Page | Address Range | Size | Device | Description |
| --- | --- | --- | --- | --- |
| 0 | =FF0000-FF001F= | 32 | PIC Controller | Interrupt controller |
| 0 | =FF0020-FF003F= | 32 | IPC Mailbox | System mailbox |
| 0 | =FF0040-FF005F= | 32 | System Timer | System timer |
| 0 | =FF0060-FF007F= | 32 | RTC Controller | Real-time clock |
| 0 | =FF0080-FF00BF= | 64 | MMU Extension | Extended MMU access |
| 0 | =FF00C0-FF00CF= | 16 | Reserved | Reserved |
| 0 | =FF00D0-FF00DF= | 16 | Reserved | Reserved |
| 0 | =FF00E0-FF00EF= | 16 | Reserved | Reserved |
| 0 | =FF00F0-FF00FF= | 16 | Reserved | Reserved |
| 1 | =FF0080-FF00FF= | 128 | Reserved | Reserved |
| 2 | =FF0100-FF017F= | 128 | Legacy Emulation | Legacy device emulation |
| 4 | =FF0200-FF027F= | 128 | DMA Controller | DMA controller |
| 6 | =FF0300-FF037F= | 128 | Graphics Chip | Graphics chip |
| 8 | =FF0400-FF047F= | 128 | Sound Chip | Sound chip |
| ... | ... | ... | ... | ... |

**Note:** Devices are placed on 32-byte boundaries to simplify address
decoding.

# Control Register System
<a id="control-register-system"></a>

## Control Registers (Native Mode)
<a id="control-registers-native-mode"></a>

These registers are accessible through I/O ports in the F0-FF range.

- **`MMIO_WINDOW` (ports `00h-7Fh`)**: A 128-byte window for accessing
  MMIO_LO.

  - Access: RW, subject to privilege restrictions.
  - Formula:
    `mmio_physical_address ` FF0000h + {MMIO_PAGE[6:0], cpu_a[6:0]}=
  - In User Mode, access is denied when `mmio_userlock`1=.

- **`MMIO_PAGE` (port `F1h`)**: A 7-bit MMIO page-selection register.

  - Access: RW, subject to privilege restrictions.
  - Range: 0-127 (7 bits).
  - In User Mode, access is denied when `mmio_userlock`1=.

- **`SYS_CALL_CMD_PORT` (port `F2h`)**: Port for invoking operating
  system commands.

  - Access: W (always).
  - In Legacy Mode, accesses to `F2XXh` are automatically redirected
    to this port.

- **`GLOBAL_CTRL` (port `F0h`)**: Main operating-mode control register.

| Bit | Group | Purpose |
| --- | --- | --- |
| 0 | Functional | *supervisor_mode*: 1 = Supervisor mode (set by hardware or software). |
| 1 | Functional | *native_mode*: 1 = Native mode, 0 = Legacy mode. |
| 2 | Functional | *supervisor_hook*: 1 = Enable hardware trapping at addresses 0038h/0066h. |
| 3 | Reserved | Reserved for future functionality. |
| 4 | Security | *mmio_user_unlock*: |
|  |  | 1 = Allow direct MMIO access. |
|  |  | 0 = Block access; SysCall only. |
|  |  | *Default: 0.* |
| 5-7 | Reserved | Reserved for future security bits. |

- **`CLOCK_CTRL` (port `F3h`)**: CPU clock control register.

  - Bits 0-3: Bus clock divider used to derive the CPU clock.
  - Access: RW, Supervisor mode only.

- **`SUPER_SLOT` (port `F9h`)**: Selects the active slot set for
  **Supervisor** mode.

- **`USER_SLOT` (port `FBh`)**: Selects the active slot set for **User**
  mode.

- **`BANK_0` (port `FCh`)**: Selects the memory page for slot 0
  (0000-3FFF) in the current slot set.

- **`BANK_1` (port `FDh`)**: Selects the memory page for slot 1
  (4000-7FFF) in the current slot set.

- **`BANK_2` (port `FEh`)**: Selects the memory page for slot 2
  (8000-BFFF) in the current slot set.

- **`BANK_3` (port `FFh`)**: Selects the memory page for slot 3
  (C000-FFFF) in the current slot set.

  - Access to BANK_0-BANK_3: RW, Native/Supervisor modes only.

## Extended MMU Access
<a id="extended-mmu-access"></a>

- **`MMU_EXT` (addresses `FF0080h-FF00BFh`)**: Provides extended access
  to the mapper state.
  - **Access:** RW, CPU only, in Native/Supervisor modes.
  - **Important:** DMA and other bus masters **cannot access** these
    registers.
  - Intended for quickly saving and restoring the complete mapper state.

## Compatibility Registers (Legacy Mode)
<a id="compatibility-registers-legacy-mode"></a>

These registers emulate the Amstrad CPC environment. They are accessed
through ports of the form `XXYYh`.

- **`RMR` / `MMR` (port `7FXXh`)**: CPC memory and graphics control
  registers.
- **`ROM_SEL` (port `DFXXh`)**: Selects the ROM bank for the upper memory
  region (C000-FFFF).
- **`SYSCALL_LEGACY` (port `F200h`)**: Invokes an operating system
  function. Automatically redirected to Native port `F2h`.

# Mode Switching Mechanisms
<a id="mode-switching-mechanisms"></a>

## Software Mode Switching
<a id="software-mode-switching"></a>

Write to the `GLOBAL_CTRL` register (port `F0h`):

`S ← {data[0], data[1]}`

This sets the Supervisor and Native mode bits.

## Hardware Trap to Supervisor Mode
<a id="hardware-trap-to-supervisor-mode"></a>

Entry into privileged mode is performed by hardware when the following
condition is met:

`trap ` (supervisor_hook `= 1) ∧ (M1 signal active) ∧ (address_bus `` 0038h ∨ address_bus `` 0066h)`

## Switching Modes Through Syscall
<a id="switching-modes-through-syscall"></a>

### System Call Protocol
<a id="system-call-protocol"></a>

- Function code: Passed in register A.
- Arguments: Passed in registers. The standard calling convention is:

  - BC — first argument (file handle or device number).
  - DE — second argument (data pointer or size).
  - HL — third argument (buffer pointer or additional parameter).

- Return value: Register A contains the status; HL may contain the
  result.
- Register preservation: The Supervisor system call handler saves and
  restores all registers except those used to return values.

### Example of a Correct System Call
<a id="correct-system-call-example"></a>

```asm
; Prepare arguments for syscall_write (function code 0x02)
LD A, 2              ; A = function code 'write'
LD BC, file_handle   ; BC = first argument: file handle
LD DE, data_size     ; DE = second argument: data size
LD HL, data_buffer   ; HL = third argument: buffer pointer
CALL syscall         ; Invoke the wrapper
; Check the return value in A (0 = success, otherwise error code)
```

### Wrapper Implementation
<a id="wrapper-implementation"></a>

**Native Mode:**

```asm
syscall:
    OUT (F2h), A    ; !!! MAGIC INSTRUCTION !!!
    RET             ; Execution returns here after the syscall completes
```

**Legacy Mode:**

```asm
syscall_legacy:
    OUT (F200h), A  ; !!! MAGIC INSTRUCTION !!!
    RET
```

**Hardware Translation:**

```verilog
if (native_mode == 1 && io_addr == 8'hF2)
    syscall_trigger = 1;
else if (native_mode == 0 && io_addr == 16'hF200)
    syscall_trigger = 1;
```

### Supervisor-Mode Handler
<a id="supervisor-mode-handler"></a>

```asm
Syscall_Dispatcher:
    ; A already contains the function code
    CP 0
    JP Z, Syscall_OpenFile
    CP 1
    JP Z, Syscall_ReadFile
    CP 2
    JP Z, Syscall_WriteFile ; <--- Jump here
    ; ... and so on

Syscall_WriteFile:
    ; Parameters are already in registers:
    ; A=function code, BC=file_handle, HL=buffer, DE=size
    ; The operation can now be performed.
    ; ... processing ...
    RET ; Return from the dispatcher
```

## Exiting Supervisor Mode
<a id="exiting-supervisor-mode"></a>

Exiting Supervisor mode is a **multi-step process** synchronized with
the processor's instruction cycle:

1. **Initiating the exit**: Kernel code executes an `OUT` instruction
   with data `0` to the `GLOBAL_CTRL` register.

   #+begin_src asm
   LD A, 00000000b  ; supervisor`0, native`0 or 1
   OUT (F0h), A     ; Write to GLOBAL_CTRL
   #+end_src

2. **Detection**: The hardware detects the write and sets the internal
   flag `EXIT_SUPERVISOR_PENDING ` 1=.

3. **RETN execution**: The next instruction (usually `RETN`) executes
   entirely in Supervisor mode.

4. **M1 synchronization**: The hardware waits for the **next** `M1` bus
   cycle.

5. **Mode switch**: When `M1` becomes active, `supervisor_mode` is cleared.

6. **Instruction fetch in User Mode**: The instruction at the return
   address is fetched in User mode.

**Result:** The `RETN` instruction executes in Supervisor mode, while the
following instruction executes in User mode.

## Determining the Active Slot Set
<a id="determining-the-active-slot-set"></a>

The active slot set depends on the current privilege mode:

`current_slot ` (supervisor_mode `= 1) ? SUPER_SLOT : USER_SLOT`

## Mapper Operation Algorithm
<a id="mapper-operation-algorithm"></a>

Accesses to the `BANK_0` through `BANK_3` registers are redirected to
one of the 16 internal mapper registers, depending on the active slot
set.

```cpp
void write_to_bank_register(uint8_t address_low_bits, uint8_t data) {
    page_index = (current_slot * 4) + (address_low_bits & 0b00000011);
    internal_mapper_registers[page_index] = data;
}
```

## Access Security Policy
<a id="access-security-policy"></a>

- **User Native Mode**: When `mmio_userlock`1=, access to ports 00-7F,
  F1, F3, F9, and FB-FF is prohibited. Only F2 (SysCall) remains
  available.

- **User Legacy Mode**: When `mmio_userlock`1=, F200 (SysCall) and all
  standard CPC ports remain available.

- **Supervisor Mode**: Access is always permitted.

## System Call for Unlocking MMIO Access
<a id="system-call-for-unlocking-mmio-access"></a>

`SYS_MMIO_ACCESS_REQUEST` (function code: `0xFE`)

- **Purpose:** Request permission for direct MMIO access.
- **Input:** `A ` 0xFE`, `BC ` 0x0001` (MMIO access request flag).
- **Output:** `A ` result code= (0: allowed, 1: denied).
- **Behavior:** The kernel verifies the application's digital signature.
  If verification succeeds, it sets `mmio_userlock ` 0=.

# Detailed Information on Native-Mode MMU Registers
<a id="detailed-information-on-native-mode-mmu-registers"></a>

## GLOBAL_CTRL Register
<a id="global-ctrl-register"></a>

The complete register table is provided in Section 4.1.

## Extended Mapper Access
<a id="extended-mapper-access"></a>

This interface is intended for system use to quickly save and restore
the complete mapper state.

| WB Address | Slot | CPU Page | Purpose |
| --- | --- | --- | --- |
| FF00E0 | 0 | 0000 | Slot 0, bank for 0000-3FFF |
| FF00E1 | 0 | 4000 | Slot 0, bank for 4000-7FFF |
| FF00E2 | 0 | 8000 | Slot 0, bank for 8000-BFFF |
| FF00E3 | 0 | C000 | Slot 0, bank for C000-FFFF |
| FF00E4 | 1 | 0000 | Slot 1, bank for 0000-3FFF |
| FF00E5 | 1 | 4000 | Slot 1, bank for 4000-7FFF |
| FF00E6 | 1 | 8000 | Slot 1, bank for 8000-BFFF |
| FF00E7 | 1 | C000 | Slot 1, bank for C000-FFFF |
| FF00E8 | 2 | 0000 | Slot 2, bank for 0000-3FFF |
| FF00E9 | 2 | 4000 | Slot 2, bank for 4000-7FFF |
| FF00EA | 2 | 8000 | Slot 2, bank for 8000-BFFF |
| FF00EB | 2 | C000 | Slot 2, bank for C000-FFFF |
| FF00EC | 3 | 0000 | Slot 3, bank for 0000-3FFF |
| FF00ED | 3 | 4000 | Slot 3, bank for 4000-7FFF |
| FF00EE | 3 | 8000 | Slot 3, bank for 8000-BFFF |
| FF00EF | 3 | C000 | Slot 3, bank for C000-FFFF |

**Important:** These registers are accessible only by the CPU in
Native/Supervisor modes. DMA and other bus masters cannot access them.

# IPC Mailbox
<a id="ipc-mailbox"></a>

**Purpose:** To provide extremely fast, deterministic, and secure
communication of control commands and notifications between the
**Supervisor (kernel)** and **drivers** running in kernel space.

**Address:** `FF0020h-FF003Fh` (32 bytes).

**Hardware implementation:** The mailbox consists of a set of registers:

- **`MAILBOX_CMD`**: The driver writes an operation code here (e.g.,
  `SND_BUF_EMPTY` or `DSK_IO_DONE`).
- **`MAILBOX_DATA_**`*: Command parameters (channel number, address, etc.).
- **`MAILBOX_STATUS`**: `FULL` (message unread) and `ACK` (processing
  acknowledged) bits.
- **`MAILBOX_INT_CTRL`**: Controls interrupts triggered by message
  reception.

**Protocol:** The driver writes the command and its data. The hardware
sets `FULL` and generates an interrupt for the kernel, if enabled.
After processing the message, the kernel clears the `FULL` flag.

# Mathematical Model
<a id="mathematical-model"></a>

## Address Translation
<a id="address-translation"></a>

Logical-to-physical address translation depends on the current operating
modes.

```text
physical_address =
    if (supervisor_mode == 1) or (native_mode == 1) then
        // Native or Supervisor mode: use the mapper
        { internal_mapper_registers[current_slot * 4 + page_number], cpu_a[13:0] }
    else
        // Legacy mode: use CPC mapping
        legacy_cpc_mapping(cpu_a, RMR, MMR)
```

## State Machine
<a id="state-machine"></a>

System state transitions can be described as follows:

```text
S(t+1) =
    if trap_condition then
        {1, S(t).native_mode} // Enter Supervisor; Native mode unchanged
    else if exit_supervisor_pending & next_M1_cycle then
        {0, S(t).native_mode} // Exit to User; Native mode unchanged
    else if io_write_to_F0h then
        {data[0], data[1]}    // Software sets both modes
    else
        S(t)                  // State remains unchanged
```

# Register and Address Table
<a id="register-and-address-table"></a>

| Device / Description | RW | Legacy IO Address | Legacy WB Address | Native IO Address | Native WB Address | Size | CPU Access | DMA Access |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| *MMIO_WINDOW* | RW | - | - | 00-7Fh | FF0000+{PAGE, ADDR[6:0]} | 128 | RW* | R* |
| *GLOBAL_CTRL* | RW | - | - | F0h | - | 1 | RW* | - |
| *MMIO_PAGE* | RW | - | - | F1h | - | 1 | RW* | - |
| *SYSCALL* | W | F200h | FFF200h | F2h | - | 1 | W | - |
| *CLOCK_CTRL* | RW | - | - | F3h | - | 1 | RW (Supervisor) | - |
| *SUPER_SLOT* | RW | - | - | F9h | - | 1 | RW* | - |
| *USER_SLOT* | RW | - | - | FBh | - | 1 | RW* | - |
| *BANK_0* | RW | - | - | FCh | - | 1 | RW* | - |
| *BANK_1* | RW | - | - | FDh | - | 1 | RW* | - |
| *BANK_2* | RW | - | - | FEh | - | 1 | RW* | - |
| *BANK_3* | RW | - | - | FFh | - | 1 | RW* | - |
| *MMU_EXT* | RW | - | - | Via window | FF0080h-FF00BFh | 64 | RW (CPU only) | - |
| *PIC Controller* | RW | - | - | Via window | FF0000h-FF001Fh | 32 | RW | RW |
| *IPC Mailbox* | RW | - | - | Via window | FF0020h-FF003Fh | 32 | RW | - |
| *System Timer* | RW | - | - | Via window | FF0040h-FF005Fh | 32 | RW | - |
| *RTC Controller* | RW | - | - | Via window | FF0060h-FF007Fh | 32 | RW | - |
| *Legacy Emulation* | RW | - | - | Via window | FF0100h-FF017Fh | 128 | RW | RW |
| *DMA Controller* | RW | - | - | Via window | FF0200h-FF027Fh | 128 | RW | - |
| *Graphics Chip* | RW | - | - | Via window | FF0300h-FF037Fh | 128 | RW | RW |
| *Sound Chip* | RW | - | - | Via window | FF0400h-FF047Fh | 128 | RW | RW |
| *Gate Array* | W | 7FXXh | FF7FXXh | - | - | - | W | W |
| *CRTC 6845* | RW | BCXXh/BDXXh | FFBCXXh/FFBDXXh | - | - | - | RW | RW |
| *Upper ROM Select* | W | DFXXh | FFDFXXh | - | - | - | W | - |
| *PPI 8255* | RW | F4XXh-F7XXh | FFF4XXh-FFF7XXh | - | - | - | RW | RW |

**Legend:**

- **RW** — Read/write access.
- *RW** — Read/write access subject to privilege restrictions.
- *R** — Read access subject to privilege restrictions.
- **CPU only** — Accessible only by the CPU; not accessible through the
  Wishbone bus.
- Certain registers are accessible only in Native/Supervisor modes.

# Legacy MMU Registers (CPC Compatibility Only)
<a id="legacy-mmu-registers-cpc-compatibility-only"></a>

## Register RMR (Control Interrupt Counter, ROM Mapping and Graphics Mode)
<a id="register-rmr-control-interrupt-counter-rom-mapping-and-graphics-mode"></a>

This shared register controls the CPC graphics mode and ROM
configuration.

| Bit | Action |
| --- | --- |
| 7 | Must be 1 |
| 6 | Must be 0 |
| 5 | Must be 0 on Plus machines with the ASIC unlocked |
| 4 | irq_control — interrupt generation control |
| 3 | upper_rom — 1 = disable upper ROM area; 0 = enable upper ROM |
| 2 | lower_rom — 1 = disable lower ROM area; 0 = enable lower ROM |
| 1-0 | graphic_mode — graphics mode selection |

- `upper_rom` starts at C000.
- `lower_rom` starts at 0000.
- `graphic_mode` determines the graphics mode (inherited from the CPC).

## Upper ROM Select (DFXX)
<a id="upper-rom-select-dfxx"></a>

An 8-bit register that selects a 16 KB memory bank at addresses
C000-FFFF when `upper_rom` is 0.

## Register MMR (RAM Memory Mapping)
<a id="register-mmr-ram-memory-mapping"></a>

| Bit | Purpose |
| --- | --- |
| 7 | Must be 1 |
| 6 | Must be 1 |
| 5-3 | *bbb* — Upper bank-number bits. Select a 64 KB block in extended memory. |
| 2-0 | *ccc* — Configuration determining the lower bank-number bits. |

**CPC 128 Memory Map**

| Address | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C000-FFFF | RAM_3 | RAM_7 | RAM_7 | RAM_7 | RAM_3 | RAM_3 | RAM_3 | RAM_3 |
| 8000-BFFF | RAM_2 | RAM_2 | RAM_6 | RAM_2 | RAM_2 | RAM_2 | RAM_2 | RAM_2 |
| 4000-7FFF | RAM_1 | RAM_1 | RAM_5 | RAM_3 | RAM_4 | RAM_5 | RAM_6 | RAM_7 |
| 0000-3FFF | RAM_0 | RAM_0 | RAM_4 | RAM_0 | RAM_0 | RAM_0 | RAM_0 | RAM_0 |

**CPC 512 KB Memory Map**

| Address | ccc=0 | ccc=1 | ccc=2 | ccc=3 | ccc=4 | ccc=5 | ccc=6 | ccc=7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0000-3FFF | 0 | 0 | bbb*4 + 0 | 0 | 0 | 0 | 0 | 0 |
| 4000-7FFF | 1 | 1 | bbb*4 + 1 | 3 | bbb*4 + 0 | bbb*4 + 1 | bbb*4 + 2 | bbb*4 + 3 |
| 8000-BFFF | 2 | 2 | bbb*4 + 2 | 2 | 2 | 2 | 2 | 2 |
| C000-FFFF | 3 | bbb*4 + 3 | bbb*4 + 3 | bbb*4 + 3 | 3 | 3 | 3 | 3 |

## CPU Clock Control
<a id="cpu-clock-control"></a>

| Bit | Purpose |
| --- | --- |
| 7-4 | Reserved |
| 3-0 | *dddd* — Bus clock divider used to derive the CPU clock. |

The `CLOCK_CTRL` register (F3h) is accessible only in Supervisor mode.

# TAG-Based Wishbone Addressing
<a id="tag-based-wishbone-addressing"></a>

## Overview
<a id="overview"></a>

The FPGA implementation uses TAG-based addressing on the Wishbone bus
to simplify address decoding:

- **Master devices** output raw addresses only.
- **Slave devices** use 3-bit TAG signals to identify the address-space
  type.
- The **interconnect** performs centralized address-to-TAG translation.

## Address-to-TAG Mapping
<a id="address-to-tag-mapping"></a>

```verilog
// Address regions
logic mmio_space, mmio_4000_FFFF, mmio_native, mmio_legacy;
assign mmio_space     = (wb_adr_i[23:16] == 8'hFF);
assign mmio_4000_FFFF = (wb_adr_i[15] || wb_adr_i[14]);   // 0x4000-0xFFFF
assign mmio_native    = mmio_space && !mmio_4000_FFFF;    // 0xFF0000-0xFF3FFF
assign mmio_legacy    = mmio_space &&  mmio_4000_FFFF;    // 0xFF4000-0xFFFFFF

// 3-bit TAG encoding — mutually exclusive
always_comb begin
    wb_tag_o = 3'b000;
    if (mmio_native)       wb_tag_o = 3'b010;  // Native IO
    else if (mmio_legacy)  wb_tag_o = 3'b100;  // Legacy IO
    else                   wb_tag_o = 3'b001;  // Memory space
end
```

## TAG Encoding
<a id="tag-encoding"></a>

```text
TAG[2:0] Encoding:
000 - Reserved
001 - Memory space        (0x000000-0xFEFFFF) - Main memory
010 - Native IO Space     (0xFF0000-0xFF3FFF) - New devices
100 - Legacy IO Space     (0xFF4000-0xFFFFFF) - Compatibility devices
```

## Advantages of This Approach
<a id="advantages-of-this-approach"></a>

- **Fast decoding**: Slave devices need to check only the TAG bits.
- **Scalability**: New address-space types can be added easily.
- **Compatibility**: CPC legacy addressing is fully preserved.

# Reset State
<a id="reset-state"></a>

| Register | Address | Reset Value | Description |
| --- | --- | --- | --- |
| =GLOBAL_CTRL= | F0h | =00000110b= | supervisor=1, native=1, mmio_userlock=0 |
| =MMIO_PAGE= | F1h | =00000000b= | MMIO page 0 |
| =SUPER_SLOT= | F9h | =00000000b= | Slot set 0 for Supervisor |
| =USER_SLOT= | FBh | =00000000b= | Slot set 0 for User |
| =BANK_0=-=BANK_3= | FCh-FFh | =00000000b= | Memory banks set to 0 |
| =CLOCK_CTRL= | F3h | =00000111b= | Clock divider (implementation-dependent) |

# Code Examples for Developers
<a id="code-examples-for-developers"></a>

## System Initialization After Reset
<a id="system-initialization-after-reset"></a>

```asm
start:
    ; The system starts in Supervisor + Native mode

    ; Configure memory banks for Supervisor
    LD A, 0
    OUT (F9h), A           ; SUPER_SLOT = 0

    ; Configure memory banks for User
    OUT (FBh), A           ; USER_SLOT = 0

    ; Configure CPU clock (Supervisor only)
    LD A, 00000111b        ; Clock divider
    OUT (F3h), A           ; CLOCK_CTRL

    ; Switch to User Native Mode
    LD A, 00000010b        ; supervisor=0, native=1
    OUT (F0h), A           ; GLOBAL_CTRL

    ; Now running in User Native Mode
    ; ...
```

## Requesting MMIO Access
<a id="requesting-mmio-access"></a>

```asm
request_mmio_access:
    LD A, 0FEh             ; SYS_MMIO_ACCESS_REQUEST
    LD BC, 0001h           ; MMIO access request flag
    CALL syscall           ; Use the wrapper
    OR A                   ; Check the result
    RET NZ                 ; Error if A != 0
    ; mmio_userlock=0; MMIO access is now permitted
    RET
```

## Hardware Trap Handler
<a id="hardware-trap-handler"></a>

```asm
    ; Configure the handler in Supervisor mode
    LD A, 00000111b        ; supervisor=1, native=1, trap_enabled=1
    OUT (F0h), A           ; GLOBAL_CTRL

    ; Accesses to 0038h/0066h will now trigger a hardware
    ; transition to Supervisor mode
```

## Saving and Restoring Mapper State
<a id="saving-and-restoring-mapper-state"></a>

```asm
save_mapper_state:
    ; Save mapper state through MMU_EXT
    LD HL, save_buffer
    LD BC, 0040h           ; 64 bytes
    LD A, 0                ; MMIO page 0
    OUT (F1h), A           ; MMIO_PAGE
    LD A, 80h              ; Start of the MMU_EXT region
    LD D, 16               ; 16 registers
.save_loop:
    OUT (A), A             ; Access through MMIO_WINDOW
    IN A, (00h)            ; (pseudocode; implementation-dependent)
    LD (HL), A
    INC HL
    INC A
    DEC D
    JR NZ, .save_loop
    RET
```

# Architectural Extension Capabilities: Dual Device Access
<a id="architectural-extension-capabilities-dual-device-access"></a>

## Current Access Architecture
<a id="current-access-architecture"></a>

The current implementation provides a **single unified access mechanism**
for peripheral devices through MMIO_WINDOW:

```text
User application → MMIO_WINDOW (00-7Fh) → MMIO_PAGE → Device in MMIO_LO
```

This approach is **uniform** and works for all devices.

## Theoretical Possibility: Dual Access
<a id="theoretical-possibility-dual-access"></a>

The architecture **could theoretically support** dual access to selected
devices.

### Through MMIO_WINDOW (Standard Path)
<a id="through-mmio-window-standard-path"></a>

```asm
; Standard access through the window
LD A, page_number
OUT (F1h), A          ; MMIO_PAGE = device page
LD A, value
OUT (reg_offset), A   ; Write through MMIO_WINDOW
```

### Direct Access Through Fixed Ports (Theoretical)
<a id="direct-access-through-fixed-ports-theoretical"></a>

```asm
; Theoretical direct access (if implemented)
LD A, value
OUT (C0h), A          ; Direct access to the device
```

## How It Could Work
<a id="how-it-could-work"></a>

**The last MMIO_LO page (page 127)** could be mapped into the *upper
128 bytes of the I/O port space*:

```text
Theoretical address mapping:
Ports 80h-FFh → MMIO_LO page 127 (FF8080h-FFFFFFh)
Exception: Ports F0h-FFh are already occupied by system registers
```

**Theoretical implementation:**

```verilog
// Theoretical dual-access implementation
always_comb begin
    if (cpu_io_write && cpu_addr[7] == 1'b1) begin
        // Direct access through ports 80h-FFh
        if (cpu_addr[7:0] >= 8'h80 && cpu_addr[7:0] <= 8'hEF) begin
            // Map to MMIO_LO page 127
            mmio_physical_addr = 24'hFF8000 + {7'd127, cpu_addr[6:0]};
            direct_access = 1'b1;
        end
    end
end
```

## Why This Is NOT Implemented in the Current Architecture
<a id="why-this-is-not-implemented-in-the-current-architecture"></a>

1. **No practical need**:
   - MMIO_WINDOW access is sufficiently fast (only 1-2 additional
     instructions).
   - Address decoding is simpler.
   - A unified approach is used for all devices.

2. **Limited port space**:
   - Ports 80h-FFh may be used by legacy devices.
   - There is a risk of conflicts with the existing CPC legacy
     environment.

3. **Architectural simplicity**:
   - One access mechanism means fewer errors.
   - The design is easier for developers to understand.
   - Documentation and debugging are simpler.

4. **Development priorities**:
   - The MMU and system registers require exclusive CPU-only access.
   - Peripheral devices work well through MMIO_WINDOW.
   - No drivers or software currently require this optimized access.

## When This Could Be Useful (Theoretically)
<a id="when-this-could-be-useful-theoretically"></a>

1. **Latency-critical devices**:
   - Real-time timers.
   - Interrupt controllers.
   - DMA controller (although it controls the bus).

2. **Frequently accessed registers**:
   - Device status registers.
   - Fast data exchange buffers.

3. **Backward compatibility**:
   - Emulating devices with fixed I/O ports.

## Implementation Details for Future Versions
<a id="implementation-details-for-future-versions"></a>

If dual access becomes necessary in the future, it could be implemented
as follows:

```verilog
module dual_access_device (
    input wire clk,
    input wire rst_n,
    // Standard MMIO access
    input wire [23:0] wb_adr_i,
    input wire [7:0] wb_dat_i,
    input wire wb_we_i,
    input wire wb_stb_i,
    // Direct CPU access (theoretical)
    input wire [7:0] cpu_io_addr,
    input wire [7:0] cpu_io_data,
    input wire cpu_io_write,
    // Access mode selection
    input wire direct_access_enabled
);

// Device registers
reg [7:0] device_regs[0:15];

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        // Reset
    end else begin
        // Priority: direct access > MMIO access
        if (direct_access_enabled && cpu_io_write &&
            cpu_io_addr[7:0] == DEVICE_BASE_PORT) begin
            // Direct access through the port
            device_regs[cpu_io_addr[3:0]] <= cpu_io_data;
        end else if (wb_stb_i && wb_we_i &&
                   wb_adr_i[23:16] == 8'hFF &&
                   wb_adr_i[15:14] == 2'b00) begin
            // Standard MMIO access
            device_regs[wb_adr_i[5:2]] <= wb_dat_i;
        end
    end
end
endmodule
```

## Future Architectural Development
<a id="future-architectural-development"></a>

The current architecture **leaves room** for direct access to be added
in the future:

| Version | Device Access | Comment |
| --- | --- | --- |
| Aleste LX v1.0 | MMIO_WINDOW only | Current implementation |
| Aleste LX v2.0 | + Direct access for CPU-critical devices | If required |
| Aleste LX v3.0 | + Direct access for selected devices | At the community's discretion |

The decision to implement direct access will be based on:

- Requests from community developers.
- Performance analysis of real-world applications.
- Backward compatibility with existing software.

---

## Recommendations for Peripheral Developers
<a id="recommendations-for-peripheral-developers"></a>

1. **Always design** devices to be accessed through MMIO_WINDOW.
2. **Do not rely** on direct access through I/O ports.
3. **If performance is critical**:
   - Optimize access algorithms.
   - Use DMA for data transfers.
   - Cache frequently used values.
4. **For compatibility** with legacy devices:
   - Use the emulation mechanism in MMIO_HI.
   - Do not occupy ports that may be required by the legacy environment.

# Summary of Key Changes
<a id="summary-of-key-changes"></a>

1. **Updated control ports**: F0-FF instead of D0-DF.

   - `GLOBAL_CTRL`: F0h (formerly D7h).
   - `MMIO_PAGE`: F1h (formerly D3h).
   - `SYSCALL`: F2h (formerly D4h).
   - `CLOCK_CTRL`: F3h (new).
   - `SUPER_SLOT`: F9h (formerly D9h).
   - `USER_SLOT`: FBh (formerly DBh).
   - `BANK_0-3`: FCh-FFh (formerly DCh-DFh).

2. **Corrected GLOBAL_CTRL bit map**:

   - Bit 0: supervisor_mode (formerly native_mode).
   - Bit 1: native_mode (formerly supervisor_mode).

3. **Added TAG-based addressing**: 3-bit TAG signals for Wishbone.

4. **Clearer access separation**:

   - MMU_EXT is accessible only by the CPU.
   - CLOCK_CTRL is accessible only in Supervisor mode.

5. **Added code examples** and a reset-state table.

6. **Added peripheral developer recommendations** and a section on the
   platform's future development.
