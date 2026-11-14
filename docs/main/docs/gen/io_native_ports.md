# Native Mode Port Map

| Value | Name | Description |
| --- | --- | --- |
| 0..127 | <a id="MMIO_window"></a>**MMIO window** | 128 bytes: access to MMIO_LO |
| 128..223 | <a id="External_I_O"></a>**External I/O** | 96 bytes: forwarded to Wishbone |
| 224..255 | <a id="MMU_registers"></a>**MMU registers** | 32 bytes: MMU control |
