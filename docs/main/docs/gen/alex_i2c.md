**I2C controller registers (one controller, four-slot multiplexer)**

| Offset | Name | Access | Description |
| --- | --- | --- | --- |
| `0x00` | <a id="I2C_DATA"></a>**I2C_DATA** | rw | Byte to transmit / received byte |
| `0x01` | <a id="I2C_CMD"></a>**I2C_CMD** | wo | Command: START, STOP, WR, RD, NACK |
| `0x02` | <a id="I2C_STATUS"></a>**I2C_STATUS** | rw | Status |
| `0x03` | <a id="I2C_CTRL"></a>**I2C_CTRL** | rw | Slot select and enable |

**I2C_DATA** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="D"></a>**D** | [7:0] | 8 | — |

**I2C_CMD** (`0x01`)

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:5] | 3 | — | — | Reserved |
| <a id="NACK"></a>**NACK** | [4] | 1 | wo | 0 | With RD: answer NACK (last byte) |
| <a id="RD"></a>**RD** | [3] | 1 | wo | 0 | Receive a byte into I2C_DATA |
| <a id="WR"></a>**WR** | [2] | 1 | wo | 0 | Transmit the byte in I2C_DATA |
| <a id="STOP"></a>**STOP** | [1] | 1 | wo | 0 | Issue STOP |
| <a id="START"></a>**START** | [0] | 1 | wo | 0 | Issue START (or repeated START) |

**I2C_STATUS** (`0x02`)

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:3] | 5 | — | — | Reserved |
| <a id="DONE"></a>**DONE** | [2] | 1 | w1c | 0 | Byte completed |
| <a id="NACK"></a>**NACK** | [1] | 1 | ro | 0 | Last answer from the module was NACK |
| <a id="BUSY"></a>**BUSY** | [0] | 1 | ro | 0 | Operation in progress |

**I2C_CTRL** (`0x03`)

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:4] | 4 | — | — | Reserved |
| <a id="IRQE"></a>**IRQE** | [3] | 1 | rw | 0 | Interrupt on DONE |
| <a id="EN"></a>**EN** | [2] | 1 | rw | 0 | Enable the controller |
| <a id="SLOT"></a>**SLOT** | [1:0] | 2 | rw | 0x0 | Slot number for the multiplexer (0..3) |
