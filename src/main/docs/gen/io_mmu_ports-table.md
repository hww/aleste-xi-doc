**MMU Registers (Ports E0–FF)**

| Port | Register | Function |
| --- | --- | --- |
| E0–EF | MMU_EXT | Extended mapper access (16 registers, save/restore) |
| F0 | GLOBAL_CTRL | Mode control: bit 0 = supervisor, bit 1 = native, bit 2 = trap hook, bit 4 = mmio_userlock |
| F1 | MMIO_PAGE | 7-bit MMIO page (0–127) |
| F2 | SYSCALL | Supervisor entry (write-only) |
| F3 | CLOCK_CTRL | CPU clock divider (Supervisor only) |
| FA | SUPER_SLOT | Supervisor slot select (4 × 2-bit page fields) |
| FB | USER_SLOT | User slot select (4 × 2-bit page fields) |
| FC–FF | BANK_0–3 | Bank registers for current slot |
