**SysDMA extension registers (ASSUMPTION: offset 0x50 is free)**

| Offset | Name | Access | Description |
| --- | --- | --- | --- |
| `0x50` | <a id="PRIO_ch_"></a>**PRIO[ch]** | rw | Per-channel arbitration mask, one register per channel |

**PRIO[ch]** (`0x50`)

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:3] | 5 | — | — | Reserved |
| <a id="MASK"></a>**MASK** | [2:0] | 3 | rw | 0x0 | Priority mask; a larger mask wins, ties go to the lower channel number |
