**PIC Register Map (wb_z80_pic.sv)**

| Offset | Name | Description |
| --- | --- | --- |
| `0x00` | <a id="MASK_L"></a>**MASK_L** | — |
| `0x01` | <a id="MASK_H"></a>**MASK_H** | — |
| `0x02` | <a id="VECTOR"></a>**VECTOR** | — |
| `0x03` | <a id="STATUS_L"></a>**STATUS_L** | — |
| `0x04` | <a id="STATUS_H"></a>**STATUS_H** | — |
| `0x05` | <a id="PENDING_L"></a>**PENDING_L** | — |
| `0x06` | <a id="PENDING_H"></a>**PENDING_H** | — |
| `0x07` | <a id="CLEAR_L"></a>**CLEAR_L** | — |
| `0x08` | <a id="CLEAR_H"></a>**CLEAR_H** | — |
| `0x09` | <a id="REPEAT_L"></a>**REPEAT_L** | — |
| `0x0A` | <a id="REPEAT_H"></a>**REPEAT_H** | — |
| `0x0B` | <a id="CLEAR_REPEAT_L"></a>**CLEAR_REPEAT_L** | — |
| `0x0C` | <a id="CLEAR_REPEAT_H"></a>**CLEAR_REPEAT_H** | — |

**MASK_L** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ_0_7"></a>**IRQ_0_7** | [7:0] | 8 | Mask, lines 0–7 (1 = enabled) |

**MASK_H** (`0x01`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ_8_15"></a>**IRQ_8_15** | [7:0] | 8 | Mask, lines 8–15 (1 = enabled) |

**VECTOR** (`0x02`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VEC"></a>**VEC** | [7:0] | 8 | Base vector for IM 2 (reset = 0xFF, RST 38h) |

**STATUS_L** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ_0_7"></a>**IRQ_0_7** | [7:0] | 8 | Status, lines 0–7 (pending & mask) |

**STATUS_H** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ_8_15"></a>**IRQ_8_15** | [7:0] | 8 | Status, lines 8–15 (pending & mask) |

**PENDING_L** (`0x05`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ_0_7"></a>**IRQ_0_7** | [7:0] | 8 | Pending, lines 0–7 (unmasked) |

**PENDING_H** (`0x06`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ_8_15"></a>**IRQ_8_15** | [7:0] | 8 | Pending, lines 8–15 (unmasked) |

**CLEAR_L** (`0x07`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="CLR_0_7"></a>**CLR_0_7** | [7:0] | 8 | Clear pending, lines 0–7 (write 1 = clear; set-dominant vs. new edge) |

**CLEAR_H** (`0x08`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="CLR_8_15"></a>**CLR_8_15** | [7:0] | 8 | Clear pending, lines 8–15 (write 1 = clear; set-dominant vs. new edge) |

**REPEAT_L** (`0x09`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="REP_0_7"></a>**REP_0_7** | [7:0] | 8 | Overrun flag, lines 0–7: a second request arrived while Pending=1 |

**REPEAT_H** (`0x0A`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="REP_8_15"></a>**REP_8_15** | [7:0] | 8 | Overrun flag, lines 8–15: a second request arrived while Pending=1 |

**CLEAR_REPEAT_L** (`0x0B`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="CLRREP_0_7"></a>**CLRREP_0_7** | [7:0] | 8 | Clear Repeat, lines 0–7 (write 1 = clear; set-dominant vs. new overrun) |

**CLEAR_REPEAT_H** (`0x0C`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="CLRREP_8_15"></a>**CLRREP_8_15** | [7:0] | 8 | Clear Repeat, lines 8–15 (write 1 = clear; set-dominant vs. new overrun) |
