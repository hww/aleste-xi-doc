**Native Mode Port Map**

| Port_range | Size | Purpose |
| --- | --- | --- |
| 00–7F | 128 bytes | MMIO window (access to MMIO_LO) |
| 80–DF | 96 bytes | External I/O (forwarded to Wishbone) |
| E0–FF | 32 bytes | MMU registers |
