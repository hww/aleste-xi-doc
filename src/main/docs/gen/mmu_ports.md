# Control Registers (Ports F0–FF, E0–EF)

| Offset | Name | Access | Reset | Description |
| --- | --- | --- | --- | --- |
| `0xE0` | <a id="MMU_EXT"></a>**MMU_EXT** | rw | — | Extended mapper access, ports E0–EF (CPU only) |
| `0xF0` | <a id="GLOBAL_CTRL"></a>**GLOBAL_CTRL** | rw | 0x13 | Mode control (supervisor=1, native=1, lock=1) |
| `0xF1` | <a id="MMIO_PAGE"></a>**MMIO_PAGE** | rw | 0x00 | 7-bit MMIO page |
| `0xF2` | <a id="SYSCALL"></a>**SYSCALL** | wo | — | Supervisor entry (write-only) |
| `0xF3` | <a id="CLOCK_CTRL"></a>**CLOCK_CTRL** | rw | 0x02 | CPU clock divider (Supervisor only), divide by 4 |
| `0xFA` | <a id="SUPER_SLOT"></a>**SUPER_SLOT** | rw | 0xFF | Supervisor slot select (all pages → slot 3) |
| `0xFB` | <a id="USER_SLOT"></a>**USER_SLOT** | rw | 0x00 | User slot select (all pages → slot 0) |
| `0xFC` | <a id="BANK_0"></a>**BANK_0** | rw | 0x00 | Bank register for current slot, page 0 |
| `0xFD` | <a id="BANK_1"></a>**BANK_1** | rw | 0x00 | Bank register for current slot, page 1 |
| `0xFE` | <a id="BANK_2"></a>**BANK_2** | rw | 0x00 | Bank register for current slot, page 2 |
| `0xFF` | <a id="BANK_3"></a>**BANK_3** | rw | 0x00 | Bank register for current slot, page 3 |
