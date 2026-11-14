# Rev. A: Global Registers Map

![Rev. A: Global Registers Map](gen/ms2a_global_map.svg)

| Offset | Name | Description |
| --- | --- | --- |
| `0x00` | <a id="GLOBAL_CR"></a>**GLOBAL_CR** | — |
| `0x01` | <a id="GLOBAL_VOL_L"></a>**GLOBAL_VOL_L** | — |
| `0x02` | <a id="GLOBAL_VOL_R"></a>**GLOBAL_VOL_R** | — |
| `0x03` | <a id="STATUS"></a>**STATUS** | — |
| `0x04` | <a id="IRQ_CTRL"></a>**IRQ_CTRL** | — |
| `0x05` | <a id="DMA_ERR_CLR"></a>**DMA_ERR_CLR** | — |
| `0x10` | <a id="TIMER_VAL"></a>**TIMER_VAL** | — |
| `0x11` | <a id="TIMER_VAL_H"></a>**TIMER_VAL_H** | — |
| `0x12` | <a id="TIMER_CTRL"></a>**TIMER_CTRL** | — |

**GLOBAL_CR** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RST"></a>**RST** | [1] | 1 | Reset |
| <a id="EN"></a>**EN** | [0] | 1 | Enable |

**GLOBAL_VOL_L** (`0x01`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VOL_L"></a>**VOL_L** | [7:0] | 8 | Global left volume |

**GLOBAL_VOL_R** (`0x02`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VOL_R"></a>**VOL_R** | [7:0] | 8 | Global right volume |

**STATUS** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="TMR_IRQ"></a>**TMR_IRQ** | [5] | 1 | Timer IRQ |
| <a id="DMA_ERR"></a>**DMA_ERR** | [4] | 1 | DMA error |
| <a id="EOF"></a>**EOF** | [3] | 1 | Any EOF |
| <a id="ERR"></a>**ERR** | [2] | 1 | Any error |
| <a id="CH_ACT"></a>**CH_ACT** | [1] | 1 | Any channel active |
| <a id="ACT"></a>**ACT** | [0] | 1 | Global active |

**IRQ_CTRL** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="DMA_NMI"></a>**DMA_NMI** | [1] | 1 | DMA error NMI enable |
| <a id="TMR_EN"></a>**TMR_EN** | [0] | 1 | Timer IRQ enable |

**DMA_ERR_CLR** (`0x05`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="CLR"></a>**CLR** | [0] | 1 | Write 1 to clear |

**TIMER_VAL** (`0x10`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VAL_L"></a>**VAL_L** | [7:0] | 8 | Timer value low |

**TIMER_VAL_H** (`0x11`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VAL_H"></a>**VAL_H** | [7:0] | 8 | Timer value high |

**TIMER_CTRL** (`0x12`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="CTRL"></a>**CTRL** | [7:0] | 8 | Timer control |
