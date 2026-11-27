**PIC Register Map (lx_sys.sv)**

| Offset | Name | Access | Description |
| --- | --- | --- | --- |
| `0x00` | <a id="COMMAND"></a>**COMMAND** | w | — |
| `0x01` | <a id="CLAIM"></a>**CLAIM** | r | — |
| `0x02` | <a id="VECTOR"></a>**VECTOR** | rw | — |
| `0x03` | <a id="PENDING_L"></a>**PENDING_L** | r | — |
| `0x04` | <a id="PENDING_H"></a>**PENDING_H** | r | — |
| `0x05` | <a id="REPEAT_L"></a>**REPEAT_L** | r | — |
| `0x06` | <a id="REPEAT_H"></a>**REPEAT_H** | r | — |
| `0x07` | <a id="IN_SERVICE_L"></a>**IN_SERVICE_L** | r | — |
| `0x08` | <a id="IN_SERVICE_H"></a>**IN_SERVICE_H** | r | — |
| `0x09` | <a id="ENABLE_L"></a>**ENABLE_L** | r | — |
| `0x0A` | <a id="ENABLE_H"></a>**ENABLE_H** | r | — |
| `0x0B` | <a id="STATUS_L"></a>**STATUS_L** | r | — |
| `0x0C` | <a id="STATUS_H"></a>**STATUS_H** | r | — |

**COMMAND** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="PAYLOAD"></a>**PAYLOAD** | [7:0] | 8 | bit7=0: {opcode[6:4], channel[3:0]}; bit7=1: {1, prio[6:4], channel[3:0]}. Supervisor only. |

**CLAIM** (`0x01`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VALID"></a>**VALID** | [7] | 1 | A channel was captured (latch valid) |
| <a id="REPEAT"></a>**REPEAT** | [6] | 1 | Captured channel had REPEAT set |
| <a id="RSV"></a>**RSV** | [5:4] | 2 | Reserved |
| <a id="CHANNEL"></a>**CHANNEL** | [3:0] | 4 | Captured channel ID (0..15) |

**VECTOR** (`0x02`)

| Field | Bits | Width | Reset | Description |
| --- | --- | --- | --- | --- |
| <a id="VEC"></a>**VEC** | [7:0] | 8 | 0xFF | Base vector for IM 2 (reset = 0xFF, RST 38h). Write: supervisor only. |

**PENDING_L** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ_0_7"></a>**IRQ_0_7** | [7:0] | 8 | Pending, lines 0–7 |

**PENDING_H** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ_8_15"></a>**IRQ_8_15** | [7:0] | 8 | Pending, lines 8–15 |

**REPEAT_L** (`0x05`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="REP_0_7"></a>**REP_0_7** | [7:0] | 8 | Overrun flag, lines 0–7 |

**REPEAT_H** (`0x06`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="REP_8_15"></a>**REP_8_15** | [7:0] | 8 | Overrun flag, lines 8–15 |

**IN_SERVICE_L** (`0x07`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ISR_0_7"></a>**ISR_0_7** | [7:0] | 8 | In service, lines 0–7 |

**IN_SERVICE_H** (`0x08`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ISR_8_15"></a>**ISR_8_15** | [7:0] | 8 | In service, lines 8–15 |

**ENABLE_L** (`0x09`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="EN_0_7"></a>**EN_0_7** | [7:0] | 8 | Enabled, lines 0–7 |

**ENABLE_H** (`0x0A`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="EN_8_15"></a>**EN_8_15** | [7:0] | 8 | Enabled, lines 8–15 |

**STATUS_L** (`0x0B`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ELIG_0_7"></a>**ELIG_0_7** | [7:0] | 8 | PENDING & ENABLE & ~IN_SERVICE, lines 0–7 (drives INT) |

**STATUS_H** (`0x0C`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ELIG_8_15"></a>**ELIG_8_15** | [7:0] | 8 | PENDING & ENABLE & ~IN_SERVICE, lines 8–15 |
