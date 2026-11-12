**Control Registers (Ports F0–FF, E0–EF)**

| Port | Register | Function |
| --- | --- | --- |
| F0 | GLOBAL_CTRL | Mode control |
| F1 | MMIO_PAGE | 7-bit MMIO page |
| F2 | SYSCALL | Supervisor entry (write-only) |
| F3 | CLOCK_CTRL | CPU clock divider (Supervisor only) |
| FA | SUPER_SLOT | Supervisor slot select |
| FB | USER_SLOT | User slot select |
| FC–FF | BANK_0–3 | Bank registers for current slot |
| E0–EF | MMU_EXT | Extended mapper access (CPU only) |
