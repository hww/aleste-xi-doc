# MMU Registers (Ports E0–FF)

| Offset | Name | Description |
| --- | --- | --- |
| `0xE0` | <a id="MMU_EXT"></a>**MMU_EXT** | Extended mapper access (16 registers, save/restore) |
| `0xF0` | <a id="GLOBAL_CTRL"></a>**GLOBAL_CTRL** | Mode control: bit 0 = supervisor, bit 1 = native, bit 2 = trap hook, bit 4 = mmio_userlock |
| `0xF1` | <a id="MMIO_PAGE"></a>**MMIO_PAGE** | 7-bit MMIO page (0–127) |
| `0xF2` | <a id="SYSCALL"></a>**SYSCALL** | Supervisor entry (write-only) |
| `0xF3` | <a id="CLOCK_CTRL"></a>**CLOCK_CTRL** | CPU clock divider (Supervisor only) |
| `0xFA` | <a id="SUPER_SLOT"></a>**SUPER_SLOT** | Supervisor slot select (4 × 2-bit page fields) |
| `0xFB` | <a id="USER_SLOT"></a>**USER_SLOT** | User slot select (4 × 2-bit page fields) |
| `0xFC` | <a id="BANK_0"></a>**BANK_0** | Bank register for current slot, page 0 |
| `0xFD` | <a id="BANK_1"></a>**BANK_1** | Bank register for current slot, page 1 |
| `0xFE` | <a id="BANK_2"></a>**BANK_2** | Bank register for current slot, page 2 |
| `0xFF` | <a id="BANK_3"></a>**BANK_3** | Bank register for current slot, page 3 |
