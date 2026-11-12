**RMR — Control, ROM Mapping, Graphics Mode**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| **B7** | [7:7] | 1 | Must be 1 |
| **B6** | [6:6] | 1 | Must be 0 |
| **B5** | [5:5] | 1 | Must be 0 (Plus ASIC unlocked) |
| **IRQ_CTRL** | [4:4] | 1 | Interrupt control |
| **UPPER_ROM** | [3:3] | 1 | 1=disabled, 0=enabled |
| **LOWER_ROM** | [2:2] | 1 | 1=disabled, 0=enabled |
| **GRAPHIC_MODE** | [1:0] | 2 | Graphics mode |
