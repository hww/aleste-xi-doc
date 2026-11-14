# Rev. C: Global Registers Map

![Rev. C: Global Registers Map](gen/ms2c_global_map.svg)

| Offset | Name | Description |
| --- | --- | --- |
| `0x00` | <a id="CTRL"></a>**CTRL** | — |
| `0x01` | <a id="VOL_L"></a>**VOL_L** | — |
| `0x02` | <a id="VOL_R"></a>**VOL_R** | — |
| `0x03` | <a id="STATUS"></a>**STATUS** | — |
| `0x04` | <a id="IRQ_CTRL"></a>**IRQ_CTRL** | — |
| `0x05` | <a id="IRQ_STAT__R_"></a>**IRQ_STAT (R)** | — |
| `0x10` | <a id="TIMER_LO"></a>**TIMER_LO** | — |
| `0x11` | <a id="TIMER_HI"></a>**TIMER_HI** | — |

**CTRL** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ENABLE"></a>**ENABLE** | [0] | 1 | Enable MS2 |

**VOL_L** (`0x01`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VOL_L"></a>**VOL_L** | [7:0] | 8 | Global left volume |

**VOL_R** (`0x02`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VOL_R"></a>**VOL_R** | [7:0] | 8 | Global right volume |

**STATUS** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="PLAYING_CH"></a>**PLAYING_CH** | [7:4] | 4 | Playing per channel (read) |
| <a id="EOF_CH"></a>**EOF_CH** | [3:0] | 4 | EOF per channel (read) |
| <a id="CLR_EOF"></a>**CLR_EOF** | [3:0] | 4 | Clear EOF (write) |

**IRQ_CTRL** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="TMR_IRQ"></a>**TMR_IRQ** | [1] | 1 | Timer IRQ enable |
| <a id="EOF_IRQ"></a>**EOF_IRQ** | [0] | 1 | EOF IRQ enable |

**IRQ_STAT (R)** (`0x05`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="TMR_PEND"></a>**TMR_PEND** | [1] | 1 | Timer pending |
| <a id="EOF_PEND"></a>**EOF_PEND** | [0] | 1 | EOF pending |

**TIMER_LO** (`0x10`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="TMR_LO"></a>**TMR_LO** | [7:0] | 8 | Timer period low |

**TIMER_HI** (`0x11`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="TMR_HI"></a>**TMR_HI** | [7:0] | 8 | Timer period high |
