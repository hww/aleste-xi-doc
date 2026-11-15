**Gate Array R2 — Mode, ROM Enable, LEDs**

| Field | Bits | Width | Fixed | Description |
| --- | --- | --- | --- | --- |
| <a id="B7"></a>**B7** | [7] | 1 | 1 | Must be 1 |
| <a id="B6"></a>**B6** | [6] | 1 | 0 | Must be 0 |
| <a id="CAPS"></a>**CAPS** | [5] | 1 | — | CAPS LED |
| <a id="RUS"></a>**RUS** | [4] | 1 | — | RUS LED |
| <a id="UPPER_ROM"></a>**UPPER_ROM** | [3] | 1 | — | 1=disabled, 0=enabled |
| <a id="LOWER_ROM"></a>**LOWER_ROM** | [2] | 1 | — | 1=disabled, 0=enabled |
| <a id="MODE"></a>**MODE** | [1:0] | 2 | — | 0=160x200, 1=320x200, 2=640x200 |
