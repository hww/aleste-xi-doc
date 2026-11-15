# LX-GPU — описание архитектуры

## Rev. A: Channel Registers Map (Base 0x20/0x30/0x40/0x50)

![Rev. A: Channel Registers Map (Base 0x20/0x30/0x40/0x50)](gen/ms2a_channel_map.svg)

*Figure 1 — Rev. A: Channel Registers Map (Base 0x20/0x30/0x40/0x50)*

**Table 1 — Rev. A: Channel Registers Map (Base 0x20/0x30/0x40/0x50)**

| Offset | Name | Description |
| --- | --- | --- |
| `0x00` | <a id="CH_CTRL"></a>**CH_CTRL** | — |
| `0x01` | <a id="START_ADDR_0"></a>**START_ADDR_0** | — |
| `0x02` | <a id="START_ADDR_1"></a>**START_ADDR_1** | — |
| `0x03` | <a id="START_ADDR_2"></a>**START_ADDR_2** | — |
| `0x04` | <a id="END_ADDR_0"></a>**END_ADDR_0** | — |
| `0x05` | <a id="END_ADDR_1"></a>**END_ADDR_1** | — |
| `0x06` | <a id="END_ADDR_2"></a>**END_ADDR_2** | — |
| `0x07` | <a id="LOOP_START_0"></a>**LOOP_START_0** | — |
| `0x08` | <a id="LOOP_START_1"></a>**LOOP_START_1** | — |
| `0x09` | <a id="LOOP_START_2"></a>**LOOP_START_2** | — |
| `0x0A` | <a id="LOOP_END_0"></a>**LOOP_END_0** | — |
| `0x0B` | <a id="LOOP_END_1"></a>**LOOP_END_1** | — |
| `0x0C` | <a id="LOOP_END_2"></a>**LOOP_END_2** | — |
| `0x0D` | <a id="STEP_0"></a>**STEP_0** | — |
| `0x0E` | <a id="STEP_1"></a>**STEP_1** | — |
| `0x0F` | <a id="STEP_2"></a>**STEP_2** | — |

**CH_CTRL** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VOL_L"></a>**VOL_L** | [7:4] | 4 | Volume L (4-bit) |
| <a id="IRQ"></a>**IRQ** | [3] | 1 | IRQ on EOF |
| <a id="VOL_R"></a>**VOL_R** | [3:0] | 4 | Volume R (4-bit) |
| <a id="PP"></a>**PP** | [2] | 1 | Ping-pong |
| <a id="LOOP"></a>**LOOP** | [1] | 1 | Loop |
| <a id="EN"></a>**EN** | [0] | 1 | Enable |

**START_ADDR_0** (`0x01`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Start address [7:0] |

**START_ADDR_1** (`0x02`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Start address [15:8] |

**START_ADDR_2** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Start address [23:16] |

**END_ADDR_0** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | End address [7:0] |

**END_ADDR_1** (`0x05`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | End address [15:8] |

**END_ADDR_2** (`0x06`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | End address [23:16] |

**LOOP_START_0** (`0x07`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Loop start [7:0] |

**LOOP_START_1** (`0x08`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Loop start [15:8] |

**LOOP_START_2** (`0x09`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Loop start [23:16] |

**LOOP_END_0** (`0x0A`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Loop end [7:0] |

**LOOP_END_1** (`0x0B`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Loop end [15:8] |

**LOOP_END_2** (`0x0C`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Loop end [23:16] |

**STEP_0** (`0x0D`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="STEP"></a>**STEP** | [7:0] | 8 | Step fraction [7:0] |

**STEP_1** (`0x0E`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="STEP"></a>**STEP** | [7:0] | 8 | Step fraction [15:8] |

**STEP_2** (`0x0F`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="STEP"></a>**STEP** | [7:0] | 8 | Step integer [23:16] |


[Таблица](gen/ms2a_channel_map.md)

## Rev. A: Global Registers Map

![Rev. A: Global Registers Map](gen/ms2a_global_map.svg)

*Figure 2 — Rev. A: Global Registers Map*

**Table 2 — Rev. A: Global Registers Map**

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


[Таблица](gen/ms2a_global_map.md)

## Rev. C: Channel Registers Map (Base 0x20/0x30/0x40/0x50)

![Rev. C: Channel Registers Map (Base 0x20/0x30/0x40/0x50)](gen/ms2c_channel_map.svg)

*Figure 3 — Rev. C: Channel Registers Map (Base 0x20/0x30/0x40/0x50)*

**Table 3 — Rev. C: Channel Registers Map (Base 0x20/0x30/0x40/0x50)**

| Offset | Name | Description |
| --- | --- | --- |
| `0x00` | <a id="CTRL"></a>**CTRL** | — |
| `0x01` | <a id="START_0"></a>**START_0** | — |
| `0x02` | <a id="START_1"></a>**START_1** | — |
| `0x03` | <a id="START_2"></a>**START_2** | — |
| `0x04` | <a id="END_0"></a>**END_0** | — |
| `0x05` | <a id="END_1"></a>**END_1** | — |
| `0x06` | <a id="END_2"></a>**END_2** | — |
| `0x07` | <a id="LOOP_0"></a>**LOOP_0** | — |
| `0x08` | <a id="LOOP_1"></a>**LOOP_1** | — |
| `0x09` | <a id="LOOP_2"></a>**LOOP_2** | — |
| `0x0A` | <a id="VOL_L"></a>**VOL_L** | — |
| `0x0B` | <a id="VOL_R"></a>**VOL_R** | — |
| `0x0C` | <a id="STEP_0"></a>**STEP_0** | — |
| `0x0D` | <a id="STEP_1"></a>**STEP_1** | — |
| `0x0E` | <a id="STEP_2"></a>**STEP_2** | — |
| `0x0F` | <a id="Status"></a>**Status** | — |

**CTRL** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ"></a>**IRQ** | [3] | 1 | IRQ on EOF |
| <a id="16BIT"></a>**16BIT** | [2] | 1 | 16-bit samples |
| <a id="LOOP"></a>**LOOP** | [1] | 1 | Loop |
| <a id="PLAY"></a>**PLAY** | [0] | 1 | Play |

**START_0** (`0x01`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR_0"></a>**ADDR_0** | [7:0] | 8 | Start address [7:0] |

**START_1** (`0x02`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR_1"></a>**ADDR_1** | [7:0] | 8 | Start address [15:8] |

**START_2** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR_2"></a>**ADDR_2** | [7:0] | 8 | Start address [23:16] |

**END_0** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR_0"></a>**ADDR_0** | [7:0] | 8 | End address [7:0] |

**END_1** (`0x05`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR_1"></a>**ADDR_1** | [7:0] | 8 | End address [15:8] |

**END_2** (`0x06`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR_2"></a>**ADDR_2** | [7:0] | 8 | End address [23:16] |

**LOOP_0** (`0x07`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR_0"></a>**ADDR_0** | [7:0] | 8 | Loop address [7:0] |

**LOOP_1** (`0x08`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR_1"></a>**ADDR_1** | [7:0] | 8 | Loop address [15:8] |

**LOOP_2** (`0x09`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR_2"></a>**ADDR_2** | [7:0] | 8 | Loop address [23:16] |

**VOL_L** (`0x0A`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VOL_L"></a>**VOL_L** | [7:0] | 8 | Channel left volume |

**VOL_R** (`0x0B`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VOL_R"></a>**VOL_R** | [7:0] | 8 | Channel right volume |

**STEP_0** (`0x0C`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="FRAC_0"></a>**FRAC_0** | [7:0] | 8 | Step fraction [7:0] |

**STEP_1** (`0x0D`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="FRAC_1"></a>**FRAC_1** | [7:0] | 8 | Step fraction [15:8] |

**STEP_2** (`0x0E`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="INT"></a>**INT** | [7:0] | 8 | Step integer |

**Status** (`0x0F`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="POS_HI"></a>**POS_HI** | [7:4] | 4 | Position high byte |
| <a id="EOF"></a>**EOF** | [1] | 1 | EOF |
| <a id="PLAYING"></a>**PLAYING** | [0] | 1 | Playing |


[Таблица](gen/ms2c_channel_map.md)

## Rev. C: Global Registers Map

![Rev. C: Global Registers Map](gen/ms2c_global_map.svg)

*Figure 4 — Rev. C: Global Registers Map*

**Table 4 — Rev. C: Global Registers Map**

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


[Таблица](gen/ms2c_global_map.md)
