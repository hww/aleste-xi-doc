**Reset State (RTL)**

| Register | Address | Reset_value | Description |
| --- | --- | --- | --- |
| GLOBAL_CTRL | F0 | 8'b0001_0011 | supervisor=1, native=1, lock=1 |
| MMIO_PAGE | F1 | 0x00 | MMIO page 0 |
| SUPER_SLOT | FA | 0xFF | All pages → slot 3 |
| USER_SLOT | FB | 0x00 | All pages → slot 0 |
| BANK_0–3 | FC–FF | 0x00 | All banks = 0 |
| CLOCK_CTRL | F3 | 8'b0000_0010 | Divide by 4 |
