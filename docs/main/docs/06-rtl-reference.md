# LX RTL Reference

**Status:** authoritative for addresses and bus widths. Generated from RTL
(`gen_rtl`, latest).
**Rule:** if this file and any other document disagree, **this file wins**.
If this file and the RTL disagree, **the RTL wins**.

This file is the **single source of addresses**. All other LX documents
describe registers, bits, protocols and behaviour, and refer to this file
for "where".

---

## 1. Address map (24-bit physical space)

| Range | Width | Purpose |
|---|---|---|
| `000000–EFFFFF` | 16-bit (8-bit to CPU via bridge) | Memory: RAM, ROM, framebuffer |
| `F00000–FCFFFF` | 8-bit | System devices (PIC, NMI, IPC) |
| `FF0000–FF3FFF` | 8-bit | MMIO_LO (bank-switched, 128 pages × 128 bytes) |
| `FF4000–FFFFFF` | 8-bit | MMIO_HI (legacy CPC devices, fixed) |

**Bridge:** the memory and the video controller are 16-bit; a bridge
converts to the 8-bit bus used by the CPU, the MMU and all peripherals.

---

## 2. System devices

| Device | RTL module | BASE_ADDR | Width | Notes |
|---|---|---|---|---|
| PIC | `wb_z80_pic.sv` (inst. in `lx_sys.sv`) | `FC0020` | 8-bit | 16 IRQ lines, edge-sensitive; regs `0x0–0xC` (see `pic_regmap`); `VECTOR` reset `0xFF` |
| System Timer | `lx_sys.sv` | ports `F4/F5/F6` | 8-bit | 16-bit `RT` @1 MHz, `COMPARE`, `WINDOW`; see `Alesta LX Hardware System Timer` Rev 5 |
| NMI controller | `wb_z80_nmi_ctrl.sv` | `FC0030` | 8-bit | 4 NMI sources; gate with `nmi_block_o` from `lx_sys.sv` |
| IPC mailbox | `ipc_mailbox.sv` | `FC0040` | 8-bit | 4 registers (CMD/DATA/STATUS/RETURN) |
| Blitter | `lx_dma.sv` | `FF0300` | 8-bit | 1 channel, copy/fill/transparent |
| SysDMA | `wb_dma.sv` | `100000` | 16-bit | 4 channels, DRQ/DACK |
| MMU native | `mmu_native.sv` | ports `F0–FF` | 8-bit | — |
| MMU legacy | `mmu_legacy.sv` | ports `7Fxx`, `DFxx` | 8-bit | — |

> **Note (System Timer):** `lx_sys.sv` decodes the timer on the low
> address byte (`A7–A0`) of the bus cycle. Upper address bits are ignored,
> as required for Z80 direct I/O. If the platform separates Z80 I/O from
> memory, OR the two decoders into `cs_i` and drive `adr_i[7:0]` from the
> I/O address. The timer's request pulse is wired to IRQ line 6 of the
> PIC.

> **TBD: verify against RTL.** The addresses above are taken from the RTL
> modules provided so far. Any module not listed here is `TBD`.

---

## 3. CPU ports (8-bit, independent of memory width)

| Port | Register | Notes |
|---|---|---|
| `00–7F` | MMIO window | 128 bytes, maps to MMIO_LO page |
| `80–DF` | External I/O | forwarded to Wishbone |
| `E0–EF` | MMU_EXT | 16 mapper registers |
| `F0` | GLOBAL_CTRL | mode control |
| `F1` | MMIO_PAGE | 7-bit page (0–127) |
| `F2` | SYSCALL | Supervisor entry (Native `F2h`, Legacy `F2xxh`) |
| `F3` | CLOCK_CTRL | CPU clock divider (Supervisor only) |
| `F4` | **TIMER_RT_L** | System Timer: read `RT` low / write `COMPARE` low buffer; sets `WINDOW=1` |
| `F5` | **TIMER_RT_H / COMPARE_H** | System Timer: read `SHADOW` / commit `COMPARE` high; clears `WINDOW` |
| `F6` | **TIMER_STATUS_CTRL** | System Timer: `{DUE, WINDOW, ARMED, ENABLE}`; write bit 0 = `ENABLE` (Supervisor only) |
| `FA` | SUPER_SLOT | 4 × 2-bit page fields |
| `FB` | USER_SLOT | 4 × 2-bit page fields |
| `FC–FF` | BANK_0–3 | bank registers for current slot |

> **Resolved (was TBD):** ports `F4/F5/F6` are now assigned to the System
> Timer. They are **not** MMU_EXT or bank registers. Writes to
> `F4/F5/F6` are **supervisor-only**; reads are allowed in both modes.
> The remaining `F0–FF` assignments follow `mmu_native.sv`.

> **TBD: verify against RTL.** The port map above follows `mmu_native.sv`
> (`gen_rtl`). If a port changes, update this table only.
>
---

## 4. MMIO_LO pages (`FF0000–FF3FFF`)

MMIO_LO is organized as 128 pages × 128 bytes. The physical address is
formed as `0xFF0000 + (page << 7) + offset`.

| Page | Physical range | Device | Notes |
|---|---|---|---|
| 0 | `FF0000–FF007F` | **PIC** (`lx_sys.sv`) | regs `0x0–0xC`; see `pic_regmap` |
| 2 | `FF0100–FF017F` | Legacy emulation | — |
| 4 | `FF0200–FF027F` | **(verify against RTL)** | not confirmed; timer is on I/O ports `F4/F5/F6`, not here |
| 6 | `FF0300–FF037F` | Blitter (`lx_dma.sv`) | 1 channel, 8-bit |
| 8 | `FF0400–FF047F` | Sound chip | — |

> **Resolved:** page 0 is the PIC. The System Timer is decoded on I/O
> ports `F4/F5/F6`, not in MMIO_LO; page 4 remains TBD.

> **TBD: verify against RTL.** Page 4 is not confirmed by the RTL
> provided so far. The blitter is confirmed at page 6.

---

## 5. MMIO_HI (`FF4000–FFFFFF`)

Legacy CPC devices at fixed addresses. See `lx_legacy.md` for the
device list. The addresses are part of the CPC canon and do not change.

| Device | Address | Notes |
|---|---|---|
| Gate Array | `FF7Fxx` | CPC canon |
| CRTC 6845 | `FFBCxx` / `FFBDxx` | CPC canon |
| Upper ROM Select | `FFDFxx` | CPC canon |
| PPI 8255 | `FFF4xx–FFF7xx` | CPC canon |
| FDC 765 | `FFFA7E` / `FFFB7E` / `FFFB7F` | CPC canon |

> The addresses above are **CPC canon**, not LX-specific. They are listed
> here for completeness; the authoritative description is in
> `lx_legacy.md` §1.

---

## 6. Bus widths

| Component | Width |
|---|---|
| Memory (SDRAM/BRAM) | 16-bit |
| Video controller | 16-bit |
| Bridge (16→8) | — |
| CPU (Z80) | 8-bit |
| MMU | 8-bit |
| PIC | 8-bit |
| NMI controller | 8-bit |
| IPC mailbox | 8-bit |
| Blitter (`lx_dma.sv`) | 8-bit |
| SysDMA (`wb_dma.sv`) | 16-bit |
| System Timer (`lx_sys.sv`) | 8-bit |

---

## 7. How to use this file

- **If you are writing a device document** (`lx_pic_controller.md`,
  `lx_ipc.md`, `lx_dma.md`, `lx_io.md`): describe registers, bits,
  protocols and behaviour. **Do not** write addresses. Refer to this
  file for "where".
- **If you are writing an architecture document** (`lx_mmu.md`,
  `lx_legacy.md`): describe modes, slots, banks, privileges. CPU port
  addresses (`F0–FF`, `7Fxx`, `DFxx`) may be included because they are
  stable; MMIO addresses should refer to this file.
- **If you are changing an address in the RTL**: update **this file
  only**. Other documents refer to it and do not need to change.
- **System Timer addresses** (`F4/F5/F6`) are recorded **here** and in
  `Alesta LX Hardware System Timer`. If they change, update this file
  first; the timer document refers here for "where".
- **PIC register offsets** (`0x0–0xC`) live in `pic_regmap`; this file
  records only the **base** (`FC0020`) and the MMIO page 0 window
  (`FF0000–FF007F`).

---

## 8. Status

- **Authoritative for addresses.** If this file and another document
  disagree, this file wins.
- **Generated from RTL.** If this file and the RTL disagree, the RTL
  wins — update this file.
- **TBD items** are marked explicitly. They will be resolved as more
  RTL is provided.
- **Changed in this revision:**
  - PIC base `FC0020` confirmed; register range extended to `0x0–0xC`
    (`REPEAT_L/H`, `CLEAR_REPEAT_L/H` added).
  - System Timer added: I/O ports `F4/F5/F6`, `lx_sys.sv`, IRQ line 6.
  - MMIO_LO page 0 resolved to PIC (`FF0000–FF007F`).
  - Ports `F4/F5/F6` explicitly assigned to the System Timer and
    **removed** from the "unassigned / bank" ambiguity.
  - NMI controller note: gate delivery with `nmi_block_o` from
    `lx_sys.sv` (`WINDOW = 1` blocks both `INT` and `NMI`).

---

*End of document.*