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
| PIC | `wb_z80_pic.sv` | `FC0020` | 8-bit | 16 IRQ lines, edge-sensitive |
| NMI controller | `wb_z80_nmi_ctrl.sv` | `FC0030` | 8-bit | 4 NMI sources |
| IPC mailbox | `ipc_mailbox.sv` | `FC0040` | 8-bit | 4 registers (CMD/DATA/STATUS/RETURN) |
| Blitter | `lx_dma.sv` | `FF0300` | 8-bit | 1 channel, copy/fill/transparent |
| SysDMA | `wb_dma.sv` | `100000` | 16-bit | 4 channels, DRQ/DACK |
| MMU native | `mmu_native.sv` | ports `F0–FF` | 8-bit | — |
| MMU legacy | `mmu_legacy.sv` | ports `7Fxx`, `DFxx` | 8-bit | — |

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
| `FA` | SUPER_SLOT | 4 × 2-bit page fields |
| `FB` | USER_SLOT | 4 × 2-bit page fields |
| `FC–FF` | BANK_0–3 | bank registers for current slot |

> **TBD: verify against RTL.** The port map above follows `mmu_native.sv`
> (`gen_rtl`). If a port changes, update this table only.

---

## 4. MMIO_LO pages (`FF0000–FF3FFF`)

MMIO_LO is organized as 128 pages × 128 bytes. The physical address is
formed as `0xFF0000 + (page << 7) + offset`.

| Page | Physical range | Device | Notes |
|---|---|---|---|
| 0 | `FF0000–FF007F` | (verify against RTL) | — |
| 2 | `FF0100–FF017F` | Legacy emulation | — |
| 4 | `FF0200–FF027F` | (verify against RTL) | — |
| 6 | `FF0300–FF037F` | Blitter (`lx_dma.sv`) | 1 channel, 8-bit |
| 8 | `FF0400–FF047F` | Sound chip | — |

> **TBD: verify against RTL.** Pages 0 and 4 are not confirmed by the
> RTL provided so far. The blitter is confirmed at page 6.

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

---

## 8. Status

- **Authoritative for addresses.** If this file and another document
  disagree, this file wins.
- **Generated from RTL.** If this file and the RTL disagree, the RTL
  wins — update this file.
- **TBD items** are marked explicitly. They will be resolved as more
  RTL is provided.

---

*End of document.*