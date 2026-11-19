**Slot control registers**

| Offset | Name | Access | Description |
| --- | --- | --- | --- |
| `0x00` | <a id="SLOT0_CTRL"></a>**SLOT0_CTRL** | rw | Slot 0 control |
| `0x01` | <a id="SLOT1_CTRL"></a>**SLOT1_CTRL** | rw | Slot 1 control |
| `0x02` | <a id="SLOT2_CTRL"></a>**SLOT2_CTRL** | rw | Slot 2 control |
| `0x03` | <a id="SLOT3_CTRL"></a>**SLOT3_CTRL** | rw | Slot 3 control |
| `0x04` | <a id="SLOT0_STAT"></a>**SLOT0_STAT** | rw | Slot 0 status |
| `0x05` | <a id="SLOT1_STAT"></a>**SLOT1_STAT** | rw | Slot 1 status |
| `0x06` | <a id="SLOT2_STAT"></a>**SLOT2_STAT** | rw | Slot 2 status |
| `0x07` | <a id="SLOT3_STAT"></a>**SLOT3_STAT** | rw | Slot 3 status |

**SLOT0_CTRL** (`0x00`)

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:3] | 5 | — | — | Reserved |
| <a id="EN12"></a>**EN12** | [2] | 1 | rw | 0 | Enable ±12 V (allowed only after ID_CHECK) |
| <a id="RST_REL"></a>**RST_REL** | [1] | 1 | rw | 0 | 1 = release PERIPH_RST_N |
| <a id="EN3V3"></a>**EN3V3** | [0] | 1 | rw | 0 | Enable slot +3.3 V |

**SLOT1_CTRL** (`0x01`)

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:3] | 5 | — | — | Reserved |
| <a id="EN12"></a>**EN12** | [2] | 1 | rw | 0 | Enable ±12 V (allowed only after ID_CHECK) |
| <a id="RST_REL"></a>**RST_REL** | [1] | 1 | rw | 0 | 1 = release PERIPH_RST_N |
| <a id="EN3V3"></a>**EN3V3** | [0] | 1 | rw | 0 | Enable slot +3.3 V |

**SLOT2_CTRL** (`0x02`)

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:3] | 5 | — | — | Reserved |
| <a id="EN12"></a>**EN12** | [2] | 1 | rw | 0 | Enable ±12 V (allowed only after ID_CHECK) |
| <a id="RST_REL"></a>**RST_REL** | [1] | 1 | rw | 0 | 1 = release PERIPH_RST_N |
| <a id="EN3V3"></a>**EN3V3** | [0] | 1 | rw | 0 | Enable slot +3.3 V |

**SLOT3_CTRL** (`0x03`)

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:3] | 5 | — | — | Reserved |
| <a id="EN12"></a>**EN12** | [2] | 1 | rw | 0 | Enable ±12 V (allowed only after ID_CHECK) |
| <a id="RST_REL"></a>**RST_REL** | [1] | 1 | rw | 0 | 1 = release PERIPH_RST_N |
| <a id="EN3V3"></a>**EN3V3** | [0] | 1 | rw | 0 | Enable slot +3.3 V |

**SLOT0_STAT** (`0x04`)

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:6] | 2 | — | — | Reserved |
| <a id="INT"></a>**INT** | [5] | 1 | ro | 0 | INT_N level (1 = request) |
| <a id="READY"></a>**READY** | [4] | 1 | rw | 0 | Software marked the module as ready |
| <a id="FAULT"></a>**FAULT** | [3] | 1 | w1c | 0 | Overcurrent protection tripped |
| <a id="PG12"></a>**PG12** | [2] | 1 | ro | 0 | ±12 V within range |
| <a id="PG3V3"></a>**PG3V3** | [1] | 1 | ro | 0 | +3.3 V within range |
| <a id="PRESENT"></a>**PRESENT** | [0] | 1 | ro | 0 | DETECT_N == 0 |

**SLOT1_STAT** (`0x05`)

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:6] | 2 | — | — | Reserved |
| <a id="INT"></a>**INT** | [5] | 1 | ro | 0 | INT_N level (1 = request) |
| <a id="READY"></a>**READY** | [4] | 1 | rw | 0 | Software marked the module as ready |
| <a id="FAULT"></a>**FAULT** | [3] | 1 | w1c | 0 | Overcurrent protection tripped |
| <a id="PG12"></a>**PG12** | [2] | 1 | ro | 0 | ±12 V within range |
| <a id="PG3V3"></a>**PG3V3** | [1] | 1 | ro | 0 | +3.3 V within range |
| <a id="PRESENT"></a>**PRESENT** | [0] | 1 | ro | 0 | DETECT_N == 0 |

**SLOT2_STAT** (`0x06`)

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:6] | 2 | — | — | Reserved |
| <a id="INT"></a>**INT** | [5] | 1 | ro | 0 | INT_N level (1 = request) |
| <a id="READY"></a>**READY** | [4] | 1 | rw | 0 | Software marked the module as ready |
| <a id="FAULT"></a>**FAULT** | [3] | 1 | w1c | 0 | Overcurrent protection tripped |
| <a id="PG12"></a>**PG12** | [2] | 1 | ro | 0 | ±12 V within range |
| <a id="PG3V3"></a>**PG3V3** | [1] | 1 | ro | 0 | +3.3 V within range |
| <a id="PRESENT"></a>**PRESENT** | [0] | 1 | ro | 0 | DETECT_N == 0 |

**SLOT3_STAT** (`0x07`)

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:6] | 2 | — | — | Reserved |
| <a id="INT"></a>**INT** | [5] | 1 | ro | 0 | INT_N level (1 = request) |
| <a id="READY"></a>**READY** | [4] | 1 | rw | 0 | Software marked the module as ready |
| <a id="FAULT"></a>**FAULT** | [3] | 1 | w1c | 0 | Overcurrent protection tripped |
| <a id="PG12"></a>**PG12** | [2] | 1 | ro | 0 | ±12 V within range |
| <a id="PG3V3"></a>**PG3V3** | [1] | 1 | ro | 0 | +3.3 V within range |
| <a id="PRESENT"></a>**PRESENT** | [0] | 1 | ro | 0 | DETECT_N == 0 |
