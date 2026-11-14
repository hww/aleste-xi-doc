# RMR — Control, ROM Mapping, Graphics Mode

![RMR — Control, ROM Mapping, Graphics Mode](gen/L_RMR.svg)

| Field | Bits | Width | Fixed | Description |
| --- | --- | --- | --- | --- |
| <a id="B7"></a>**B7** | [7] | 1 | 1 | Must be 1 |
| <a id="B6"></a>**B6** | [6] | 1 | 0 | Must be 0 |
| <a id="B5"></a>**B5** | [5] | 1 | 0 | Must be 0 (Plus ASIC unlocked) |
| <a id="IRQ_CTRL"></a>**IRQ_CTRL** | [4] | 1 | — | Interrupt control |
| <a id="UPPER_ROM"></a>**UPPER_ROM** | [3] | 1 | — | 1=disabled, 0=enabled |
| <a id="LOWER_ROM"></a>**LOWER_ROM** | [2] | 1 | — | 1=disabled, 0=enabled |
| <a id="GRAPHIC_MODE"></a>**GRAPHIC_MODE** | [1:0] | 2 | — | Graphics mode |
