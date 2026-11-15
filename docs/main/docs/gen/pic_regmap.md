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
| <a id="VEC"></a>**VEC** | [7:0] | 8 | Base vector for IM 2 (default 0xFF) |

**STATUS_L** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ_0_7"></a>**IRQ_0_7** | [7:0] | 8 | Status, lines 0–7 |

**STATUS_H** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ_8_15"></a>**IRQ_8_15** | [7:0] | 8 | Status, lines 8–15 |

**PENDING_L** (`0x05`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ_0_7"></a>**IRQ_0_7** | [7:0] | 8 | Pending, lines 0–7 |

**PENDING_H** (`0x06`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="IRQ_8_15"></a>**IRQ_8_15** | [7:0] | 8 | Pending, lines 8–15 |

**CLEAR_L** (`0x07`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="CLR_0_7"></a>**CLR_0_7** | [7:0] | 8 | Clear pending, lines 0–7 |

**CLEAR_H** (`0x08`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="CLR_8_15"></a>**CLR_8_15** | [7:0] | 8 | Clear pending, lines 8–15 |
