**Slot SPI controller registers (4 instances)**

| Offset | Name | Access | Description |
| --- | --- | --- | --- |
| `0x00` | <a id="SPI_DATA"></a>**SPI_DATA** | rw | A write starts a byte transfer; a read returns the received byte |
| `0x01` | <a id="SPI_CTRL"></a>**SPI_CTRL** | rw | Control |
| `0x02` | <a id="SPI_STATUS"></a>**SPI_STATUS** | ro | Status |
| `0x03` | <a id="SPI_RSV"></a>**SPI_RSV** | ro | Reserved (DMA: address and length — TBD) |

**SPI_DATA** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="D"></a>**D** | [7:0] | 8 | — |

**SPI_CTRL** (`0x01`)

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:6] | 2 | — | — | Reserved |
| <a id="CSA"></a>**CSA** | [5] | 1 | rw | 0 | 1 = keep CS_N asserted |
| <a id="DIV"></a>**DIV** | [4:1] | 4 | rw | 0xF | SCK divider: f = f_sys / (2·(DIV+1)) |
| <a id="EN"></a>**EN** | [0] | 1 | rw | 0 | Enable the slot controller |

**SPI_STATUS** (`0x02`)

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:3] | 5 | — | — | Reserved |
| <a id="DREQ"></a>**DREQ** | [2] | 1 | ro | 0 | GPIO0_DREQ_N level (0 = module ready) |
| <a id="RXV"></a>**RXV** | [1] | 1 | ro | 0 | Received byte ready |
| <a id="BUSY"></a>**BUSY** | [0] | 1 | ro | 0 | Byte transfer in progress |
