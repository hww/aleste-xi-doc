# Rev. C: Channel Registers Map (Base 0x20/0x30/0x40/0x50)

![Rev. C: Channel Registers Map (Base 0x20/0x30/0x40/0x50)](gen/ms2c_channel_map.svg)

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
