# LX MMU API (planned)

## 1. Purpose

`mmu_api.asm` is a planned library that provides a unified interface to
the LX MMU:

- get / set bank for a page
- save / restore the full mapper state
- copy data between slots
- wrappers around the syscall mechanism
- mode control (Native / Legacy, Supervisor / User)

The API is **inspired by MSX** (`ENASLT` / `RDSLT` / `WRSLT`) to make
porting easier, but it is adapted to the LX architecture: **4 hardware
slots × 256 banks × 16 KB = 16 MB**.

---

## 2. Terminology

| Term | Meaning |
|---|---|
| **Slot** | One of four hardware slots (0–3). Each slot has 256 banks. |
| **Bank** | A 16 KB block within a slot. |
| **Page** | A 16 KB region in the Z80 logical address space: page 0 = `0000–3FFF`, page 1 = `4000–7FFF`, page 2 = `8000–BFFF`, page 3 = `C000–FFFF`. |
| **Physical address** | `{slot, bank, offset}` (2 + 8 + 14 = 24 bits). |

The physical address form matches the RTL
(`m_wb_adr_o = {current_slot, mapper_bank, cpu_a[13:0]}`). See
`lx_mmu.md` §3.2.

---

## 3. Functions (planned)

The list below is the intended API. **Signatures and exact register
usage are not fixed yet** — they will be defined when the library is
implemented. The functions are listed here so that the API surface is
documented before the code exists.

### 3.1 Bank access

| Function | Purpose |
|---|---|
| `mmu_get_current_slot` | Return the current slot (depends on mode and `cpu_page`). |
| `mmu_get_bank(page)` | Return the bank mapped at `page` in the current slot. |
| `mmu_set_bank(page, bank)` | Map `bank` at `page` in the current slot. |
| `mmu_set_all_banks(bank0, bank1, bank2, bank3)` | Map all four pages of the current slot at once. |

### 3.2 Cross-slot access

| Function | Purpose |
|---|---|
| `mmu_get_bank_for_slot_page(slot, page)` | Read the bank at `slot`/`page`. |
| `mmu_set_bank_for_slot_page(slot, page, bank)` | Write the bank at `slot`/`page`. |
| `mmu_copy_cross_slot(src_slot, src_bank, dst_slot, dst_bank, size)` | Copy data between banks in different slots. |

### 3.3 State save / restore

| Function | Purpose |
|---|---|
| `mmu_save_full_state(buffer)` | Save the full mapper state (16 registers) to `buffer`. |
| `mmu_restore_full_state(buffer)` | Restore the full mapper state from `buffer`. |

The full mapper state is 16 registers (`reg_bank[0:15]` in the RTL).
They are reachable via `MMU_EXT` at ports `E0–EF` (see `lx_mmu.md` §4.8).

### 3.4 Mode control

| Function | Purpose |
|---|---|
| `mmu_get_mode` | Return the current `GLOBAL_CTRL` value. |
| `mmu_set_mode(value)` | Write `value` to `GLOBAL_CTRL`. |
| `mmu_enable_native` | Set `native_mode` (bit 1 of `GLOBAL_CTRL`). |
| `mmu_enable_legacy` | Clear `native_mode`. |
| `mmu_set_clock(divider)` | Set `CLOCK_CTRL` (Supervisor only). |

### 3.5 Syscall wrappers

| Function | Purpose |
|---|---|
| `syscall(function, arg1, arg2, arg3)` | Invoke a Supervisor syscall. Native: `OUT (F2h), A`. Legacy: `OUT (F2xxh), A`. |

See `lx_mmu.md` §5.3 for the syscall protocol.

---

## 4. Recommendations

1. **Check the current mode before accessing ports.** The MMU registers
   are only reachable in Native mode; in Legacy mode, only the syscall
   port is available.
2. **From User mode, use syscall.** Direct port access is blocked when
   `mmio_userlock = 1` (the RTL default). See `lx_mmu.md` §6.2.
3. **Save / restore the memory context when switching tasks.** Use
   `mmu_save_full_state` / `mmu_restore_full_state`. The BIOS
   `MemoryContext` mechanism (see `lx-bios.md` §8) does this lazily;
   the MMU API provides the explicit form.
4. **Cache frequently used banks.** Reading a bank register costs a
   port access; keeping the value in a variable avoids the cost.
5. **Use `mmu_copy_cross_slot` for large transfers.** It is faster than
   remapping banks back and forth for each 16 KB block.

---

## 5. Not implemented in `gen_rtl`

The following functions appear in older drafts of this document but are
**not implemented** in the current RTL:

| Function | Status |
|---|---|
| `syscall_mem_alloc` | Not implemented (no allocator in RTL). |
| `syscall_mem_free` | Not implemented. |
| `syscall_mmap` | Not implemented. |
| `syscall_request_mmio` (`SYS_MMIO_ACCESS_REQUEST`, `0xFE`) | Not implemented. See `lx_mmu.md` §6.3. |

These may be implemented in a future BIOS or in the library itself. They
are listed here so that the intended API surface is documented, but they
must **not** be assumed to exist on the current hardware.

---

## 6. Relation to `lx-bios.md`

The MMU is a **singleton driver** in the sense of `lx-bios.md` §3.1:

- The VTable is fixed at build time.
- Applications call the MMU through its own labels, for example
  `call __mmu_set_bank`.
- The MMU is used by the system during boot (detection,
  initialization).
- Other drivers may depend on the MMU.

`mmu_api.asm` is the **public interface** of that singleton driver. It
does not implement the MMU itself (the MMU is in the RTL); it wraps the
RTL registers behind a stable API.

---

## 7. MSX compatibility (informative)

The API is inspired by MSX, which makes porting from MSX easier:

| LX (planned) | MSX equivalent |
|---|---|
| `mmu_get_bank(page)` | `RDSLT` (read slot) |
| `mmu_set_bank(page, bank)` | `WRSLT` (write slot) |
| `mmu_set_bank_for_slot_page(slot, page, bank)` | `ENASLT` (enable slot) |
| `mmu_copy_cross_slot(...)` | (no direct MSX equivalent) |

The mapping is approximate: MSX has 4 slots × 4 pages × 64 KB, while LX
has 4 slots × 256 banks × 16 KB. The API keeps the MSX *shape* (get /
set / enable) but uses the LX addressing model.

---

## 8. Status

- **Planned.** Not implemented in `gen_rtl`.
- **API surface** is documented above. Signatures and register usage
  will be finalized when the library is written.
- **Reference** for the current RTL registers: `lx_mmu.md` §4.
- **Reference** for the BIOS driver architecture: `lx-bios.md`.

---

*End of document.*
