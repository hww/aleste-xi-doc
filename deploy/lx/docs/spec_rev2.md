# Aleste LX —  Lean eXtreme FPGA Architecture

## Memory Management and Expansion System

**Architecture Specification — revised and annotated draft (rev. 2)**

| | |
|---|---|
| Original author | h2w |
| This revision | Annotated review draft, prepared for author review |
| Date | 2026-11-06 |
| Base document | `aleste-xi_en.org` (Aleste LX architecture specification) |
| Compared against | MiSTer implementation document — **known only through the summary supplied with the request** (see §0.4) |
| Language / format | English / Markdown |

**TODO**

Исправленная и расширенная спецификация лежит в файле aleste-lx_spec_rev2.md: примерно 1470 строк, английский, Markdown. В ней 28 исправлений, 46 вопросов к вам и 10 расхождений с MiSTer.

Документ реализации MiSTer я не видел. Все расхождения построены только на вашем перечне: страницы MMIO, порт FAh, и отсутствие Mailbox, TAG, mmio_userlock, supervisor_hook и syscall 0xFE. Всё, что в перечне не упомянуто, в таблицах помечено «not stated» и считается совпадающим со спецификацией. Эти ячейки стоит проверить.

Как устроены пометки. Все они оформлены цитатами с ID в первой строке, так что их находит grep -n '^> \*\*\[Q'.

[E##] — ошибка в исходнике; исправление уже внесено в текст.
[Q##] — вопрос к вам. Рядом всегда указано рабочее допущение, чтобы текст читался дальше.
[D##] — расхождение с реализацией MiSTer.
Всё, что добавил я сам, а не взял из исходника, подписано как Proposal или Working assumption.
В приложениях A–C автоматически собраны индексы ошибок, вопросов и расхождений. Приложение D — бывший «Summary of Key Changes» (старые номера портов).

Главные проблемы исходника (полный список в §0.3):

Формула {bank_reg[7:0], A[13:0]} даёт 22 бита (4 МБ), а не 24 (E07, Q05).
Сброс GLOBAL_CTRL = 00000110b противоречит собственной карте битов, у бита блокировки перевёрнута полярность, а выход записью 0 молча отключает hook (E03, E04, E21).
Не определено, как syscall передаёт управление супервизору, какой именно M1 завершает выход из supervisor, и где лежит адрес возврата (Q24, Q28, Q22).
Возможная дыра в привилегиях: пользователь может писать GLOBAL_CTRL, а unlock фактически даёт всё, включая DMA (Q01, Q15, Q33).
Адреса MMU_EXT противоречат сами себе: FF0080–BF в карте устройств и FF00E0–EF в таблице регистров (E16, Q19).
Порты CPC с A[15:14]=00 попадают в MMIO_LO (E10, Q08).
OUT (F200h),A — не существующая инструкция Z80, а её рабочая замена портит BC (E18, Q27).
Пример сохранения состояния маппера в исходнике не ассемблируется (E24).

Расхождения с MiSTer (§17): страницы MMIO назначены разным устройствам (DMA и graphics на странице 6 против DMA на странице 4 в спеке), supervisor-слот на FAh, и отсутствуют lock, hook, mailbox, TAG и 0xFE. Отдельно спрошено, как в MiSTer ядро получает управление без hook (D09) и что в MiSTer значит отсутствие lock — всё открыто или всё закрыто (D10).

Я переименовал термины: «slot» в смысле 16 КБ окна стал «window» (W0–W3), «slot set» оставлен. Имена регистров (SUPER_SLOT и т.д.) не менял. Таблица «Dual Access» сокращена до справочного приложения, а её Verilog с неверными адресами убран (E27, E28).

Полностью за пределами того, что я мог вывести из исходника: регистры PIC, Timer, RTC, DMA, Graphics, Sound и Legacy Emulation нигде не описаны (Q11). Формулу делителя CLOCK_CTRL я просто угадал и честно пометил как догадку (Q42).

**Contents**

- [0. How to Read This Document](#0-how-to-read-this-document)
- [1. Introduction and Design Principles](#1-introduction-and-design-principles)
- [2. System State and Operating Modes](#2-system-state-and-operating-modes)
- [3. Address Spaces and Memory Organisation](#3-address-spaces-and-memory-organisation)
- [4. MMIO_LO — Device Space for Native Mode](#4-mmiolo--device-space-for-native-mode)
- [5. I/O Port Map and Control Registers (Native Mode)](#5-io-port-map-and-control-registers-native-mode)
- [6. Memory Mapper](#6-memory-mapper)
- [7. Mode Switching](#7-mode-switching)
- [8. Security Model](#8-security-model)
- [9. IPC Mailbox](#9-ipc-mailbox)
- [10. Legacy (CPC) Compatibility](#10-legacy-cpc-compatibility)
- [11. CPU Clock Control](#11-cpu-clock-control)
- [12. TAG-Based Wishbone Addressing](#12-tag-based-wishbone-addressing)
- [13. Register and Address Summary](#13-register-and-address-summary)
- [14. Reset State](#14-reset-state)
- [15. Code Examples](#15-code-examples)
- [16. Informative Annex: Direct Port Access to MMIO_LO Page 127 (not implemented)](#16-informative-annex-direct-port-access-to-mmiolo-page-127-not-implemented)
- [17. MiSTer Implementation — Divergence Summary](#17-mister-implementation--divergence-summary)
- [Appendix A. Index of Errata](#appendix-a-index-of-errata)
- [Appendix B. Index of Open Questions](#appendix-b-index-of-open-questions)
- [Appendix C. Index of MiSTer Divergences](#appendix-c-index-of-mister-divergences)
- [Appendix D. Historical Port Renames (from the original "Summary of Key Changes")](#appendix-d-historical-port-renames-from-the-original-summary-of-key-changes)

---

## 0. How to Read This Document

### 0.1 What was done to the original

- Normative text was corrected where the original contradicts itself or is technically impossible. Every such correction is marked with an **erratum** (`[E##]`).
- Missing detail was added (register tables, access matrices, cycle-level sequences, ABI tables). Anything that is **my proposal and not in the original** is labelled *Proposal* or *Working assumption*, so it can be accepted or thrown away without digging.
- Open points are marked as **questions** (`[Q##]`). Each question carries a working assumption so the text stays readable until you answer.
- Every place where the MiSTer implementation differs from this specification is marked as a **divergence** (`[D##]`).
- Structure was reorganised: the original "Summary of Key Changes" became a historical appendix (Appendix D); the "Dual Device Access" chapter was condensed into a non-normative annex (§16).

### 0.2 Markers

| Marker | Meaning | What you need to do |
|---|---|---|
| `[E##]` Erratum | The original is self-contradictory or technically wrong. A correction has been applied in the text. | Confirm or reject the correction. |
| `[Q##]` Question | Information is missing or ambiguous. A *working assumption* is stated. | Answer; until then the assumption stands. |
| `[D##]` Divergence | The MiSTer implementation differs from this specification. | Decide: change the spec, change the implementation, or declare it implementation-specific. |
| *Note* | Informational remark by the reviewer. | None. |

All markers are blockquotes whose first line starts with the marker ID, so they can be found with `grep -n '^> \*\*\[Q'` (or `[E`, `[D`). Appendices A, B and C contain auto-generated indexes of all errata, questions and divergences.

### 0.3 Top issues (read these first)

| # | Issue | See |
|---|---|---|
| 1 | The bank-register formula gives a 22-bit (4 MB) address, not 24 bits | E07, Q05 |
| 2 | `GLOBAL_CTRL`: wrong reset value, inverted/duplicated name of the unlock bit, exit value `0` silently kills the hook | E03, E04, E21 |
| 3 | Privilege transitions are under-specified: how a syscall enters Supervisor, which M1 ends it, deferred exit, return address/stack | Q24, Q28, Q22, E06, E20 |
| 4 | Possible privilege hole: User may write `GLOBAL_CTRL`; "unlock" grants nearly everything incl. DMA | Q01, Q15, Q33 |
| 5 | `MMU_EXT` address conflict (`FF0080–BF` vs `FF00E0–EF`); BANK ports write the *active* set only | E16, Q19, E15 |
| 6 | Legacy ports with `A[15:14]=00` land in MMIO_LO; `F2xx` vs PPI aliasing; syscall decode | E10, Q08, Q26 |
| 7 | Legacy syscall wrapper `OUT (F200h),A` is not a valid Z80 instruction and destroys `BC` | E18, Q27 |
| 8 | MiSTer: different MMIO page map, `SUPER_SLOT` at `FAh`, no lock/hook/mailbox/TAG/`0xFE` | D01–D10, §17 |

### 0.4 Limits of the divergence analysis

The MiSTer implementation document was not available to me. All `[D##]` items are derived from this summary of it:

- MMIO page map: palette/CRTC on page 2, MS2 on page 7, keyboard on page 8, FDC on page 9, DMA/blitter on page 6.
- Supervisor slot port is `FAh`.
- Not implemented: IPC Mailbox, TAG addressing, `mmio_userlock`, `supervisor_hook`, syscall `0xFE`.

Everything the summary does not mention is shown as "not stated" and *assumed* identical to this specification. Please correct those cells.

---

## 1. Introduction and Design Principles

### 1.1 Purpose

Aleste LX is a Z80-based system with an extended 24-bit physical address space (16 MB), implemented with a bank-switching mechanism similar to MSX but with extended functionality. It provides:

1. **Backward compatibility** with the Amstrad CPC (Legacy mode: CPC memory maps, CPC port decoding).
2. **Extended functionality** (Native mode: slot-set based mapper, new device set accessed through an MMIO window).
3. **Privilege separation** (Supervisor / User) so that a kernel can mediate access to hardware.

### 1.2 Design principles

- **Fixed device addresses.** A device's MMIO address is part of its architectural contract. Any bus master (CPU, DMA) reaches a device at the same Wishbone address.
- **CPU-private mapper.** The memory mapper state is reachable only by the CPU (never by DMA or other bus masters).
- **Single access path for new devices.** All new devices are reached through one mechanism (MMIO window + MMIO page register).
- **Hardware-assisted privilege transitions.** Entry into Supervisor mode is performed by hardware (trap, syscall); exit is synchronised with the instruction stream.

### 1.3 Notation

| Notation | Meaning |
|---|---|
| `F0h` | Hexadecimal in prose (suffix `h`). Assembler listings use `0F0h` (leading zero) so that assemblers accept it. |
| `0xFF0000` | Hexadecimal in C / Verilog-style listings and 24-bit physical addresses. |
| `A[n:m]` | Bits *n* down to *m* of the Z80 address bus. On I/O cycles this is the port address. |
| bit 0 | Least significant bit. |
| *port* | Z80 I/O address (16 bits on the bus; see §5.1 for how many bits are decoded). |
| `*` after RW | Access subject to privilege restrictions (§8). |

### 1.4 Terminology (changed — please review)

> **[E01] Overloaded terms "slot" and "page"**
> The original uses **"slot"** for (a) a 16 KB region of the Z80 address space ("Slot 0–3"), (b) a group of four bank registers ("slot set", `SUPER_SLOT`/`USER_SLOT`), and (c) the set index in the MMU_EXT table ("Slot 0..3"). It uses **"page"** for (a) the bank register content, (b) the MMIO page (128 bytes), and (c) the column "CPU Page" in the MMU_EXT table (which actually holds CPU address ranges).
> **Correction applied:** this document uses the terms below consistently. Register names (`SUPER_SLOT`, `USER_SLOT`, `MMIO_PAGE`) are kept unchanged because they are part of the programming interface.

| Term | Meaning | Original wording |
|---|---|---|
| **Window** W0–W3 | 16 KB region of the Z80 logical address space, selected by `A[15:14]`: W0 = 0000–3FFF, W1 = 4000–7FFF, W2 = 8000–BFFF, W3 = C000–FFFF | "logical slot", "Slot 0–3", "CPU Page" |
| **Bank** | 16 KB block of physical memory | "page", "bank", "memory page" |
| **Bank register** | Register holding the bank number for one window in one slot set | "BANK_n", "internal mapper register" |
| **Slot set** | Group of four bank registers (one per window). There are four slot sets (16 bank registers total). | "slot set", "Slot" (in MMU_EXT table) |
| **Active slot set** | The slot set currently used for translation: selected by `SUPER_SLOT` in Supervisor mode, `USER_SLOT` in User mode | "current_slot" |
| **MMIO page** | 128-byte block of MMIO_LO selected by `MMIO_PAGE` | "page" |
| **Native port** | I/O port in the new port set (`00h–7Fh`, `F0h–FFh`) | — |
| **Legacy port** | CPC-style port decoded from the full 16-bit address (`7Fxxh`, `BCxxh`, …) | — |

> **Note:** the physical-address formula in the original reads `bank_reg[7:0]` and calls the register "page (bank) register". I use *bank register* throughout.

---

## 2. System State and Operating Modes

### 2.1 State variables

> **[E02] "Two independent parameters" vs. three state variables**
> The original says the state is determined by *two* independent parameters (privilege mode and active I/O device set) and then defines `S = {supervisor_mode, native_mode, mmio_userlock}` — three variables. Furthermore `supervisor_hook` (bit 2 of `GLOBAL_CTRL`) and the internal `EXIT_SUPERVISOR_PENDING` flag are also state.
> **Correction applied:** the complete state is listed below.

| Variable | Where it lives | Description |
|---|---|---|
| `supervisor_mode` | `GLOBAL_CTRL[0]` | 1 = Supervisor, 0 = User |
| `native_mode` | `GLOBAL_CTRL[1]` | 1 = Native, 0 = Legacy. **Ignored while `supervisor_mode = 1`** (but retained and applied when returning to User) |
| `supervisor_hook` | `GLOBAL_CTRL[2]` | 1 = enable hardware trap on opcode fetch from `0038h`/`0066h` |
| `mmio_userlock` | derived: `NOT GLOBAL_CTRL[4]` | 1 = User code is locked out of MMIO/mapper ports |
| `exit_supervisor_pending` | internal flag, not software-visible | set by a write to `GLOBAL_CTRL` that requests leaving Supervisor mode (§7.4) |
| `SUPER_SLOT`, `USER_SLOT` | `F9h`, `FBh` | select the active slot set |
| `MMIO_PAGE` | `F1h` | selects the MMIO page seen through the window |

The system is therefore described by two orthogonal *mode* parameters — **privilege** (Supervisor/User) and **I/O device set** (Native/Legacy) — plus the security and trap-control bits.

> **[D01] `mmio_userlock` and `supervisor_hook` do not exist in the MiSTer implementation**
> According to the implementation summary, `mmio_userlock` and `supervisor_hook` are not implemented. `GLOBAL_CTRL[4]` and `GLOBAL_CTRL[2]` therefore have no function there. Consequences are discussed in §7.2 and §8.

### 2.2 GLOBAL_CTRL — port F0h

> **[E03] Polarity and naming of the security bit**
> The bit table names bit 4 **`mmio_user_unlock`** (1 = allow direct MMIO access; default 0), but every other place (state tuple, security policy, reset table, examples) uses **`mmio_userlock`** and says access is denied when `mmio_userlock = 1`. These are the same bit with *inverted polarity* and two different names.
> **Correction applied:** the *register bit* is `mmio_user_unlock` (bit 4, reset 0). The *internal signal* `mmio_userlock = NOT mmio_user_unlock`. After reset `mmio_user_unlock = 0` ⇒ `mmio_userlock = 1` ⇒ User code is **locked out**.

> **[E04] Reset value of GLOBAL_CTRL is wrong**
> The reset table gives `00000110b` and describes it as "supervisor=1, native=1, mmio_userlock=0". With the bit map of the original (bit 0 = supervisor, bit 1 = native, bit 2 = hook), `00000110b` means *supervisor = 0*, native = 1, hook = 1. In addition "mmio_userlock = 0" would mean *unlocked*, which contradicts "Default: 0" of the unlock bit (locked). Note that `00000110b` is exactly the value of "User + Native + hook enabled", so it was probably confused with a post-initialisation value.
> **Correction applied:** reset value = `00000011b` (Supervisor, Native, hook disabled, locked).

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| 0 | `supervisor_mode` | RW (Supervisor only, see Q01) | 1 | 1 = Supervisor. Set by hardware on trap/syscall. Writing 1 takes effect immediately; writing 0 requests a *deferred* exit (§7.4). |
| 1 | `native_mode` | RW (Supervisor only) | 1 | 1 = Native, 0 = Legacy. No effect while `supervisor_mode = 1`. |
| 2 | `supervisor_hook` | RW (Supervisor only) | 0 (assumed, Q02) | 1 = enable hardware trap on fetches from `0038h`/`0066h`. |
| 3 | — | reserved | 0 | Write 0. |
| 4 | `mmio_user_unlock` | RW (Supervisor only) | 0 | 1 = User code may access MMIO window, `MMIO_PAGE`, and (if applicable) mapper ports. 0 = locked; SysCall only. |
| 7:5 | — | reserved | 0 | Reserved for future security bits. Write 0. |

> **[Q01] Can User code write GLOBAL_CTRL?**
> The access policy of the original (§8.2) lists the prohibited ports for a locked User as `00–7F, F1, F3, F9, FB–FF` and says "only F2 remains available". `F0` (GLOBAL_CTRL) is in neither list. Taken literally, User code could write `GLOBAL_CTRL` and set `supervisor_mode = 1`, which makes the whole privilege model void.
> *Working assumption:* `GLOBAL_CTRL` writes are **ignored in User mode** (reads return the current value or `FFh` — see Q03). Please confirm.

> **[Q02] Default of `supervisor_hook` after reset**
> Original is silent. Reset value `0` is assumed (the kernel enables the hook after installing its handlers at `0038h`/`0066h`). Alternatively the hook could be `1` at reset; in Supervisor mode it is harmless because the trap only matters in User mode (see Q09).

> **[Q03] Read-back and reserved bits**
> What does a read of `GLOBAL_CTRL` return (live bits? `exit_supervisor_pending` visible?). Do reserved bits read as 0 and ignore writes?
> *Working assumption:* reads return the live register bits; reserved bits read 0, writes ignored.

### 2.3 Privilege modes

- **User mode** — execution of application code. Access to mapper/MMIO ports is restricted by `mmio_userlock` (§8).
- **Supervisor mode** — execution of kernel code. Full access to all system resources. Entered by hardware on a trap or syscall (§7). **After reset the system always starts in Supervisor mode.**

### 2.4 Compatibility modes

- **Legacy mode** — full hardware and software compatibility with the Amstrad CPC: CPC port decoding on the full 16-bit address, CPC memory maps (RMR/MMR/ROM select, §10). Available only in User mode.
- **Native mode** — extended mode: slot-set mapper, native port set, MMIO window.

> **[E05] "Supervisor + (Native or Legacy)" contradicts "Native is always active"**
> The original mode table lists the effective mode after a trap as "Supervisor + (Native or Legacy)", while the text says that in Supervisor mode the `native_mode` bit has no effect and Native mechanisms are always used.
> **Correction applied:** in Supervisor mode the effective device set and memory translation are **always Native**. The `native_mode` bit is merely remembered for the next return to User mode.

### 2.5 Effective mode

| `supervisor_mode` | `native_mode` | Effective mode | Memory translation | Port decoding | Native control ports |
|---|---|---|---|---|---|
| 1 | 0 or 1 | **Supervisor (Native)** | Mapper, slot set `SUPER_SLOT` | Native | All |
| 0 | 0 | **User + Legacy** | CPC mapping (RMR/MMR/ROM select) | CPC (16-bit); `F2xxh` → SYSCALL | None, except SYSCALL |
| 0 | 1 | **User + Native** | Mapper, slot set `USER_SLOT` | Native | Depends on `mmio_userlock` (§8.2) |

> **[Q04] Are CPC ports reachable in User + Native mode (and from Supervisor)?**
> The original says Legacy = "CPC port addressing" and Native = "modern I/O port set", suggesting they are mutually exclusive. Then:
> (a) a Native-mode program cannot use `7Fxxh`, `BCxxh`, `F4xxh` etc. at all;
> (b) the Supervisor cannot read or write `RMR`/`MMR`/`ROM_SEL`/Gate Array state of a Legacy task — which it needs when it traps out of a Legacy task and wants to emulate or save/restore it.
> How should (b) be done — via the "Legacy Emulation" page (MMIO_LO page 2), via direct Wishbone access to `MMIO_HI` addresses (CPU cannot do this, only DMA), or not at all?
> *Working assumption:* exclusive port sets; Supervisor accesses legacy device state through the *Legacy Emulation* page (§4.3). In the MiSTer implementation page 2 holds palette/CRTC (see D02).

### 2.6 State transitions

| Event | `supervisor_mode` | `native_mode` | Other effects |
|---|---|---|---|
| Reset | 1 | 1 | `supervisor_hook` = 0, `mmio_user_unlock` = 0, `exit_supervisor_pending` = 0 |
| Hardware trap (§7.2) | → 1 | unchanged | active slot set switches to `SUPER_SLOT` |
| Syscall (`OUT` to `F2h` / `F2xxh`, §7.3) | → 1 *(not specified, Q24)* | unchanged | — |
| Write to `GLOBAL_CTRL` with bit 0 = 1 (Supervisor) | 1 (immediate) | from bit 1 | hook/unlock from bits 2/4 |
| Write to `GLOBAL_CTRL` with bit 0 = 0 (Supervisor) | **unchanged until exit completes** | from bit 1 | `exit_supervisor_pending` = 1 (§7.4) |
| Exit completes (M1 condition, §7.4) | → 0 | unchanged | active slot set switches to `USER_SLOT` |

> **[E06] Software write of `supervisor_mode = 0` is deferred, not immediate**
> The original "Software Mode Switching" section and the state machine say a write to `F0h` sets `S ← {data[0], data[1]}` immediately, whereas "Exiting Supervisor Mode" says that clearing `supervisor_mode` is deferred until a later M1 cycle. These are contradictory for `data[0] = 0`.
> **Correction applied:** setting `supervisor_mode = 1` by software is immediate; clearing is always deferred through `exit_supervisor_pending`.

---

## 3. Address Spaces and Memory Organisation

### 3.1 Logical and physical address spaces

- **Physical address space:** 24 bits (16 MB).
- **Z80 logical address space:** 16 bits (64 KB), divided into four 16 KB **windows** W0–W3 (§1.4).
- A **bank register** maps one window onto a 16 KB bank of physical memory:

```
physical_address = { bank_reg[7:0], cpu_a[13:0] }      (as in the original)
```

> **[E07] The address formula produces 22 bits, not 24**
> `{bank_reg[7:0], cpu_a[13:0]}` is 8 + 14 = **22 bits = 4 MB**, not 16 MB. With an 8-bit bank register the mapper cannot reach the 24-bit space, and in particular cannot reach `FF0000h–FFFFFFh` (which would need bank values `0x3FC–0x3FF`).
> **Not corrected silently** — see Q05. In this document the formula is kept as written, and the usable memory range through the mapper is therefore `000000h–3FFFFFh`.

> **[Q05] What is the real width of a bank register?**
> Options:
> (A) Bank registers are 10 bits wide (e.g. a second byte per register, or two spare bits elsewhere). Note that `MMU_EXT` reserves 64 bytes (`FF0080h–FF00BFh`) while 16 single-byte registers need only 16 — 16 × 2 bytes = 32 bytes would fit a 16-bit-per-register layout.
> (B) Bank registers stay 8 bits; the mapper reaches only 4 MB and the remaining address space is used by MMIO and DMA-only regions.
> (C) The two upper physical address bits come from somewhere else (fixed 0 for memory cycles).
> Also: can a bank register select an MMIO page ("memory-mapped" access to `FF0000h+` through the mapper), or is MMIO reachable only through ports? The original suggests ports only.
> *Working assumption:* option (B)/(C) — mapper reach = 4 MB, memory cycles carry physical address bits `[23:22] = 00`.
> **MiSTer:** the implementation summary does not state the bank width — please fill in.

### 3.2 Typical use of the windows (convention, not hardware-enforced)

> **[E08] Slot roles in the original do not match the CPC memory layout**
> The original assigns fixed roles: "Slot 0 = CPC RAM", "Slot 1 = CPC ROM, system firmware", "Slot 2 = user extended memory", "Slot 3 = supervisor memory, privileged". On a real CPC the lower ROM overlays `0000–3FFF` (window 0) and the upper ROM overlays `C000–FFFF` (window 3) — and the document itself says so in the RMR description (`lower_rom` starts at 0000, `upper_rom` at C000). Also, no hardware mechanism makes window 3 "privileged": any window can be mapped to any bank in any slot set.
> **Correction applied:** the roles are described as *conventions*, below.

| Window | CPU range | CPC meaning (Legacy mode) | Suggested use in Native mode |
|---|---|---|---|
| W0 | `0000–3FFF` | RAM bank 0, or lower ROM when enabled | base memory / low vectors (`0038h`, `0066h` live here) |
| W1 | `4000–7FFF` | RAM | application code/data |
| W2 | `8000–BFFF` | RAM (default screen is at `C000`) | user extended memory |
| W3 | `C000–FFFF` | RAM / screen, or upper ROM when enabled | supervisor data / stack area (by convention) |

> **[Q06] Is any window protected by hardware?**
> Is there any hardware protection (e.g. User code cannot see supervisor memory)? As written, protection exists only because a locked User task cannot change its bank registers, so it is confined to the banks the kernel mapped for `USER_SLOT`. Please confirm that this is the entire memory-protection model (and that DMA bypasses it — §8.4).

> **[Q07] Boot memory**
> After reset all bank registers are `00h` (reset table), so all four windows show physical bank 0 and the Z80 starts at `0000h`. What is at physical `000000h–003FFFh` after reset — boot ROM, flash, preloaded RAM? Where do the CPC ROMs reside physically for Legacy mode (needed to define `legacy_cpc_mapping`)?

### 3.3 MMIO address space: MMIO_HI and MMIO_LO

The last 64 KB of the physical address space (`FF0000h–FFFFFFh`) is reserved for memory-mapped I/O. It is logically split into two regions:

| Region | Range | Size | Purpose | Access path |
|---|---|---|---|---|
| **MMIO_LO** | `FF0000h–FF3FFFh` | 16 KB (128 pages × 128 bytes) | New Aleste LX devices | CPU: `MMIO_PAGE` + window ports `00h–7Fh`. Other bus masters: direct Wishbone access. |
| **MMIO_HI** | `FF4000h–FFFFFFh` | 48 KB | Emulation of legacy CPC devices; hard-wired addresses (e.g. Gate Array at `FF7F00h`, CRTC at `FFBC00h`) | Legacy mode: CPC port `P[15:0]` is translated to `FF0000h \| P[15:0]`. Other bus masters: direct Wishbone access. |

*Note:* The MMIO address of a device is part of its architectural contract. This allows not only the CPU but also other bus masters (such as the DMA controller) to access peripherals directly at fixed addresses over the Wishbone bus.

> **[E09] "The MMU is not mapped into this address space" contradicts the MMIO_LO map**
> The original states that the MMU is not mapped into the MMIO address space and is only accessible by the CPU, while the MMIO_LO device map lists "MMU Extension" at `FF0080–FF00BF` and the extended-mapper table lists registers at `FF00E0–FF00EF`.
> **Correction applied:** `MMU_EXT` *is* decoded at those MMIO_LO addresses, but only on the **CPU's I/O path**. The Wishbone slave interface that DMA and other bus masters use does not decode these addresses (§6.5). The column "WB Address" of the original MMU_EXT table is therefore renamed.

> **[E10] Legacy port translation can hit MMIO_LO**
> "Legacy accesses are translated into direct accesses to MMIO_HI using the full bus address `A[15:0]`." That is only true if `A[15:14] ≠ 00`. A CPC port with `A[15:14] = 00` (e.g. `0F40h`, `3FFFh`) maps to `FF0000h–FF3FFFh`, which is **MMIO_LO** — native devices such as the PIC, mailbox, timer, RTC or even `MMU_EXT`.
> **Not corrected:** needs a decision, see Q08.

> **[Q08] How are Legacy ports with A[15:14] = 00 handled?**
> *Working assumption:* in Legacy mode such accesses are **ignored** (writes dropped, reads return the floating-bus value `FFh`), never forwarded to MMIO_LO.

> **[Q09] Does the hook apply only in User mode?**
> `trap = hook ∧ M1 ∧ (addr = 0038h ∨ 0066h)` as written does not mention the current privilege. In Supervisor mode such a fetch must be a plain fetch from the Supervisor map. *Working assumption:* the trap condition is qualified with `supervisor_mode = 0` (and is therefore a no-op while in Supervisor mode).


---

## 4. MMIO_LO — Device Space for Native Mode

### 4.1 Organisation and address translation

MMIO_LO is 128 pages × 128 bytes = 16 384 bytes (16 KB). The CPU reaches it through the **MMIO window** (ports `00h–7Fh`) and the **`MMIO_PAGE`** register (`F1h`):

```
mmio_physical_address = 0xFF0000 + { MMIO_PAGE[6:0], cpu_a[6:0] }
                      = 0xFF0000 + (MMIO_PAGE << 7) + A[6:0]
```

- `MMIO_PAGE` is a 7-bit register (0–127); bit 7 is ignored and reads 0.
- `A[6:0]` are the seven low bits of the port address (port range `00h–7Fh`).
- Other bus masters (DMA) do not use the window; they address `0xFF0000 + page × 0x80 + offset` directly.

Start address of selected pages (for convenience):

| Page | Start address | Page | Start address |
|---|---|---|---|
| 0 | `FF0000` | 6 | `FF0300` |
| 1 | `FF0080` | 7 | `FF0380` |
| 2 | `FF0100` | 8 | `FF0400` |
| 3 | `FF0180` | 9 | `FF0480` |
| 4 | `FF0200` | … | … |
| 5 | `FF0280` | 127 | `FF3F80` |

> **[E11] The MMIO_LO device map in the original has wrong page numbers and overlapping rows**
> The original lists MMU Extension (`FF0080–FF00BF`) and four reserved ranges (`FF00C0–FF00FF`) under **Page 0**, and then lists `FF0080–FF00FF` again as **Page 1 (Reserved)**. A page is 128 bytes, so page 0 is only `FF0000–FF007F`; everything from `FF0080` to `FF00FF` is page 1. The rows overlapped and contradicted each other.
> **Correction applied:** the map below places each range on its true page. The statement "devices are placed on 32-byte boundaries" is restated: *inside* a page, small devices are aligned to 32 (or 16) bytes; large devices occupy a whole page.

> **[E12] "DMA Access: R\*" for MMIO_WINDOW makes no sense**
> The register table gives DMA read access (`R*`) to `MMIO_WINDOW`. The window is a CPU I/O-path construct; DMA never uses ports. DMA reaches MMIO_LO devices *directly* by their Wishbone addresses.
> **Correction applied:** the DMA column for `MMIO_WINDOW` is "—". DMA access rights are listed per *device* (§13).

> **[Q12] Is `MMIO_PAGE` per-privilege or global?**
> `MMIO_PAGE` is a single register. If a User task changes it (when unlocked) and a trap happens, the kernel finds an unknown page selected; if the kernel changes it, the User task finds it changed on return.
> *Proposal:* the kernel saves and restores `MMIO_PAGE` on every trap/syscall/exit (documented as a software convention). Alternative: two banked copies (like the slot sets). Which one do you want?

### 4.2 Device map

Legend for the last column: **S** = specified in the original, **T** = only named, no register-level specification, **—** = nothing.

| Page | Offset | Address | Size | Device | Spec | MiSTer implementation |
|---|---|---|---|---|---|---|
| 0 | `00–1F` | `FF0000–FF001F` | 32 | PIC Controller (interrupt controller) | T | not stated |
| 0 | `20–3F` | `FF0020–FF003F` | 32 | IPC Mailbox | S (§9) | **not implemented** (D06) |
| 0 | `40–5F` | `FF0040–FF005F` | 32 | System Timer | T | not stated |
| 0 | `60–7F` | `FF0060–FF007F` | 32 | RTC Controller | T | not stated |
| 1 | `00–3F` | `FF0080–FF00BF` | 64 | MMU Extension (`MMU_EXT`), CPU-only | S (§6.5) | not stated |
| 1 | `40–5F` | `FF00C0–FF00DF` | 32 | Reserved | — | not stated |
| 1 | `60–6F` | `FF00E0–FF00EF` | 16 | `MMU_EXT` mapper register file (per original table) | S (§6.5) | not stated |
| 1 | `70–7F` | `FF00F0–FF00FF` | 16 | Reserved | — | not stated |
| 2 | all | `FF0100–FF017F` | 128 | **Legacy Emulation** | T | **palette + CRTC** (D02) |
| 3 | all | `FF0180–FF01FF` | 128 | unassigned | — | not stated |
| 4 | all | `FF0200–FF027F` | 128 | **DMA Controller** | T | not stated (DMA is on page 6, D03) |
| 5 | all | `FF0280–FF02FF` | 128 | unassigned | — | not stated |
| 6 | all | `FF0300–FF037F` | 128 | **Graphics Chip** | T | **DMA / blitter** (D03) |
| 7 | all | `FF0380–FF03FF` | 128 | unassigned | — | **MS2** (D04) |
| 8 | all | `FF0400–FF047F` | 128 | **Sound Chip** | T | **keyboard** (D04) |
| 9 | all | `FF0480–FF04FF` | 128 | unassigned | — | **FDC** (D04) |
| 10–127 | — | `FF0500–FF3FFF` | — | unassigned / reserved | — | not stated |

> **[D02] Page 2: "Legacy Emulation" vs. palette/CRTC**
> Spec: page 2 = "Legacy Emulation" (128 bytes, purpose undefined, see Q10). Implementation: page 2 = palette and CRTC. In the spec, the Gate Array palette and the CRTC are CPC legacy devices living in MMIO_HI (`FF7Fxx`, `FFBCxx`) and are reachable in Native mode only via the Graphics Chip page. If page 2 is meant to be *the native-mode view of the legacy video devices*, then the implementation is the natural realisation and the spec should say so.

> **[D03] DMA at page 4 (spec) vs. DMA/blitter at page 6 (implementation); Graphics Chip also at page 6 (spec)**
> The same page number is assigned to *different devices* in the two documents (page 6: Graphics Chip vs. DMA/blitter). Software written for one will write into the wrong device on the other. Also: **the blitter does not appear anywhere in the spec** — is it part of the "Graphics Chip" or of the DMA controller, or a separate device?

> **[D04] Pages 7, 8, 9: MS2, keyboard, FDC vs. Sound Chip**
> Spec: page 8 = Sound Chip; no keyboard, no FDC, no "MS2". Implementation: MS2 on page 7, keyboard on page 8, FDC on page 9. Open: is "MS2" the Sound Chip (then the spec page 8 should become 7)? Where did the sound chip go if not MS2? Keyboard and FDC (native versions) need to be added to the spec's map; legacy keyboard access goes through the PPI 8255 at `F4xx–F7xx`, and the CPC FDC ports (uPD765 at `FA7E/FB7E`) are not in the spec's legacy list at all.

> **[Q10] What exactly is the "Legacy Emulation" device (page 2)?**
> The original gives no registers. Is it a window to the MMIO_HI devices (so a native-mode kernel can read/write Gate Array, CRTC, PPI, `RMR`, `MMR`, `ROM_SEL` state — cf. Q04)? An emulation control block (enables, trap-on-access)? Please describe or point at the implementation's page 2 register list.

> **[Q11] Missing register-level specifications**
> The following devices appear in the map but have no register description anywhere: **PIC**, **System Timer**, **RTC**, **DMA Controller**, **Graphics Chip**, **Sound Chip**, **Legacy Emulation**. A spec that is the contract for software must define at least offset, name, access (R/W), reset value and interrupt behaviour. Do you want these in this document or in separate per-device documents (and what is their naming/numbering)?

---

## 5. I/O Port Map and Control Registers (Native Mode)

### 5.1 Native port map

| Port | Register | Access | Description | MiSTer implementation |
|---|---|---|---|---|
| `00h–7Fh` | `MMIO_WINDOW` | RW\* | 128-byte window into the selected MMIO_LO page | not stated |
| `80h–EFh` | — | unassigned | see Q14, and §16 for a possible future use | not stated |
| `F0h` | `GLOBAL_CTRL` | RW (Supervisor, Q01) | Mode and security control (§2.2) | bits 2 and 4 not implemented (D01) |
| `F1h` | `MMIO_PAGE` | RW\* | MMIO page selection | not stated |
| `F2h` | `SYS_CALL_CMD_PORT` | W (always) | System call trigger | exists; function `0xFE` not implemented (D08) |
| `F3h` | `CLOCK_CTRL` | RW (Supervisor only) | CPU clock divider (§11) | not stated |
| `F4h–F8h` | — | unassigned | see Q14 | not stated |
| `F9h` | `SUPER_SLOT` | RW\* | Active slot set for Supervisor | **`FAh`** (D05) |
| `FAh` | — | unassigned in spec | see Q14 | `SUPER_SLOT` in the implementation (D05) |
| `FBh` | `USER_SLOT` | RW\* | Active slot set for User | not stated |
| `FCh` | `BANK_0` | RW\* | Bank for W0 (`0000–3FFF`) in the active slot set | not stated |
| `FDh` | `BANK_1` | RW\* | Bank for W1 (`4000–7FFF`) | not stated |
| `FEh` | `BANK_2` | RW\* | Bank for W2 (`8000–BFFF`) | not stated |
| `FFh` | `BANK_3` | RW\* | Bank for W3 (`C000–FFFF`) | not stated |

> **[D05] SUPER_SLOT is at `F9h` in the spec and at `FAh` in the implementation**
> The spec places `SUPER_SLOT`/`USER_SLOT` at `F9h`/`FBh` (formerly `D9h`/`DBh`), leaving `FAh` free. The implementation uses `FAh`, which makes the pair adjacent (`FAh`/`FBh`). Decide which is normative; all examples, the reset table and the access policy in this document currently say `F9h` and must be changed together if the implementation value wins. Also confirm that `USER_SLOT = FBh` and `BANK_0–3 = FCh–FFh` are the same in the implementation.

> **[Q13] How many port-address bits does Native mode decode?**
> The Z80 puts `A[15:8]` on the bus during I/O: for `OUT (n),A` it is the *accumulator*; for `OUT (C),r` it is `B`. The original shows `OUT (F2h),A` (so `A[15:8]` = function code) and uses 8-bit port numbers throughout, therefore Native decoding must use `A[7:0]` only and ignore `A[15:8]`. Legacy decoding uses the full 16 bits.
> *Working assumption:* Native = `A[7:0]`, Legacy = `A[15:0]`.

> **[Q14] Behaviour of unassigned native ports (`80h–EFh`, `F4h–F8h`, `FAh`)**
> Reads return? Writes ignored? Reserved for future use? The original also says (in the Dual Access chapter) "ports `80h–FFh` may be used by legacy devices" — but in Native mode legacy devices are not addressed by ports at all (Q04).
> *Working assumption:* reads return `FFh`, writes are ignored, ports are reserved.

### 5.2 Access matrix

Combines the security policy of §8.2 with the privilege model. `✓` = allowed, `✗` = blocked (write ignored, read returns `FFh` — assumption), `?` = original silent.

| Port / register | Supervisor | User Native, **locked** (`mmio_user_unlock = 0`) | User Native, **unlocked** | User Legacy |
|---|---|---|---|---|
| `00h–7Fh` MMIO_WINDOW | ✓ | ✗ | ✓ | ✗ (CPC decoding) |
| `F0h` GLOBAL_CTRL | ✓ | ? → ✗ (Q01) | ? → ✗ (Q01) | ✗ |
| `F1h` MMIO_PAGE | ✓ | ✗ | ✓ | ✗ |
| `F2h` SYSCALL | ✓ | ✓ | ✓ | ✓ via `F2xxh` |
| `F3h` CLOCK_CTRL | ✓ | ✗ | ✗ (E13) | ✗ |
| `F9h` SUPER_SLOT | ✓ | ✗ | ? (Q15) | ✗ |
| `FBh` USER_SLOT | ✓ | ✗ | ✓ | ✗ |
| `FCh–FFh` BANK_0–3 | ✓ | ✗ | ✓ | ✗ |
| `F4h–F8h`, `FAh`, `80h–EFh` | ✓ (ignored) | ✗ | ✗ | ✗ |

> **[E13] CLOCK_CTRL: "Supervisor only" contradicts the unlock policy**
> `CLOCK_CTRL` is described as "RW, Supervisor mode only", but the access policy lists `F3` among the ports prohibited *when `mmio_userlock = 1`* — implying that an unlocked User may access it.
> **Correction applied:** `CLOCK_CTRL` is Supervisor-only regardless of the unlock bit.

> **[Q15] What does "unlocked" actually grant? (and what are the bit widths of the slot registers?)**
> As written, an unlocked User task can write `USER_SLOT`, all `BANK_n`, `SUPER_SLOT`, `MMIO_PAGE` and the whole MMIO window (including the DMA controller and `MMU_EXT`). That is equivalent to full control of memory and DMA — i.e. effectively Supervisor privilege, and with `SUPER_SLOT` writable it can also redirect the kernel's own memory map at the next trap. Is that intended? Would you like a finer-grained unlock (e.g. separate bits for *window only*, *own bank registers only*, *DMA*)?
> Also: `SUPER_SLOT`/`USER_SLOT` are 8-bit ports but only four slot sets exist (16 bank registers). Are bits 7:2 ignored, reserved-zero, or does a larger value fault?
> *Working assumption:* only bits 1:0 are used; bits 7:2 write-ignored, read 0; unlock grants everything except `GLOBAL_CTRL` and `CLOCK_CTRL`.

### 5.3 Register reference

- **`MMIO_WINDOW` (`00h–7Fh`)** — RW\*. Maps port `P` to `0xFF0000 + {MMIO_PAGE[6:0], P[6:0]}`. In User mode access is denied when `mmio_userlock = 1`.
- **`MMIO_PAGE` (`F1h`)** — RW\*. 7-bit, reset `00h` (Q12).
- **`GLOBAL_CTRL` (`F0h`)** — see §2.2.
- **`SYS_CALL_CMD_PORT` (`F2h`)** — **W, always accessible**. The byte written is the function code. In User + Legacy mode, any access to `F2xxh` is redirected here (see Q on decoding in §7.3).
- **`CLOCK_CTRL` (`F3h`)** — RW, Supervisor only. Bits 3:0 = bus-clock divider (§11).
- **`SUPER_SLOT` (`F9h`)** / **`USER_SLOT` (`FBh`)** — select the active slot set for Supervisor / User mode.
- **`BANK_0…BANK_3` (`FCh…FFh`)** — write/read the bank register of window W0…W3 **in the currently active slot set** (not the other mode's set — see §6.4).

---

## 6. Memory Mapper

### 6.1 Structure

The mapper holds **16 bank registers** = 4 slot sets × 4 windows. Internal index:

```
index = slot_set * 4 + window          // slot_set = 0..3, window = 0..3
```

The *active slot set* depends on the privilege mode:

```
active_slot_set = (supervisor_mode == 1) ? SUPER_SLOT[1:0] : USER_SLOT[1:0]
```

> **[E14] "current_slot" is an 8-bit register value used unmasked as a set index**
> The original defines `current_slot = supervisor_mode ? SUPER_SLOT : USER_SLOT` and computes `current_slot * 4 + ...`. `SUPER_SLOT`/`USER_SLOT` are 8-bit ports; with four sets only 2 bits can be used (Q15). Also the translation formula uses an undefined `page_number`.
> **Correction applied:** the slot-set index is masked to 2 bits, and `page_number` is defined as `cpu_a[15:14]` (the window number).

### 6.2 Bank-register access algorithm

```c
// Access to ports FCh..FFh (BANK_0..BANK_3)
uint8_t  active_slot_set(void) {
    return (supervisor_mode ? SUPER_SLOT : USER_SLOT) & 0x03;
}

void write_bank_register(uint8_t port, uint8_t data) {       // port = FCh..FFh
    uint8_t window = port & 0x03;                            // FCh->0 ... FFh->3
    bank_reg[active_slot_set() * 4 + window] = data;         // width: see Q05
}

uint8_t read_bank_register(uint8_t port) {
    return bank_reg[active_slot_set() * 4 + (port & 0x03)];
}
```

### 6.3 Address translation

```c
uint32_t translate(uint16_t cpu_a) {
    if (supervisor_mode || native_mode) {
        uint8_t window = cpu_a >> 14;                        // cpu_a[15:14]
        return ((uint32_t)bank_reg[active_slot_set() * 4 + window] << 14)
               | (cpu_a & 0x3FFF);                           // 22 bits as written, see Q05
    } else {
        return legacy_cpc_mapping(cpu_a, RMR, MMR, ROM_SEL); // see Section 10
    }
}
```

Note that in User + Legacy mode the mapper (and therefore the bank registers and slot sets) is **not used**; the CPC maps (§10) produce the physical address.

> **[Q16] What does `legacy_cpc_mapping` produce physically?**
> Which physical banks do "RAM_0…RAM_7" and the 512 KB extension correspond to? Where are the lower ROM and the (selectable) upper ROMs located physically? Is the CPC RAM a fixed physical region, or is it itself mapped via a hidden slot set?

### 6.4 Programming a slot set that is not active

> **[E15] BANK ports always write the *active* slot set — this is not stated in the original and it matters**
> In the original, "accesses to `BANK_0`–`BANK_3` are redirected to one of the 16 internal mapper registers, depending on the active slot set". Consequently the Supervisor, when running, writes the registers of the set selected by `SUPER_SLOT` — i.e. *its own* map — and **cannot** configure the User's set through `FCh–FFh` unless it first points `SUPER_SLOT` at the User's set (which instantly changes the Supervisor's own memory map, including the window the kernel code is executing from).
> **Correction applied:** documented here.

Two ways to prepare the User's set:

1. **Through `MMU_EXT`** (preferred): write the four registers of the User set directly via the MMIO window (§6.5). Supervisor's own map is untouched.
2. **Temporary `SUPER_SLOT` switch:** set `SUPER_SLOT` = user set, write `FCh–FFh`, restore `SUPER_SLOT`. This is only safe if the code executing during the switch sits in a window whose bank is identical in both sets.

> **[Q18] Slot sets after reset**
> After reset `SUPER_SLOT = USER_SLOT = 0` and all banks `00h` (reset table), i.e. Supervisor and User share slot set 0. The example in the original ("System initialization") also leaves both at 0. Writing `BANK_n` in Supervisor mode then changes the User map too. Is this intended as the initial state, with the kernel expected to move User to a different set (recommended: Supervisor = 0, User = 1)? Do all 16 bank registers reset to 0, or only set 0?
> *Working assumption:* all 16 reset to `00h`; kernel is expected to separate sets before the first return to User.

> **[Q17] When does a bank/slot write take effect?**
> *Working assumption:* from the very next bus cycle after the `OUT` completes (the Z80 has no prefetch queue, so the next opcode fetch already uses the new mapping). Code that remaps the window it executes from must therefore be mapped identically before and after.

### 6.5 Extended mapper access — `MMU_EXT`

Purpose: save and restore the complete mapper state quickly (context switches), and program non-active slot sets. Access: **RW, CPU only, Native/Supervisor modes**; DMA and other bus masters cannot access it.

Register file as given in the original (addresses renamed — see E09):

| MMIO_LO address (CPU-only path) | Page | Offset | Slot set | Window | Z80 range controlled |
|---|---|---|---|---|---|
| `FF00E0` | 1 | `60h` | 0 | W0 | `0000–3FFF` |
| `FF00E1` | 1 | `61h` | 0 | W1 | `4000–7FFF` |
| `FF00E2` | 1 | `62h` | 0 | W2 | `8000–BFFF` |
| `FF00E3` | 1 | `63h` | 0 | W3 | `C000–FFFF` |
| `FF00E4` | 1 | `64h` | 1 | W0 | `0000–3FFF` |
| `FF00E5` | 1 | `65h` | 1 | W1 | `4000–7FFF` |
| `FF00E6` | 1 | `66h` | 1 | W2 | `8000–BFFF` |
| `FF00E7` | 1 | `67h` | 1 | W3 | `C000–FFFF` |
| `FF00E8` | 1 | `68h` | 2 | W0 | `0000–3FFF` |
| `FF00E9` | 1 | `69h` | 2 | W1 | `4000–7FFF` |
| `FF00EA` | 1 | `6Ah` | 2 | W2 | `8000–BFFF` |
| `FF00EB` | 1 | `6Bh` | 2 | W3 | `C000–FFFF` |
| `FF00EC` | 1 | `6Ch` | 3 | W0 | `0000–3FFF` |
| `FF00ED` | 1 | `6Dh` | 3 | W1 | `4000–7FFF` |
| `FF00EE` | 1 | `6Eh` | 3 | W2 | `8000–BFFF` |
| `FF00EF` | 1 | `6Fh` | 3 | W3 | `C000–FFFF` |

Formula: `MMIO_LO address = FF00E0h + slot_set * 4 + window` — page 1, window offset `60h + slot_set*4 + window`.

> **[E16] MMU_EXT address conflict inside the original**
> The device map reserves **`FF0080–FF00BF` (64 bytes)** for "MMU Extension" and marks `FF00E0–FF00EF` as *Reserved*; the register table puts the actual 16 mapper registers at **`FF00E0–FF00EF`**. The save-example in the original reads from window offset `80h` (which is not even a valid window offset: the window is `00h–7Fh`) for 16 registers.
> **Not corrected silently:** see Q19. This document keeps the register table (`FF00E0–EF`) because it is the only place that defines per-register addresses, and treats `FF0080–FF00BF` as the reserved MMU_EXT block.

> **[Q19] Where is `MMU_EXT` really located and what does the 64-byte block contain?**
> Options: (1) the 16 registers at `FF00E0–EF` are authoritative, and `FF0080–BF` is simply reserved; (2) the 16 registers should be at `FF0080–FF008F` (and other state, e.g. wide bank registers — cf. Q05 — occupies the rest of the 64 bytes). Also: the doc says "CPU-only" — through which hardware path is that enforced (a CPU-side decoder that precedes the Wishbone master)? And is `MMU_EXT` writable in User mode when unlocked?
> *Working assumption:* option (1); `MMU_EXT` is accessible through the window by the CPU only, in Supervisor mode, or in User mode when unlocked.

> **[Q20] Is the `MMU_EXT` register file affected by `supervisor_mode`/slot selection?**
> `MMU_EXT` addresses a specific (set, window) directly, independent of the active slot set. Confirm.

An example of saving/restoring the mapper through `MMU_EXT` is in §15.4 (the original example was not assemblable — see E24).


---

## 7. Mode Switching

There are exactly three ways to change privilege: **software write** to `GLOBAL_CTRL`, **hardware trap**, and **system call**.

### 7.1 Software mode switching

Writing `GLOBAL_CTRL` (port `F0h`) in Supervisor mode loads all defined bits (§2.2). Setting `supervisor_mode = 1` takes effect immediately; clearing it starts the deferred exit sequence of §7.4. The original expressed this as `S ← {data[0], data[1]}`; the full update is:

```
supervisor_mode      <- data[0]        (deferred when 0, see 7.4)
native_mode          <- data[1]
supervisor_hook      <- data[2]
mmio_user_unlock     <- data[4]        (mmio_userlock = ~data[4])
```

Writes from User mode are ignored (Q01).

### 7.2 Hardware trap to Supervisor mode

Entry into Supervisor mode is performed by hardware when the following condition is met:

```
trap = supervisor_hook ∧ ¬supervisor_mode ∧ M1 ∧ MREQ ∧ (A[15:0] == 0038h ∨ A[15:0] == 0066h)
```

> **[E17] The trap condition must use the opcode-fetch cycle, not just "M1"**
> The original says "M1 signal active". On the Z80, `M1` is also active during the **interrupt-acknowledge** cycle (with `IORQ` instead of `MREQ`), where the address bus is not a fetch address. The trap must be qualified by `MREQ` (an opcode fetch). I also added `¬supervisor_mode` per Q09.
> **Correction applied.**

Effects: `supervisor_mode ← 1`; `native_mode` unchanged; active slot set becomes `SUPER_SLOT`. `0038h` is the IM 1 interrupt vector and the `RST 38h` target; `0066h` is the NMI vector.

> **[Q21] Which mapping serves the trapped fetch itself?**
> The trap is detected *during* the M1 cycle whose address is `0038h`/`0066h`. For the Supervisor's handler to run, that very opcode fetch must already be translated with the Supervisor map (`SUPER_SLOT`). That means the mode switch has to take effect combinationally *within* the M1 cycle, before the physical address is presented to memory. Is that the design? (If the switch happens one cycle later, the first handler instruction would be fetched from the User's map.)
> *Working assumption:* yes, combinational.

> **[Q22] Where does the return address live?**
> For an interrupt or NMI the Z80 pushes the return address **before** the fetch at `0038h`/`0066h` — i.e. *in User mode, through the User map, onto the User's stack*. After the trap, the same `SP` is interpreted through the Supervisor map, which may point to different memory. Consequences:
> (a) the kernel must either use identical banks in the stack window in both sets, or reach the User's stack through the other slot set;
> (b) a hostile User can set `SP` to an address whose User-map target is arbitrary — a push through the User map is harmless for the kernel, but the kernel must not trust the stacked value, and must not use `SP` as its own stack without first switching it.
> How should the kernel locate the return address and the user's registers? (Typical answer: the first instruction of the handler loads the Supervisor `SP`; the User's `SP` must be saved in a register that survives — but then which register can the hardware leave untouched?)
> *Working assumption:* kernel handler starts by saving `SP` into a fixed location and loading its own stack; stack window must be mapped identically in both sets for the first few instructions. Please confirm or replace with a better mechanism (e.g. hardware banked `SP`).

> **[Q23] Legacy tasks and the 0038h hook**
> A CPC program takes ~300 interrupts per second at `0038h`. With the hook enabled, each interrupt traps into the Supervisor, which must re-inject the interrupt into the Legacy firmware (emulate `0038h` entry) — costly and complex. Is the intent that the hook is **disabled while a Legacy task runs** (kernel clears bit 2 before exit), so Legacy tasks behave like a plain CPC? Or is `0038h` meant to be re-vectored?
> *Working assumption:* the hook is a per-task kernel setting; the kernel disables it for Legacy tasks.

> **[D09] No `supervisor_hook` in the implementation — how does the Supervisor regain control?**
> Without the hook, a User task running with interrupts/NMI cannot be pre-empted by the kernel, and the only entries into Supervisor are the syscall port and (unprivileged?) writes to `F0h`. Please describe how the implementation delivers interrupts and NMIs to the kernel, and how a syscall enters Supervisor mode (see Q24), because that mechanism must become the specification of the trap path.

### 7.3 System calls

#### 7.3.1 Protocol

- **Function code:** register `A`.
- **Arguments** (standard calling convention):
  - `BC` — first argument (file handle or device number),
  - `DE` — second argument (data pointer or size),
  - `HL` — third argument (buffer pointer or additional parameter).
- **Return value:** `A` = status (`0` = success, other = error code); `HL` may contain a result.
- **Register preservation:** the Supervisor handler saves and restores all registers **except** the ones used to return values.

Register summary (made explicit):

| Register | On entry | On return | Notes |
|---|---|---|---|
| `A` | function code | status | clobbered |
| `F` | undefined | undefined | clobbered |
| `BC` | argument 1 | preserved | Legacy: see E18 / Q27 |
| `DE` | argument 2 | preserved | |
| `HL` | argument 3 | result **or** preserved, per function | Q25 |
| `IX`, `IY`, shadow set, `SP`, `I`, `R` | — | preserved | |

#### 7.3.2 Function codes

| Code | Name | Status in the original |
|---|---|---|
| `00h` | `OpenFile` | named in the dispatcher example only |
| `01h` | `ReadFile` | named in the dispatcher example only |
| `02h` | `WriteFile` | used in the example (BC = handle, DE = size, HL = buffer) |
| `03h–FDh` | — | "and so on" |
| `FEh` | `SYS_MMIO_ACCESS_REQUEST` | specified in §8.3; **not implemented in MiSTer (D08)** |
| `FFh` | — | unassigned |

> **[Q25] System-call ABI details**
> (a) Full list of function codes (the examples show 0, 1, 2 and `0xFE`). (b) Error code numbering: `0xFE` returns `A = 1` for "denied", so is `1` reserved as "denied/generic error"? (c) Is `HL` always clobbered, or only for functions that return a value? (d) Which `F` flags are defined on return (Carry = error would be convenient for Z80)? (e) What happens for an undefined function code? (f) Are syscalls re-entrant/nestable (can a syscall be issued from Supervisor mode)?
> *Working assumption:* undefined code ⇒ `A = FFh`; syscall from Supervisor mode is a no-op returning `FFh`; `1` = "denied".

#### 7.3.3 Wrappers (User side)

**Native mode:**

```asm
; User + Native.  A = function code, BC/DE/HL = arguments.
; OUT (n),A puts A on the data bus AND on A[15:8]; the port is decoded on A[7:0] only (Q13).
syscall:
    OUT  (0F2h),A        ; SYS_CALL_CMD_PORT
    RET                  ; execution comes back here after the syscall completes
```

> **[E18] The Legacy wrapper in the original is not a valid Z80 instruction and cannot keep `BC`**
> The original shows `OUT (F200h), A`. The Z80 has no 16-bit-immediate `OUT`: `OUT (n),A` takes an 8-bit port, and the full 16-bit port can only be given with `OUT (C),r` (address = `BC`). Moreover, with `OUT (n),A` the accumulator appears on `A[15:8]`, so `F2xxh` would require `A = F2h`, i.e. the *function code would have to be `F2h`*. A correct Legacy wrapper must therefore use `OUT (C),A` with `B = F2h`, which **destroys `BC`** — the first syscall argument.
> **Correction applied (as proposal):** see below and Q27.

```asm
; User + Legacy.  A = function code.  BC is destroyed by the wrapper:
; the first argument is passed in IX in Legacy mode (Proposal, Q27).
syscall_legacy:
    LD   BC,0F200h       ; B = F2h on A[15:8]; C = don't care
    OUT  (C),A           ; data bus = A = function code
    RET
```

> **[Q27] Legacy syscall ABI: where does argument 1 go?**
> Options: (a) first argument in `IX` for Legacy (my proposal); (b) wrapper pushes `BC` and the kernel reads it from the User stack (requires stack access, see Q22); (c) a different Legacy trigger that does not need `BC`, e.g. a memory-mapped write or an `IN`-based call; (d) do not support Legacy syscalls with arguments.
> *Working assumption:* (a).

> **[Q26] Decoding of the Legacy syscall port**
> The original text redirects *all* accesses to `F2XXh` (low byte don't care) to `SYS_CALL_CMD_PORT`, while the Verilog fragment compares `io_addr == 16'hF200` (exact match). Which one? Also: on a real CPC the PPI 8255 is selected by `A11 = 0` only, and `F2xxh` has `A11 = 0`; please check that `F2xxh` is not also claimed by the legacy PPI alias decoding, and decide whether `F2xxh` is removed from the PPI range.
> *Working assumption:* all of `F2xxh` (low byte don't care) is the syscall port in User + Legacy mode and takes priority over any CPC alias.

#### 7.3.4 Hardware translation

> **[E19] Verilog fragment compares one signal with two different widths**
> The original compares `io_addr == 8'hF2` and `io_addr == 16'hF200` on the same signal. In Native mode only `A[7:0]` is decoded; in Legacy mode only `A[15:8]` carries the `F2` byte (assumption Q26).
> **Correction applied:**

```verilog
wire native_decode   = supervisor_mode | native_mode;       // Supervisor always decodes Native ports
wire io_write        = iorq & wr;
wire syscall_native  = io_write &  native_decode & (io_addr[7:0]  == 8'hF2);
wire syscall_legacy  = io_write & ~native_decode & (io_addr[15:8] == 8'hF2);  // low byte: don't care
assign syscall_trigger = syscall_native | syscall_legacy;
```

> **[Q24] How does the syscall actually transfer control to the Supervisor?**
> This is the central missing definition. `syscall_trigger` is generated by the `OUT`; the text only says "the Supervisor handler runs, then execution returns after the syscall". It does not say:
> (1) what the hardware does with the CPU: set `supervisor_mode`, and then fetch from **which address**? Forced vector? The same `0038h`? A new address? (The Z80 cannot jump by itself; hardware must either inject an opcode — e.g. `RST` — on the data bus during an M1 cycle, or make the next M1 fetch from a fixed address in Supervisor map.)
> (2) where the return address is kept (the address after the `OUT`, which is the `RET` of the wrapper — pushed on the user stack, or latched in hardware);
> (3) whether interrupts are disabled on entry;
> (4) whether the syscall works when `supervisor_hook = 0`;
> (5) how the handler *returns* to User mode — see E20 and §7.4.
> The implementation does have the syscall (only `0xFE` is missing), so its mechanism is the natural basis for the specification (D09).

#### 7.3.5 Supervisor-side handler

> **[E20] The handler's `RET` does not leave Supervisor mode**
> The example ends each handler with `RET ; Return from the dispatcher`. Returning from the dispatcher with a plain `RET` leaves the CPU in **Supervisor mode**. The only way back to User mode is the sequence of §7.4.
> **Correction applied:**

```asm
Syscall_Dispatcher:                  ; entered in Supervisor mode (Q24)
    ; A = function code; BC, DE, HL = arguments (preserved from the caller)
    CP   0
    JP   Z,Syscall_OpenFile
    CP   1
    JP   Z,Syscall_ReadFile
    CP   2
    JP   Z,Syscall_WriteFile
    CP   0FEh
    JP   Z,Syscall_MmioAccessRequest
    LD   A,0FFh                      ; unknown function (Q25)
    JP   Syscall_Return

Syscall_WriteFile:
    ; BC = file handle, DE = size, HL = buffer pointer
    ; ... perform the operation ...
    XOR  A                           ; status = 0 (success)
    JP   Syscall_Return

Syscall_Return:                      ; common exit
    ; restore the User environment (stack, MMIO_PAGE, ...) as required
    JP   Supervisor_Exit             ; sequence of Section 7.4
```

### 7.4 Exiting Supervisor mode

Exit is a multi-step process synchronised with the processor's instruction cycle:

1. **Initiate.** Kernel code writes `GLOBAL_CTRL` with `supervisor_mode = 0`.
2. **Detect.** Hardware sets `exit_supervisor_pending = 1`. The new `native_mode`, `supervisor_hook` and `mmio_user_unlock` values are loaded immediately (native/hook are not used while in Supervisor mode).
3. **Return instruction.** The following instruction (normally `RETN`) executes **entirely in Supervisor mode**.
4. **M1 synchronisation.** Hardware waits for the specified M1 cycle (Q28).
5. **Mode switch.** At that M1 cycle `supervisor_mode` is cleared and the active slot set becomes `USER_SLOT`.
6. **User fetch.** The instruction at the return address is fetched in User mode.

*Result:* `RETN` executes in Supervisor mode, while the next instruction executes in User mode.

> **[E21] The exit value "data = 0" silently disables the hook and the unlock**
> The original tells the kernel to write `0` to `GLOBAL_CTRL` ("supervisor = 0, native = 0 or 1" — `0` is only `native = 0`). `GLOBAL_CTRL` is a **full register write** (§2.2): `0` also clears `supervisor_hook` and `mmio_user_unlock`, so after the first return to User mode no further traps are possible and a previously granted unlock is lost. The initialisation example has the same issue (it writes `00000010b`).
> **Correction applied:** the exit value must be composed by the kernel. Examples:

| Target | `GLOBAL_CTRL` value |
|---|---|
| User + Native, locked, hook on | `00000110b` (`06h`) |
| User + Native, **unlocked**, hook on | `00010110b` (`16h`) |
| User + Legacy, hook off (Q23) | `00000000b` (`00h`) |
| User + Legacy, hook on | `00000100b` (`04h`) |

Cycle-level view of the exit with `RETN` (`RETN` is `ED 45`: two opcode fetches, then two stack reads; only the third M1 belongs to the next instruction):

| Step | Bus activity | Privilege (specified) |
|---|---|---|
| 1 | `OUT (F0h),A` — I/O write, `supervisor_mode = 0` requested; `pending ← 1` | Supervisor |
| 2 | M1: fetch `ED` | Supervisor |
| 3 | M1: fetch `45` | Supervisor |
| 4 | memory read PCL, PCH (stack, through the **Supervisor** map) | Supervisor |
| 5 | M1: fetch at return address | **User** — clear `supervisor_mode` and `pending` here, active slot set switches |

> **[Q28] Which M1 cycle clears `supervisor_mode`?**
> The original says "the hardware waits for the *next* `M1` bus cycle". Literally, the next M1 after the `OUT` is the `ED` prefix fetch of `RETN` (step 2), which would switch the mode **before** `RETN` runs — contradicting "RETN executes in Supervisor mode". Hardware cannot know instruction boundaries without decoding. Candidates:
> (a) hardware decodes `ED 45` (and perhaps `ED 4D`, `RET`, `JP (HL)`) and switches at the first M1 after the instruction has completed;
> (b) hardware counts M1 cycles (switch at the 3rd M1 after the write — fixes the exit instruction to `RETN`);
> (c) other (e.g. the exit is bound to the pop completing).
> *Working assumption:* (a) restricted to `RETN`; any other instruction after the write is undefined behaviour. Please specify which instructions are allowed.

> **[Q29] Interrupts and traps during the exit window**
> If an INT/NMI is accepted between steps 1 and 5 with the hook enabled, what happens (the trap sets `supervisor_mode ← 1` again while `pending = 1`)? Also the state machine in the original gives the trap higher priority than the exit — so an M1 at `0038h` at step 5 re-enters Supervisor.
> *Working assumption:* the kernel executes `DI` before step 1, and a trap clears `pending`.

> **[Q30] `RETN` vs. `RETI`/`EI;RET` and the interrupt flip-flops**
> `RETN` copies `IFF2` into `IFF1`. If the kernel entered through an IM 1 interrupt (`0038h`), the usual return is `EI; RETI`/`EI; RET`, while `RETN` is the NMI return. Which return is mandated for each entry type (INT, NMI, syscall), and how does the kernel restore the User's `IFF1` correctly?
> *Working assumption:* `RETN` is always used; the kernel sets `IFF2` appropriately beforehand (e.g. with `EI`/`DI` as needed) so that `RETN` restores the right state.

### 7.5 State machine

> **[E22] The original transition function does not match the exit procedure**
> The original function gives the trap priority, then the exit, then `io_write_to_F0h → {data[0], data[1]}` — an immediate update of the supervisor bit, contradicting §7.4 (E06), and it does not update `supervisor_hook`/`mmio_user_unlock`.
> **Correction applied:**

```
on every CPU bus event, in this priority order:

if (reset):
    supervisor_mode = 1; native_mode = 1; supervisor_hook = 0;
    mmio_user_unlock = 0; exit_supervisor_pending = 0

else if (trap_condition):                    // §7.2, requires hook && !supervisor_mode
    supervisor_mode = 1                      // native_mode unchanged
    exit_supervisor_pending = 0              // Q29

else if (syscall_trigger):                   // §7.3; mechanism: Q24
    supervisor_mode = 1                      // native_mode unchanged

else if (exit_supervisor_pending && exit_m1_event):      // Q28
    supervisor_mode = 0                      // native_mode unchanged
    exit_supervisor_pending = 0

else if (io_write_F0h && supervisor_mode):   // Supervisor only, Q01
    native_mode      = data[1]
    supervisor_hook  = data[2]
    mmio_user_unlock = data[4]
    if (data[0]) supervisor_mode = 1         // immediate
    else         exit_supervisor_pending = 1 // deferred
```

---

## 8. Security Model

### 8.1 Model

The mechanism is deliberately small. A User task is **confined** by the following:

- It cannot change its own memory map (bank registers are blocked while `mmio_userlock = 1`).
- It cannot reach the MMIO window, and therefore cannot reach any new device, including the DMA controller and the mailbox.
- Its only door to privileged functionality is the syscall port `F2h`.
- Entry into Supervisor mode happens only through trap or syscall; exit only through the §7.4 sequence.

Not enforced by hardware (as far as the specification states): protection between memory banks (confinement is by mapping, not by permission bits), protection of the Supervisor stack at trap time (Q22), and protection against DMA (§8.4).

### 8.2 Access policy

- **User Native, `mmio_userlock = 1`:** every native port except `F2h` is blocked (writes ignored, reads return `FFh` — assumption, Q14). In the original this was given as the list `00–7F, F1, F3, F9, FB–FF`; `F0` and `F4–F8`, `FA` were omitted, which is covered by Q01/Q14.
- **User Native, `mmio_userlock = 0`:** see matrix in §5.2 (Q15).
- **User Legacy, `mmio_userlock = 1`:** `F2xxh` (syscall) and all standard CPC ports remain available. (The lock bit has no meaning for Legacy tasks beyond that, as no native port is reachable at all.)
- **Supervisor:** access is always permitted.

> **[D10] The lock does not exist in the implementation**
> (see D01.) In the MiSTer implementation, `mmio_userlock` is not implemented. The summary does not say whether User code is *always unlocked* (all native ports accessible — security off) or *always locked*. Which is it? The answer determines whether the existing MiSTer software is portable to a locked implementation (it would use syscalls) or depends on direct access.

### 8.3 System call for unlocking MMIO access — `SYS_MMIO_ACCESS_REQUEST` (function `0xFEh`)

- **Purpose:** request permission for direct MMIO access.
- **Input:** `A = 0FEh`, `BC = 0001h` (MMIO access request flag).
- **Output:** `A` = result code (`0` = allowed, `1` = denied).
- **Behaviour:** the kernel verifies the application's digital signature. If verification succeeds, it clears `mmio_userlock` (sets `GLOBAL_CTRL[4] = 1`).

> **[D08] Syscall `0xFE` is not implemented**
> Software using `SYS_MMIO_ACCESS_REQUEST` will fail on the MiSTer implementation (undefined syscall, see Q25(e)). Until `mmio_userlock` exists, no meaningful implementation of `0xFE` is possible.

> **[Q31] Details of the unlock request**
> (a) What is signed (binary image, header, a manifest?), with which algorithm, and where does the public key live (kernel ROM)? Verifying a signature on a Z80 is heavy — is verification delegated to hardware or to a co-processor?
> (b) How is the "application" identified when the call is made (which bank/slot set/User task)?
> (c) What other values of `BC` are defined (the request flag `0001h` suggests a bit field)?
> (d) What happens on repeated calls?
> *Working assumption:* only `BC = 0001h` is defined; any other value returns `A = 1`.

> **[Q32] Persistence and revocation**
> `mmio_user_unlock` is a single global bit. When the kernel switches to another task it must re-lock (or restore that task's value); how is this expected to be done — by composing the exit value of §7.4 per task? Is there a way to relock a task that no longer needs access? Is the unlock *per application* or *per system run*?
> *Working assumption:* per task, managed by the kernel through the exit value.

### 8.4 DMA and other bus masters

DMA addresses the **physical** 24-bit space directly (through the Wishbone interconnect), bypasses the mapper, and — per the register table — can reach several MMIO_LO devices. The MMU and the `MMU_EXT` block are *not* accessible to it.

> **[Q33] Who may start a DMA transfer, and is DMA address-checked?**
> The DMA controller (MMIO page 4) is reachable only through the window, so a locked User cannot program it. But once unlocked, a User task can ask the DMA to copy to/from *any* physical address, including Supervisor memory. Should the DMA be restricted (address range registers, privilege tag from the master, e.g. a Wishbone `TGC` bit)? Or is "unlock = trust" an accepted position? In that case say so explicitly in §8.2.

---

## 9. IPC Mailbox

**Purpose.** Extremely fast, deterministic and secure communication of control commands and notifications between the **Supervisor (kernel)** and **drivers running in kernel space**.

**Address:** `FF0020h–FF003Fh` (32 bytes, MMIO_LO page 0, offsets `20h–3Fh`). CPU access: RW; DMA: none (register table).

> **[D06] The IPC Mailbox is not implemented in the MiSTer implementation**
> Offsets `20h–3Fh` of page 0 are therefore unused there. Software must not rely on the mailbox; notifications such as `SND_BUF_EMPTY` or `DSK_IO_DONE` must be delivered some other way (interrupt line? polling of device status registers?) — please document the implementation's mechanism so that the specification can describe the fallback.

### 9.1 Registers (as named in the original)

The original names a set of registers but not their offsets, widths or access types. The table lists them with the missing information marked **TBD**.

| Register | Offset | Access | Description |
|---|---|---|---|
| `MAILBOX_CMD` | TBD | RW | Operation code written by the sender (e.g. `SND_BUF_EMPTY`, `DSK_IO_DONE`) |
| `MAILBOX_DATA_*` | TBD (how many?) | RW | Command parameters (channel number, address, …) |
| `MAILBOX_STATUS` | TBD | R / W1C? | `FULL` = message unread; `ACK` = processing acknowledged |
| `MAILBOX_INT_CTRL` | TBD | RW | Interrupt enable / routing for message reception |

### 9.2 Protocol (as given, with the implicit steps made explicit)

1. The sender writes the command and its data.
2. Hardware sets `FULL` and, if enabled in `MAILBOX_INT_CTRL`, raises an interrupt for the kernel.
3. The kernel reads the message and processes it.
4. After processing, the kernel clears `FULL` (and, *possibly*, sets `ACK` — Q35).

> **[Q34] Who are the "drivers" and who writes into the mailbox?**
> The register table gives the mailbox to the CPU only (DMA: "—"). The examples (`SND_BUF_EMPTY`, `DSK_IO_DONE`) look like *hardware* events from the sound and disk devices, yet "drivers running in kernel space" are software. Is the sender (a) kernel-space software on the same Z80 (then the mailbox interrupts the CPU that wrote the message — what is the point?), (b) hardware devices through an internal path that does not use the Wishbone bus, (c) a second processor (e.g. the MiSTer ARM/HPS or a soft core), or (d) User-mode drivers?

> **[Q35] Mailbox semantics**
> (a) Register layout (offsets, number and width of `MAILBOX_DATA_*`).
> (b) What triggers the commit — the write to `MAILBOX_CMD` (so data must be written first), or a separate "send" bit?
> (c) Depth: single message or a FIFO? What happens if the sender writes while `FULL = 1` — overwritten, dropped, or a "busy" bit?
> (d) Who sets/clears `ACK`, and what for? Is `FULL` cleared by software write or automatically on a read of `MAILBOX_CMD`?
> (e) Multiple senders: arbitration or one mailbox per sender?
> (f) Event-code namespace (`SND_*`, `DSK_*`, …) — where is the table of codes?

> **[Q36] Mailbox interrupt routing**
> Is the mailbox interrupt delivered via the PIC (which input line) and then as a Z80 interrupt (IM 1 at `0038h`)? With `supervisor_hook = 1` this enters the Supervisor via the trap; if the CPU is already in Supervisor mode it is an ordinary interrupt. Is the interrupt maskable with `DI`?


---

## 10. Legacy (CPC) Compatibility

### 10.1 Port decoding and device list

In **User + Legacy** mode a Z80 I/O access is decoded on the full 16-bit address `A[15:0]` and forwarded to the fixed MMIO_HI Wishbone address:

```
wb_address = 0xFF0000 | A[15:0]            // valid for A[15:14] != 00, see E10 / Q08
```

| Device | Access | CPC port | WB address | Notes |
|---|---|---|---|---|
| Gate Array (incl. `RMR`, `MMR`, pens/inks) | W | `7Fxxh` | `FF7Fxx` | `RMR`/`MMR` selected by data bits 7:6, §10.2 |
| CRTC 6845 | RW | `BCxxh` / `BDxxh` | `FFBCxx` / `FFBDxx` | register select / data (see Q38) |
| Upper ROM select | W | `DFxxh` | `FFDFxx` | §10.5 |
| PPI 8255 | RW | `F4xxh–F7xxh` | `FFF4xx–FFF7xx` | keyboard, PSG, cassette, … |
| SYSCALL (Aleste LX addition) | W | `F2xxh` | `FFF2xx` | redirected to `SYS_CALL_CMD_PORT` (E19, Q26) |

> **[Q37] Partial decoding and aliasing of CPC ports**
> The original CPC decodes ports partially (e.g. Gate Array = `A15 = 0, A14 = 1`; ROM select = `A13 = 0`; PPI = `A11 = 0`; CRTC = `A14 = 0` with `A9:A8` selecting the function). The spec lists canonical addresses only. Does Aleste LX reproduce the **aliasing** exactly (a port is claimed if its select bits match, regardless of other bits), or decode only canonical addresses? Some CPC software depends on aliases (e.g. `OUT (C),r` with `B = 7Fh` and a floating `C`; `BC` values such as `BCxx` where `xx` is arbitrary). It also decides the priority between overlapping CPC selects.
> *Working assumption:* full CPC-compatible partial decoding with the CPC priority rules, except that `F2xxh` belongs to the syscall.

> **[Q38] CRTC read ports and status**
> Only `BCxxh`/`BDxxh` are listed. The real CRTC is also read via `BExxh` (status) and `BFxxh` (register read). Are those implemented (the MiSTer implementation puts the CRTC on MMIO page 2 — D02)?

> **[Q39] Which CPC peripherals are required?**
> Not listed in the legacy table: the FDC (`FA7Eh`/`FB7Eh`), printer port (`EFxxh`), expansion peripheral select/reset (`F8xxh`), PSG access (via PPI, so covered), cassette (via PPI). The MiSTer implementation has a native FDC on page 9 (D04) — is a Legacy-mode FDC mapped to it? Does the keyboard in Legacy mode go through the PPI emulation, or through the native keyboard device on page 8?

### 10.2 Gate Array command register (`7Fxxh`) — `RMR` and `MMR`

> **[E23] "Must be 1 / Must be 0" are function selectors**
> The original lists bits 7 and 6 of `RMR` as "Must be 1 / Must be 0" and of `MMR` as "Must be 1 / Must be 1". They are the **command selector** of the Gate Array port: bits 7:6 = `00` pen select, `01` ink (colour) select, `10` `RMR`, `11` `MMR`. A write with other values is a *different command* (palette), not an invalid write. The original does not describe the pen/ink commands at all.
> **Correction applied:** documented as selectors; palette commands are an open point (Q39, D02).

| Bits 7:6 | Command |
|---|---|
| `00` | Select pen |
| `01` | Select ink (colour) for the current pen |
| `10` | **RMR** — ROM, mode and interrupt control |
| `11` | **MMR** — RAM memory mapping |

### 10.3 `RMR` — ROM mapping, graphics mode, interrupt counter

| Bit | Name | Description |
|---|---|---|
| 7:6 | selector | `10` (see E23) |
| 5 | — | Must be 0 on Plus machines with the ASIC unlocked |
| 4 | `irq_control` | Interrupt generation control (on a real CPC: resets the Gate Array's 52-line interrupt counter and delays the next interrupt) |
| 3 | `upper_rom` | 1 = upper ROM **disabled**; 0 = enabled. Upper ROM starts at `C000h` |
| 2 | `lower_rom` | 1 = lower ROM **disabled**; 0 = enabled. Lower ROM starts at `0000h` |
| 1:0 | `graphic_mode` | Graphics mode selection (inherited from the CPC) |

### 10.4 `MMR` — RAM memory mapping

| Bit | Name | Description |
|---|---|---|
| 7:6 | selector | `11` (see E23) |
| 5:3 | `bbb` | Upper bank-number bits: select a 64 KB block in extended memory |
| 2:0 | `ccc` | Configuration (which banks appear in which window) |

**CPC 128 KB map** — the table below was cross-checked with the standard CPC 6128 configuration table and is correct as in the original:

| Window | `ccc`=0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| C000–FFFF (W3) | RAM_3 | RAM_7 | RAM_7 | RAM_7 | RAM_3 | RAM_3 | RAM_3 | RAM_3 |
| 8000–BFFF (W2) | RAM_2 | RAM_2 | RAM_6 | RAM_2 | RAM_2 | RAM_2 | RAM_2 | RAM_2 |
| 4000–7FFF (W1) | RAM_1 | RAM_1 | RAM_5 | RAM_3 | RAM_4 | RAM_5 | RAM_6 | RAM_7 |
| 0000–3FFF (W0) | RAM_0 | RAM_0 | RAM_4 | RAM_0 | RAM_0 | RAM_0 | RAM_0 | RAM_0 |

**CPC 512 KB map** (as in the original):

| Window | `ccc`=0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| 0000–3FFF | 0 | 0 | `bbb*4+0` | 0 | 0 | 0 | 0 | 0 |
| 4000–7FFF | 1 | 1 | `bbb*4+1` | 3 | `bbb*4+0` | `bbb*4+1` | `bbb*4+2` | `bbb*4+3` |
| 8000–BFFF | 2 | 2 | `bbb*4+2` | 2 | 2 | 2 | 2 | 2 |
| C000–FFFF | 3 | `bbb*4+3` | `bbb*4+3` | `bbb*4+3` | 3 | 3 | 3 | 3 |

> **[Q40] Numbering base of the 512 KB map**
> The 128 KB table uses absolute names `RAM_0…RAM_7`. The 512 KB table mixes plain numbers (`0…3`) and expressions `bbb*4+n`. With `bbb = 0` the expression `bbb*4+n` gives `0…3`, i.e. the *base* banks, while the 128 KB table shows `RAM_4…RAM_7` for the same configuration (`ccc = 2`).
> The only consistent reading is: **plain numbers = base RAM banks 0–3; `bbb*4+n` = bank *n* of extension block *bbb***, with extension block 0 = `RAM_4…RAM_7`. Please confirm this reading, add it to the table notes, and state: total RAM (base 64 KB + 8 × 64 KB = 576 KB?), the physical location of the extension (Q16), and the behaviour for `bbb` beyond the installed RAM.

### 10.5 Upper ROM select (`DFxxh`)

An 8-bit register that selects the ROM number paged in at `C000–FFFF` when `upper_rom = 0`. (The lower ROM is fixed.)

> **[Q41] ROM numbers**
> How many ROMs can be selected (all 256 values)? What is returned for a ROM number that does not exist (blank / the BASIC ROM, as on a real CPC)? Physical location of the ROMs (Q16).

---

## 11. CPU Clock Control

`CLOCK_CTRL` (port `F3h`), **RW, Supervisor only** (E13).

| Bit | Name | Description |
|---|---|---|
| 7:4 | — | Reserved |
| 3:0 | `dddd` | Bus-clock divider used to derive the CPU clock |

Reset value: `00000111b` (§14).

> **[Q42] Divider formula and legal values**
> The original does not say how `dddd` maps to the CPU frequency: `f_cpu = f_bus / dddd`? `f_bus / (dddd + 1)`? `f_bus / 2^dddd`? Is `0000b` legal? What is `f_bus` (the system clock; is it the same on MiSTer, where the base clock is a PLL output)?
> *Working assumption:* `f_cpu = f_bus / (dddd + 1)`; `0` = no division. **Marked as pure guess; please replace.**

> **[Q43] Interaction with Legacy mode timing**
> A real CPC inserts wait states so that Z80 accesses are aligned to the Gate Array's 1 µs cycle; instruction timings are therefore multiples of 4 T-states at 4 MHz. Does `CLOCK_CTRL` apply to Legacy tasks, or is the Legacy clock fixed at the CPC-equivalent rate? Can a User task observe a clock change (e.g. through the System Timer)?

---

## 12. TAG-Based Wishbone Addressing

### 12.1 Overview

The FPGA interconnect uses a 3-bit **TAG** on the Wishbone bus to simplify slave address decoding:

- **Master devices** output raw addresses only.
- **Slave devices** use the TAG to identify the type of address space.
- The **interconnect** performs a centralised address→TAG translation.

*Note:* the TAG is a pure function of the address, so it is an *implementation optimisation*, not a software-visible architecture feature; software cannot tell whether an implementation uses it. It is therefore described as **informative** here.

> **[D07] TAG addressing is not implemented in the MiSTer implementation**
> Functionally equivalent as long as the implementation's decoders use the same address ranges (§12.3). If any external IP core (or future slave) is written against the TAG signals, it will not work on the MiSTer build. Presumably the implementation decodes `wb_adr_i` directly — please confirm.

### 12.2 TAG encoding

| `TAG[2:0]` | Space | Address range | Contents |
|---|---|---|---|
| `000` | reserved (never generated) | — | — |
| `001` | Memory | `000000h–FEFFFFh` | main memory |
| `010` | Native IO (MMIO_LO) | `FF0000h–FF3FFFh` | new devices |
| `100` | Legacy IO (MMIO_HI) | `FF4000h–FFFFFFh` | compatibility devices |

### 12.3 Address-to-TAG mapping

```verilog
// Address regions
logic mmio_space, mmio_4000_FFFF, mmio_native, mmio_legacy;
assign mmio_space     = (wb_adr_i[23:16] == 8'hFF);
assign mmio_4000_FFFF = (wb_adr_i[15] || wb_adr_i[14]);   // 0x4000-0xFFFF within the FFxxxx page
assign mmio_native    = mmio_space && !mmio_4000_FFFF;    // 0xFF0000-0xFF3FFF
assign mmio_legacy    = mmio_space &&  mmio_4000_FFFF;    // 0xFF4000-0xFFFFFF

// 3-bit TAG, mutually exclusive
always_comb begin
    if      (mmio_native) wb_tag_o = 3'b010;  // Native IO
    else if (mmio_legacy) wb_tag_o = 3'b100;  // Legacy IO
    else                  wb_tag_o = 3'b001;  // Memory space
end
```

The original assigned `3'b000` first and then overrode it; the `000` code is therefore never emitted (a latch-free `always_comb` now covers all branches). No functional change.

> **[Q44] Is the TAG visible to any slave or external core?**
> If TAG encoding becomes an interface (e.g. for third-party cores), a version/compat statement is needed; otherwise it may be dropped from the normative part. Also: the *DMA-originated* accesses — do they use the same address→TAG function (so `MMU_EXT`, which must be CPU-only, is protected by *not* being decoded on the DMA side, or by an additional TAG bit)?

### 12.4 Advantages

- Slaves only compare the TAG: fast decoding.
- New address-space types can be added without touching slaves.
- CPC legacy addressing is preserved.

---

## 13. Register and Address Summary

`*` = subject to privilege restrictions (§5.2, §8). Divergence column: only what is known from the implementation summary.

| Device / register | RW | Legacy IO | Legacy WB | Native IO | Native WB | Size | CPU | DMA | MiSTer |
|---|---|---|---|---|---|---|---|---|---|
| `MMIO_WINDOW` | RW | – | – | `00h–7Fh` | `FF0000 + {PAGE, A[6:0]}` | 128 | RW\* | – (E12) | not stated |
| `GLOBAL_CTRL` | RW | – | – | `F0h` | – | 1 | RW (Supervisor) | – | bits 2, 4 absent (D01) |
| `MMIO_PAGE` | RW | – | – | `F1h` | – | 1 | RW\* | – | not stated |
| `SYSCALL` | W | `F2xxh` | `FFF2xx` | `F2h` | – | 1 | W | – | present; `0xFE` absent (D08) |
| `CLOCK_CTRL` | RW | – | – | `F3h` | – | 1 | RW (Supervisor) | – | not stated |
| `SUPER_SLOT` | RW | – | – | `F9h` | – | 1 | RW\* | – | **`FAh`** (D05) |
| `USER_SLOT` | RW | – | – | `FBh` | – | 1 | RW\* | – | not stated |
| `BANK_0…3` | RW | – | – | `FCh–FFh` | – | 1 each | RW\* | – | not stated |
| `MMU_EXT` | RW | – | – | via window (page 1) | `FF0080–FF00BF` (regs at `FF00E0–EF`, Q19) | 64 | RW (CPU only) | – | not stated |
| PIC Controller | RW | – | – | via window (page 0) | `FF0000–FF001F` | 32 | RW | RW | not stated |
| IPC Mailbox | RW | – | – | via window (page 0) | `FF0020–FF003F` | 32 | RW | – | **absent** (D06) |
| System Timer | RW | – | – | via window (page 0) | `FF0040–FF005F` | 32 | RW | – | not stated |
| RTC Controller | RW | – | – | via window (page 0) | `FF0060–FF007F` | 32 | RW | – | not stated |
| Legacy Emulation | RW | – | – | via window (page 2) | `FF0100–FF017F` | 128 | RW | RW | palette+CRTC (D02) |
| DMA Controller | RW | – | – | via window (page 4) | `FF0200–FF027F` | 128 | RW | – | page 6, DMA/blitter (D03) |
| Graphics Chip | RW | – | – | via window (page 6) | `FF0300–FF037F` | 128 | RW | RW | page 6 = DMA/blitter (D03) |
| Sound Chip | RW | – | – | via window (page 8) | `FF0400–FF047F` | 128 | RW | RW | MS2 on page 7; page 8 = keyboard (D04) |
| *(no spec entry)* keyboard | – | – | – | page 8 | `FF0400–FF047F` | 128 | – | – | **page 8** (D04) |
| *(no spec entry)* FDC | – | – | – | page 9 | `FF0480–FF04FF` | 128 | – | – | **page 9** (D04) |
| Gate Array | W | `7Fxxh` | `FF7Fxx` | – | – | – | W | W | not stated |
| CRTC 6845 | RW | `BCxxh/BDxxh` | `FFBCxx/FFBDxx` | – | – | – | RW | RW | page 2 (D02) |
| Upper ROM select | W | `DFxxh` | `FFDFxx` | – | – | – | W | – | not stated |
| PPI 8255 | RW | `F4xxh–F7xxh` | `FFF4xx–FFF7xx` | – | – | – | RW | RW | not stated |

---

## 14. Reset State

> **[E04]** — see §2.2: the original reset value of `GLOBAL_CTRL` (`00000110b`) is inconsistent with its own bit map.

| Register | Address | Reset value | Description |
|---|---|---|---|
| `GLOBAL_CTRL` | `F0h` | `00000011b` (**corrected**) | supervisor = 1, native = 1, hook = 0 (Q02), `mmio_user_unlock` = 0 (locked) |
| `MMIO_PAGE` | `F1h` | `00h` | MMIO page 0 |
| `SUPER_SLOT` | `F9h` (impl. `FAh`, D05) | `00h` | slot set 0 for Supervisor |
| `USER_SLOT` | `FBh` | `00h` | slot set 0 for User (shares set 0 with Supervisor, Q18) |
| `BANK_0…BANK_3` / all 16 bank registers | `FCh–FFh`, `MMU_EXT` | `00h` | all banks 0 (Q18, Q07) |
| `CLOCK_CTRL` | `F3h` | `00000111b` | divider value (Q42) |
| `exit_supervisor_pending` | internal | 0 | — |

> **[Q45] Reset values of the remaining state**
> Missing: `RMR`/`MMR`/`ROM_SEL` (CPC reset values: both ROMs enabled, mode 1?), Gate Array palette, PIC mask, timer, mailbox (`FULL = 0`?), DMA. Please add (even "undefined; kernel must initialise").

---

## 15. Code Examples

### 15.1 Initialisation after reset and first entry to User mode

> **[E25] The original initialisation example never leaves Supervisor mode correctly**
> The original sets `SUPER_SLOT = USER_SLOT = 0` (same slot set — Q18), writes `00000010b` to `GLOBAL_CTRL` and says "Now running in User Native Mode". Per §7.4 the switch only completes after a `RETN` (or other defined exit instruction) and a fetch from a return address. The value also disables the hook and does not program any User map.
> **Correction applied:**

```asm
; After reset: Supervisor + Native, GLOBAL_CTRL = 03h, all banks 00h, slot sets 0/0.
USER_BANKS  EQU  0x10            ; physical banks 10h..13h for the User (illustrative)

start:
    DI
    ; 1. Separate the slot sets: Supervisor keeps set 0, User uses set 1
    LD   A,1
    OUT  (0FBh),A                ; USER_SLOT = 1          (SUPER_SLOT stays 0; port F9h / FAh in impl., D05)

    ; 2. Program the User map through MMU_EXT (page 1, offsets 64h..67h = set 1, W0..W3)
    LD   A,1
    OUT  (0F1h),A                ; MMIO_PAGE = 1 -> window covers FF0080h..FF00FFh
    LD   BC,0464h                ; B = 4 registers, C = window offset 64h (FF00E4h)
    LD   HL,user_bank_table      ; 4 bytes: 10h,11h,12h,13h
.map_loop:
    LD   A,(HL)
    OUT  (C),A                   ; port C (A[7:0]) = 64h..67h, B on A[15:8] is ignored (Q13)
    INC  HL
    INC  C
    DJNZ .map_loop

    ; 3. CPU clock (Supervisor only)
    LD   A,00000111b
    OUT  (0F3h),A                ; CLOCK_CTRL (divider meaning: Q42)

    ; 4. Enter User + Native, locked, hook on:  GLOBAL_CTRL = 00000110b
    LD   SP,SV_STACK_TOP         ; Supervisor stack, mapped in set 0
    LD   HL,USER_ENTRY
    PUSH HL                      ; return address for RETN
    LD   A,00000110b
    OUT  (0F0h),A                ; request exit; hook = 1, unlock = 0
    RETN                         ; pops USER_ENTRY; the fetch at USER_ENTRY is in User mode (Q28)
    ; The User code must set its own SP first.
```

### 15.2 Requesting MMIO access

```asm
request_mmio_access:
    LD   A,0FEh                  ; SYS_MMIO_ACCESS_REQUEST   (not implemented in MiSTer, D08)
    LD   BC,0001h                ; MMIO access request flag  (Legacy: argument in IX, Q27)
    CALL syscall                 ; wrapper of 7.3.3
    OR   A                       ; A = 0: allowed, A = 1: denied
    RET  NZ                      ; error if A != 0
    ; mmio_user_unlock = 1: direct MMIO access is now permitted (E03: unlock = 1)
    RET
```

The original comment "`mmio_userlock=0`" is equivalent to `mmio_user_unlock = 1` (E03).

### 15.3 Enabling the hardware trap

> **[E26] Trap-handler example is misleading**
> The original writes `00000111b` ("supervisor=1, native=1, trap_enabled=1") *while already in Supervisor mode* and then states that "accesses to `0038h`/`0066h` will now trigger a hardware transition". In Supervisor mode the trap is a no-op (Q09); the hook is only meaningful for the *next* User task. The bit is also named `supervisor_hook`, not `trap_enabled`.
> **Correction applied:** the hook is enabled as part of the exit value (see 15.1 and E21). To enable it while remaining in Supervisor mode:

```asm
    ; Supervisor mode; handlers at 0038h and 0066h already installed in the Supervisor map
    LD   A,00000111b             ; supervisor=1, native=1, supervisor_hook=1, locked
    OUT  (0F0h),A                ; GLOBAL_CTRL
    ; Fetches from 0038h / 0066h by User code now enter Supervisor mode (Section 7.2)
```

### 15.4 Saving and restoring the mapper state

> **[E24] The original save routine cannot be assembled and cannot work**
> `OUT (A),A` is not a Z80 instruction; `IN A,(00h)` reads a different port than the one being addressed (so it would read window offset 0, not the register); the register index and the data both live in `A`; the start offset `80h` is outside the window (`00h–7Fh`); the registers are at window offset `60h` of page 1 (Q19), not `80h`; the previous `MMIO_PAGE` is not restored.
> **Correction applied:**

```asm
; Save all 16 bank registers (MMU_EXT) to (HL)..(HL+15).
; Supervisor, or unlocked User.  Destroys AF, BC, HL.  Preserves MMIO_PAGE.
save_mapper_state:
    IN   A,(0F1h)                ; remember MMIO_PAGE
    PUSH AF
    LD   A,1
    OUT  (0F1h),A                ; MMIO_PAGE = 1: FF0080h..FF00FFh
    LD   BC,1060h                ; B = 16 registers, C = window offset 60h (= FF00E0h)
.save_loop:
    IN   A,(C)                   ; read MMU_EXT register
    LD   (HL),A
    INC  HL
    INC  C
    DJNZ .save_loop
    POP  AF
    OUT  (0F1h),A                ; restore MMIO_PAGE
    RET

; Restore.  Writing the *active* slot set changes the current mapping immediately (Q17).
restore_mapper_state:
    IN   A,(0F1h)
    PUSH AF
    LD   A,1
    OUT  (0F1h),A
    LD   BC,1060h
.restore_loop:
    LD   A,(HL)
    OUT  (C),A
    INC  HL
    INC  C
    DJNZ .restore_loop
    POP  AF
    OUT  (0F1h),A
    RET
```

---

## 16. Informative Annex: Direct Port Access to MMIO_LO Page 127 (not implemented)

*This annex is non-normative. It condenses the original chapter "Architectural Extension Capabilities: Dual Device Access" and corrects its address arithmetic.*

### 16.1 Current architecture

All new devices are reached through one mechanism only: `User application → MMIO_WINDOW (00–7Fh) → MMIO_PAGE → device in MMIO_LO`. This is uniform and works for all devices. Typical cost of a device access: `OUT (F1h),A` once to select the page, then the access itself.

### 16.2 Possible extension

The *last MMIO_LO page (page 127)* could be mapped to the upper half of the port space for latency-critical devices (real-time timer, interrupt controller, frequently polled status registers):

| Item | Value |
|---|---|
| MMIO page 127 | `FF3F80h–FF3FFFh` (128 bytes) |
| Ports mapped | `80h–EFh` (112 ports) ↔ page-127 offsets `00h–6Fh` |
| Not mapped | page-127 offsets `70h–7Fh` (ports `F0h–FFh` are the control registers) |

```verilog
// Direct access: ports 80h..EFh -> MMIO_LO page 127
wire direct_hit = io_access && (io_addr[7:0] >= 8'h80) && (io_addr[7:0] <= 8'hEF);
wire [23:0] mmio_physical_addr = 24'hFF0000 + {7'd127, io_addr[6:0]};   // = FF3F80 + offset
```

> **[E27] Wrong addresses and arithmetic in the original annex**
> The original says "ports `80h–FFh` → MMIO_LO page 127 (`FF8080h–FFFFFFh`)". Page 127 is `FF3F80h–FF3FFFh`, not `FF8080h–FFFFFFh` (which would also be MMIO_HI). Its Verilog computes `24'hFF8000 + {7'd127, cpu_addr[6:0]}`, which yields an address around `FFBF80h`–`FFBFFFh` — outside MMIO_LO. It also mentions ports up to `FFh` in the text but filters `<= EFh` in the code.
> **Correction applied** (above).

> **[E28] Faults in the original `dual_access_device` example**
> `DEVICE_BASE_PORT` is undefined; the port path indexes `device_regs[cpu_io_addr[3:0]]` while the bus path indexes `device_regs[wb_adr_i[5:2]]` (word addressing) — the two accesses would hit different registers; the `rst_n` block is empty. The module was dropped from this annex; a conforming version needs a single common register index.

### 16.3 Why it is not implemented

1. No practical need — window access costs one or two additional instructions.
2. Port-space pressure — `80h–EFh` is the only large free native range; the original also worried about conflicts with legacy devices (not relevant in Native mode, Q04/Q14).
3. Simplicity — one access mechanism, simpler decoding, documentation and debugging.
4. No driver currently needs it.

### 16.4 Roadmap statement of the original (informative)

| Version | Device access | Comment |
|---|---|---|
| Aleste LX v1.0 | `MMIO_WINDOW` only | current implementation |
| Aleste LX v2.0 | + direct access for CPU-critical devices | if required |
| Aleste LX v3.0 | + direct access for selected devices | at the community's discretion |

**Recommendations for peripheral developers:** always design devices to be accessed through `MMIO_WINDOW`; do not rely on direct port access; if performance is critical, optimise access algorithms, use DMA, and cache frequently used values; for compatibility with legacy devices use the emulation mechanism in MMIO_HI and do not occupy ports that may be required by the legacy environment.

---

## 17. MiSTer Implementation — Divergence Summary

*All entries are derived from the implementation summary (§0.4).*

### 17.1 Conformance matrix

| Area | Specification | MiSTer implementation | Status | ID |
|---|---|---|---|---|
| `SUPER_SLOT` port | `F9h` | `FAh` | **differs** | D05 |
| MMIO page 2 | Legacy Emulation | palette + CRTC | **differs** | D02 |
| MMIO page 4 | DMA Controller | not stated (page 6 = DMA/blitter) | **differs** | D03 |
| MMIO page 6 | Graphics Chip | DMA / blitter | **differs** | D03 |
| MMIO page 7 | unassigned | MS2 | **extension** | D04 |
| MMIO page 8 | Sound Chip | keyboard | **differs** | D04 |
| MMIO page 9 | unassigned | FDC | **extension** | D04 |
| Blitter | not in spec | present (page 6) | **extension** | D03 |
| IPC Mailbox (page 0, `20h–3Fh`) | specified (§9) | not implemented | **missing** | D06 |
| TAG-based Wishbone addressing | specified (§12) | not implemented | **missing** (informative) | D07 |
| `mmio_userlock` / `GLOBAL_CTRL[4]` | specified (§2.2, §8) | not implemented | **missing** | D01, D10 |
| `supervisor_hook` / `GLOBAL_CTRL[2]` | specified (§7.2) | not implemented | **missing** | D01, D09 |
| Syscall function `0xFE` | specified (§8.3) | not implemented | **missing** | D08 |
| Syscall port `F2h` / `F2xxh` | specified (§7.3) | present (assumed) | not stated | Q24 |
| `GLOBAL_CTRL` bits 0, 1 | specified | present (assumed) | not stated | — |
| `MMIO_PAGE` (`F1h`), window `00h–7Fh` | specified | present (assumed) | not stated | — |
| `USER_SLOT` `FBh`, `BANK_0–3` `FCh–FFh` | specified | assumed same | not stated | D05 |
| `MMU_EXT` | specified (§6.5) | not stated | not stated | Q19 |
| PIC / Timer / RTC (page 0) | named only | not stated | not stated | Q11 |
| `CLOCK_CTRL` `F3h` | specified | not stated | not stated | Q42 |
| Bank register width | 8 bits (22-bit result) | not stated | not stated | Q05 |

### 17.2 Practical consequences

- **Software portability:** code written for the MMIO page map of the spec (DMA at page 4, graphics at page 6, sound at page 8) will address wrong devices on the MiSTer build, and vice versa (D02–D04). The page map is *the* ABI of the native devices; it has to be unified.
- **Security:** the MiSTer build has no lock and no signed-unlock syscall. Whatever runs in User mode has either full port access or none (D01/D10). Software that relies on `0xFE` returning "allowed" cannot work there (D08).
- **Supervisor entry:** the MiSTer build cannot trap `0038h`/`0066h`. A kernel on that build can only get control through syscalls (and, if User code may write `GLOBAL_CTRL`, by User cooperation), which defeats pre-emption and NMI handling (D09).
- **Mailbox:** drivers cannot use the mailbox for notifications (D06).
- **Wishbone TAG:** no functional effect for software (D07).

---

## Appendix A. Index of Errata

Errors in the original, corrected in this document (generated).

| ID | Title | Section |
|---|---|---|
| E01 | Overloaded terms "slot" and "page" | §1.4 |
| E02 | "Two independent parameters" vs. three state variables | §2.1 |
| E03 | Polarity and naming of the security bit | §2.2 |
| E04 | Reset value of GLOBAL_CTRL is wrong | §2.2 |
| E05 | "Supervisor + (Native or Legacy)" contradicts "Native is always active" | §2.4 |
| E06 | Software write of `supervisor_mode = 0` is deferred, not immediate | §2.6 |
| E07 | The address formula produces 22 bits, not 24 | §3.1 |
| E08 | Slot roles in the original do not match the CPC memory layout | §3.2 |
| E09 | "The MMU is not mapped into this address space" contradicts the MMIO_LO map | §3.3 |
| E10 | Legacy port translation can hit MMIO_LO | §3.3 |
| E11 | The MMIO_LO device map in the original has wrong page numbers and overlapping rows | §4.1 |
| E12 | "DMA Access: R\*" for MMIO_WINDOW makes no sense | §4.1 |
| E13 | CLOCK_CTRL: "Supervisor only" contradicts the unlock policy | §5.2 |
| E14 | "current_slot" is an 8-bit register value used unmasked as a set index | §6.1 |
| E15 | BANK ports always write the *active* slot set — this is not stated in the original and it matters | §6.4 |
| E16 | MMU_EXT address conflict inside the original | §6.5 |
| E17 | The trap condition must use the opcode-fetch cycle, not just "M1" | §7.2 |
| E18 | The Legacy wrapper in the original is not a valid Z80 instruction and cannot keep `BC` | §7.3 |
| E19 | Verilog fragment compares one signal with two different widths | §7.3 |
| E20 | The handler's `RET` does not leave Supervisor mode | §7.3 |
| E21 | The exit value "data = 0" silently disables the hook and the unlock | §7.4 |
| E22 | The original transition function does not match the exit procedure | §7.5 |
| E23 | "Must be 1 / Must be 0" are function selectors | §10.2 |
| E24 | The original save routine cannot be assembled and cannot work | §15.4 |
| E25 | The original initialisation example never leaves Supervisor mode correctly | §15.1 |
| E26 | Trap-handler example is misleading | §15.3 |
| E27 | Wrong addresses and arithmetic in the original annex | §16.2 |
| E28 | Faults in the original `dual_access_device` example | §16.2 |

## Appendix B. Index of Open Questions

Items needing author input; each has a working assumption in the text (generated).

| ID | Title | Section |
|---|---|---|
| Q01 | Can User code write GLOBAL_CTRL? | §2.2 |
| Q02 | Default of `supervisor_hook` after reset | §2.2 |
| Q03 | Read-back and reserved bits | §2.2 |
| Q04 | Are CPC ports reachable in User + Native mode (and from Supervisor)? | §2.5 |
| Q05 | What is the real width of a bank register? | §3.1 |
| Q06 | Is any window protected by hardware? | §3.2 |
| Q07 | Boot memory | §3.2 |
| Q08 | How are Legacy ports with A[15:14] = 00 handled? | §3.3 |
| Q09 | Does the hook apply only in User mode? | §3.3 |
| Q10 | What exactly is the "Legacy Emulation" device (page 2)? | §4.2 |
| Q11 | Missing register-level specifications | §4.2 |
| Q12 | Is `MMIO_PAGE` per-privilege or global? | §4.1 |
| Q13 | How many port-address bits does Native mode decode? | §5.1 |
| Q14 | Behaviour of unassigned native ports (`80h–EFh`, `F4h–F8h`, `FAh`) | §5.1 |
| Q15 | What does "unlocked" actually grant? (and what are the bit widths of the slot registers?) | §5.2 |
| Q16 | What does `legacy_cpc_mapping` produce physically? | §6.3 |
| Q17 | When does a bank/slot write take effect? | §6.4 |
| Q18 | Slot sets after reset | §6.4 |
| Q19 | Where is `MMU_EXT` really located and what does the 64-byte block contain? | §6.5 |
| Q20 | Is the `MMU_EXT` register file affected by `supervisor_mode`/slot selection? | §6.5 |
| Q21 | Which mapping serves the trapped fetch itself? | §7.2 |
| Q22 | Where does the return address live? | §7.2 |
| Q23 | Legacy tasks and the 0038h hook | §7.2 |
| Q24 | How does the syscall actually transfer control to the Supervisor? | §7.3 |
| Q25 | System-call ABI details | §7.3 |
| Q26 | Decoding of the Legacy syscall port | §7.3 |
| Q27 | Legacy syscall ABI: where does argument 1 go? | §7.3 |
| Q28 | Which M1 cycle clears `supervisor_mode`? | §7.4 |
| Q29 | Interrupts and traps during the exit window | §7.4 |
| Q30 | `RETN` vs. `RETI`/`EI;RET` and the interrupt flip-flops | §7.4 |
| Q31 | Details of the unlock request | §8.3 |
| Q32 | Persistence and revocation | §8.3 |
| Q33 | Who may start a DMA transfer, and is DMA address-checked? | §8.4 |
| Q34 | Who are the "drivers" and who writes into the mailbox? | §9.2 |
| Q35 | Mailbox semantics | §9.2 |
| Q36 | Mailbox interrupt routing | §9.2 |
| Q37 | Partial decoding and aliasing of CPC ports | §10.1 |
| Q38 | CRTC read ports and status | §10.1 |
| Q39 | Which CPC peripherals are required? | §10.1 |
| Q40 | Numbering base of the 512 KB map | §10.4 |
| Q41 | ROM numbers | §10.5 |
| Q42 | Divider formula and legal values | §11 |
| Q43 | Interaction with Legacy mode timing | §11 |
| Q44 | Is the TAG visible to any slave or external core? | §12.3 |
| Q45 | Reset values of the remaining state | §14 |
| Q46 | Why were the ports moved from `D0h–DFh`? | §Appendix |

## Appendix C. Index of MiSTer Divergences

Differences between this specification and the MiSTer implementation (generated).

| ID | Title | Section |
|---|---|---|
| D01 | `mmio_userlock` and `supervisor_hook` do not exist in the MiSTer implementation | §2.1 |
| D02 | Page 2: "Legacy Emulation" vs. palette/CRTC | §4.2 |
| D03 | DMA at page 4 (spec) vs. DMA/blitter at page 6 (implementation); Graphics Chip also at page 6 (spec) | §4.2 |
| D04 | Pages 7, 8, 9: MS2, keyboard, FDC vs. Sound Chip | §4.2 |
| D05 | SUPER_SLOT is at `F9h` in the spec and at `FAh` in the implementation | §5.1 |
| D06 | The IPC Mailbox is not implemented in the MiSTer implementation | §9 |
| D07 | TAG addressing is not implemented in the MiSTer implementation | §12.1 |
| D08 | Syscall `0xFE` is not implemented | §8.3 |
| D09 | No `supervisor_hook` in the implementation — how does the Supervisor regain control? | §7.2 |
| D10 | The lock does not exist in the implementation | §8.2 |

## Appendix D. Historical Port Renames (from the original "Summary of Key Changes")

| Register | Old port | New port |
|---|---|---|
| `GLOBAL_CTRL` | `D7h` | `F0h` |
| `MMIO_PAGE` | `D3h` | `F1h` |
| `SYSCALL` | `D4h` | `F2h` |
| `CLOCK_CTRL` | new | `F3h` |
| `SUPER_SLOT` | `D9h` | `F9h` (MiSTer: `FAh`, D05) |
| `USER_SLOT` | `DBh` | `FBh` |
| `BANK_0–3` | `DCh–DFh` | `FCh–FFh` |

Other changes recorded in the original: `GLOBAL_CTRL` bit 0 = `supervisor_mode`, bit 1 = `native_mode` (previously swapped); TAG-based Wishbone addressing added; `MMU_EXT` CPU-only and `CLOCK_CTRL` Supervisor-only; code examples, reset table and peripheral-developer recommendations added.

> **[Q46] Why were the ports moved from `D0h–DFh`?**
> Presumably to avoid a clash with the CPC upper-ROM select `DFxxh` in Legacy decoding. Please confirm and record the reason.
