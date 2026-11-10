# LX Minimal Supervisor BIOS — example

**Status:** example / test code. **NOT normative. NOT RTL.**
**Purpose:** demonstrate Supervisor entry, syscall dispatch, and exit
in Verilator.
**See also:** `lx_mmu.md` §4 (control registers), §5.3 (syscall),
§5.4 (exit), §7 (reset state).

> **Note:** This is a **minimal example**, not the full LX BIOS. The full
> BIOS is in the `aleste-xi-bios` repository. This file exists only to
> show the Supervisor/syscall/exit mechanism on the current RTL
> (`gen_rtl`).

> **⚠ Spec:** Earlier versions of this example used the old `D0–DF` port
> map (`GLOBAL_CTRL=0xD7`, `BANK_0–3=0xDC–0xDF`). The current RTL
> (`gen_rtl`) uses `F0–FF` (`GLOBAL_CTRL=0xF0`, `BANK_0–3=0xFC–0xFF`,
> `SUPER_SLOT=0xFA`, `USER_SLOT=0xFB`). This example has been updated
> to match the RTL.

---

## What this minimal BIOS does

1. **Initialization** — switch to Native + Supervisor mode, set up
   supervisor slot, enable trap.
2. **Three syscalls:**
   - `00` — set `GLOBAL_CTRL` (value in `C'`).
   - `01` — set user bank (slot in `B'`, bank in `C'`).
   - `02` — add two numbers (`D' + E' = A`).
3. **Register preservation** — uses only the alternate registers
   (`AF'`, `BC'`, `DE'`, `HL'`).
4. **Correct return to user code** via `RETN`.

### Calling from user code (Verilator test)

```asm
ld a, 0x02    ; function: add
ld d, 5       ; first number
ld e, 3       ; second number
call syscall  ; result in A
```

---

## Source

```asm
        ;#################################################
        ;# Minimal Supervisor BIOS for Aleste LX Testing #
        ;# Entry point: 0x0000 (Cold Boot)               #
        ;# SysCall Entry: 0x0038                        #
        ;# NMI Entry: 0x0066 (if enabled)                #
        ;# Uses: AF', BC', DE', HL' only                #
        ;# RTL: gen_rtl (F0-FF port map)                #
        ;#################################################

        .org 0x0000

        ; --- Cold Boot Vector ---
        di
        ld sp, 0xFFF0          ; Supervisor stack in slot 3
        jp supervisor_init

        .org 0x0038
        ; --- SysCall/Trap Vector ---
        jp syscall_dispatcher

        .org 0x0066
        ; --- NMI Vector ---
        retn                    ; Minimal NMI handler

        ; --- Supervisor Initialization ---
supervisor_init:
        ; Set Native Mode + Supervisor Mode
        ld a, 0b00000011        ; bit0=supervisor, bit1=native
        out (0xF0), a           ; GLOBAL_CTRL (RTL: F0h)

        ; Set up Supervisor Slot (Slot 3: C000-FFFF)
        ld a, 0x03              ; slot 3 for page 3
        out (0xFA), a           ; SUPER_SLOT (RTL: FAh)
        ld a, 0x03              ; bank 3
        out (0xFF), a           ; BANK_3 (RTL: FFh)

        ; Enable supervisor hook for traps
        ld a, 0b00000111        ; bit0=supervisor, bit1=native, bit2=hook
        out (0xF0), a           ; GLOBAL_CTRL

        ; --- Return to User Mode ---
        ; Simulate exit sequence
        xor a                   ; A=0 to exit supervisor
        out (0xF0), a           ; Initiate exit (completes after RETN)
        retn                    ; Return to user code

        ; --- SysCall Dispatcher ---
syscall_dispatcher:
        ex af, af'              ; Switch to alt registers
        exx

        ; Dispatch based on function code in A'
        cp 0x00
        jp z, sys_set_control   ; Set GLOBAL_CTRL
        cp 0x01
        jp z, sys_set_userbank  ; Set USER_SLOT bank
        cp 0x02
        jp z, sys_add_numbers   ; Add two numbers

        ; Unknown function - return error
        ld a, 0xFF
        jp syscall_return

        ; --- Function 00: Set GLOBAL_CTRL ---
sys_set_control:
        ; Value in C'
        ld a, c'
        out (0xF0), a           ; GLOBAL_CTRL (RTL: F0h)
        ld a, 0x00              ; Success
        jp syscall_return

        ; --- Function 01: Set User Bank ---
sys_set_userbank:
        ; Bank number in C', slot in B'
        ld a, b'
        cp 0x00
        jr z, set_bank0
        cp 0x01
        jr z, set_bank1
        cp 0x02
        jr z, set_bank2
        cp 0x03
        jr z, set_bank3
        ld a, 0xFE              ; Invalid slot error
        jp syscall_return

set_bank0:
        ld a, c'
        out (0xFC), a           ; BANK_0 (RTL: FCh)
        jr success
set_bank1:
        ld a, c'
        out (0xFD), a           ; BANK_1 (RTL: FDh)
        jr success
set_bank2:
        ld a, c'
        out (0xFE), a           ; BANK_2 (RTL: FEh)
        jr success
set_bank3:
        ld a, c'
        out (0xFF), a           ; BANK_3 (RTL: FFh)
success:
        ld a, 0x00              ; Success

        ; --- Function 02: Add Numbers ---
sys_add_numbers:
        ; Numbers in D' and E'
        ld a, d'
        add a, e'
        ; Result in A

        ; --- Common Return Path ---
syscall_return:
        ; Return value in A
        exx
        ex af, af'              ; Restore main registers
        retn                    ; Return to user code (M1 sync)

        .end
```

---

## Binary image (updated for RTL)

```
F3 31 F0 FF C3 1A 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 C3 38 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
ED 45 3E 03 D3 F0 3E 03 D3 FA 3E 03 D3 FF 3E 07
D3 F0 AF D3 F0 ED 45 08 D9 F5 78 B9 C2 80 00 F1
3D CA 90 00 3D CA A0 00 3D CA B0 00 3E FE C3 D0
00 F1 79 D3 F0 3E 00 C3 D0 00 F1 79 D3 FC 18 F6
F1 79 D3 FD 18 F0 F1 79 D3 FE 18 EA F1 79 D3 FF
18 E4 3E 00 C3 D0 00 7A 83 C3 D0 00 D9 08 ED 4D
```

> **Note:** The binary image above is **not verified** — the source
> was updated for the RTL port map (`F0`/`FA`/`FC–FF`), but the hex
> dump was not reassembled. Reassemble with your assembler of choice
> before use.

---

## Differences from the previous version

| Item | Old (D0–DF) | New (RTL) |
|---|---|---|
| `GLOBAL_CTRL` | `0xD7` | `0xF0` |
| `SUPER_SLOT` | (not used) | `0xFA` |
| `BANK_0` | `0xDC` | `0xFC` |
| `BANK_1` | `0xDD` | `0xFD` |
| `BANK_2` | `0xDE` | `0xFE` |
| `BANK_3` | `0xDF` | `0xFF` |
| Return | `RETI` | `RETN` |

> **⚠ Spec:** The old example wrote `BANK_3` (`0xDF`) to set the
> supervisor slot. In the RTL, `SUPER_SLOT` is a separate register at
> `0xFA`; `BANK_3` (`0xFF`) only sets the bank for slot 3. The new
> example writes both: `SUPER_SLOT = 0x03` and `BANK_3 = 0x03`.

---

*End of document.*
