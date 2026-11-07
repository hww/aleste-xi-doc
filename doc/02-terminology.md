# LX Terminology

**Status:** reference. Definitions of terms used across the LX documentation.
**See also:** `lx_story.md` (historical background), `lx_rtl_reference.md`
(addresses), `lx_mmu.md` (memory model), `lx_io.md` (I/O map).

---

## Platforms and revisions

**CPC** — Amstrad CPC 6128. The canon platform. LX emulates the CPC
6128 *inside the case* (Gate Array, CRTC, PPI, FDC, PSG, RAM banking,
RMR/MMR). Third‑party expansions are not part of the canon.

**520 EXU** — Aleste 520 EXU. The original 1990s Aleste: CPC‑compatible,
built from Soviet discrete components, 520 KB of RAM, extended expansion
bus with DMA. Not canon for LX. Extended features (EXTPORT, MAPMOD,
HIGHX, D62 recode, MSX mapper) are **not recommended** for LX.

**Xi** — Aleste Xi. The "uncompromised" Aleste: expanded capabilities,
analog audio filters, many connectors. Never produced as a finished
board. The design freedom Xi explored is what LX later moved *inside*
the FPGA.

**LX** — Aleste LX. **Lean eXtreme FPGA Architecture.** The current
platform. The guiding principle: *inside the FPGA — no compromises;
outside the FPGA — only what is necessary.* A 24‑bit physical address
space (16 MB), a Z80 CPU, a Native/Legacy mode model, and a compact
serial expansion bus.

**rev. A / rev. C** — revisions of a device (used for MS2):
- **rev. A** — the planned baseline. Tested in simulation only, never
  produced sound on hardware.
- **rev. C** — the working implementation (Carlos). Produces sound.

**Carlos** — the RTL author of the working LX implementation. Rev. C is
his work. The RTL (`gen_rtl`) is authoritative for what exists.

**hww** — the author of the LX platform and of the planned baseline
(rev. A).

---

## Execution modes

**Supervisor mode** — privileged CPU mode. Full access to all system
resources. Entered by reset, by trap (`0038h`/`0066h`), or by syscall.
`GLOBAL_CTRL` bit 0 = 1.

**User mode** — restricted CPU mode for application code. Access to MMU
ports is blocked when `mmio_userlock = 1` (the RTL default). Only the
syscall port (`F2h` / `F2xxh`) is available. `GLOBAL_CTRL` bit 0 = 0.

**Native mode** — modern LX address space and port map. `GLOBAL_CTRL`
bit 1 = 1. In Supervisor mode, Native mode is always used (Legacy is
ignored).

**Legacy mode** — CPC 6128 compatibility mode. CPC ports (`7Fxx`,
`BCXX`, `DFXX`, `F4XX–F7XX`, `FA7E`, `FB7E`, `FB7F`) are active.
Legacy software has no direct access to modern LX devices — only
syscall (`F2xxh`) and the IPC mailbox (via the Supervisor).

**Trap** — hardware entry into Supervisor mode on the M1 cycle at
`0038h` (IM 1) or `0066h` (NMI), when `supervisor_hook = 1`.

**Syscall** — the mechanism to enter Supervisor mode from user code.
`OUT (F2h), A` in Native mode; `OUT (F2xxh), A` in Legacy mode. The
function code is passed in `A`; arguments in `BC`, `DE`, `HL`.

---

## Memory model

**Slot** — one of four 16 KB logical regions: slot 0 (`0000–3FFF`), slot
1 (`4000–7FFF`), slot 2 (`8000–BFFF`), slot 3 (`C000–FFFF`).

**Bank** — a 16 KB physical page. The 24‑bit physical address is formed
as `{slot, bank, offset}`.

**Mapper** — the 16‑register bank‑selection unit. Index:
`{current_slot, cpu_page}`. `current_slot` is read from `SUPER_SLOT`
(`FAh`) in Supervisor mode, from `USER_SLOT` (`FBh`) in User mode.
`cpu_page` is `cpu_a[15:14]` for memory, `cpu_a[1:0]` for I/O.

**SUPER_SLOT / USER_SLOT** — byte registers holding four 2‑bit page
fields (one per slot page). `FAh` and `FBh`. Reset: `SUPER_SLOT = 0xFF`
(all pages → slot 3), `USER_SLOT = 0x00` (all pages → slot 0).

**MMU_EXT** — the 16 mapper registers at ports `E0–EF`, CPU‑only. Used
to save/restore the full mapper state.

**MMIO** — memory‑mapped I/O. The top of the 24‑bit space:
`MMIO_LO` (`FF0000–FF3FFF`, bank‑switched) and `MMIO_HI`
(`FF4000–FFFFFF`, fixed legacy addresses).

**mmio_userlock** — `GLOBAL_CTRL` bit 4. When 1 (RTL default), MMU
ports (`E0–FF`) are blocked in User mode; only `F2` (syscall) is
available. When 0, User mode can reach MMU ports.

---

## Devices

**PIC** — interrupt controller. 16 IRQ lines, edge‑sensitive, priority
bit 15 > bit 0. Registers: mask, status, pending, clear, vector (IM 2).

**NMI controller** — non‑maskable interrupt controller. 4 sources
(wishbone error, panic button, ext board error, debug trigger).

**IPC** — Inter‑Processor Communication mailbox. 4 registers (`CMD`,
`DATA`, `STATUS`, `RETURN`), 8‑bit, `busy` in `STATUS[0]`, `irq_o = busy`.
Exchanges commands and notifications between the Supervisor and drivers.

**DMA** — Direct Memory Access. Two devices in LX:
- **Blitter** (`lx_dma.sv`) — 1 channel, 8‑bit, 2D rectangle copy/fill/
  transparent.
- **SysDMA** (`wb_dma.sv`) — 4 channels, 16‑bit, DRQ/DACK, on the
  memory/video side of the 16→8 bridge.

**MS2 (Magic Sound 2)** — the LX sound chip. 4 channels, 8/16 bit
samples, 48 kHz, stereo, automatic loop, timer IRQ. Two revisions:
**rev. A** (planned baseline, simulation only) and **rev. C** (working
implementation, Carlos).

**Magic Sound** — the original 1990s sound expansion (not MS2). DMA‑based,
MOD/STM playback. Its "birth defects" (64 KB sample limit, ~6‑bit
volume, no stereo, CPU loop) motivated MS2.

**Gate Array** — CPC graphics and RAM‑banking chip. In Legacy mode,
accessed via `7Fxx` (D7/D6 register select). In LX, the palette is
handled outside the legacy MMU.

**CRTC 6845** — CPC video timing chip. `BCXX` (index), `BDXX` (data out),
`BEXX` (status), `BFXX` (data in).

**PSG (AY‑3‑8912)** — CPC sound chip. Accessed through PPI Port A (data)
and Port C (BDIR/BC1). Mandatory in LX (all CPC music depends on it).

**PPI (8255)** — CPC I/O hub. `F4XX`–`F7XX`. Connects the PSG, keyboard,
tape, VSYNC, printer busy.

**FDC (765)** — CPC floppy disk controller. `FA7E` (motor), `FB7E`
(status), `FB7F` (data).

**RMR / MMR** — CPC memory‑mapping registers. RMR: graphics mode, ROM
enable, IRQ control. MMR: RAM bank configuration.

---

## Bus and FPGA

**Wishbone** — the on‑FPGA bus. 24‑bit address, 8‑bit data (CPU/MMU/
peripherals) or 16‑bit (memory/video, SysDMA). Devices are Wishbone
masters or slaves.

**Bridge** — the 16→8 bridge between the 16‑bit memory/video side and
the 8‑bit CPU/peripheral side.

**TAG** — a 3‑bit Wishbone tag identifying the address space:
`001` = memory, `010` = Native I/O, `100` = Legacy I/O.

**MMIO_LO / MMIO_HI** — see *MMU* above. MMIO_LO is bank‑switched
(128 pages × 128 bytes). MMIO_HI is fixed (legacy CPC addresses).

**GLOBAL_CTRL** — the master control register (`F0h`). Bits: 0 =
supervisor, 1 = native, 2 = trap hook, 4 = mmio_userlock.

**gen_rtl** — the generated RTL used in the LX build. The authoritative
source for what exists.

---

## Hardware outside the FPGA

**EXTPORT** — the 520 EXU expansion port (`FABF`). Controls MAPMOD,
HIGHX, HIZ, PPI Port A usage. **Not recommended** for LX.

**MAPMOD** — 520 EXU mode: 0 = CPC‑style 27‑colour palette + CPC6128
RAM banking; 1 = 64‑colour palette + extended RAM mapper.

**HIGHX** — 520 EXU high‑resolution mode. Changes clock frequencies and
video address decoding.

**HIZ** — 520 EXU signal controlling video address decoding. Not fully
understood.

**D62** — the 520 EXU PROM that recodes `DFxx` values (`7→2, 3→3,
otherwise→1`). **Not recommended** for LX.

**Bus (LX Bus)** — the 40‑pin physical expansion slot. 33 signals
assigned (digital: SPI, I2C, RESET, INT, NMI, DETECT, CLK, GPIO; analog:
audio in/out, CV in/out, power, AGND). 7 pins reserved (NC). **Planned
hardware**, not implemented.

**SPI / I2C** — serial buses on the LX Bus. SPI is the main digital bus;
I2C is secondary.

**CV IN / CV OUT** — analog control‑voltage inputs/outputs on the LX Bus,
for modular‑synth‑style control.

---

## Documentation terms

**normative** — a document that defines what LX *must* do.

**planned** — a specification for something not yet implemented.

**archived** — an obsolete document, superseded by a newer one.

**⚠ Spec** — the old specification differs from the RTL; the RTL wins.

**⚠ Outdated** — the old document may be stale.

**✔ By design** — an intentional RTL decision.

**⚠ Carlos** — implemented in RTL by Carlos, but not the LX design
intent.

---

*End of document.*