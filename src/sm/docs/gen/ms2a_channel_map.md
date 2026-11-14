# Rev. A: Channel Registers Map (Base 0x20/0x30/0x40/0x50)

![Rev. A: Channel Registers Map (Base 0x20/0x30/0x40/0x50)](gen/ms2a_channel_map.svg)

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
