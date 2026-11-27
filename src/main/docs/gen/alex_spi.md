**SPI controller registers (four instances, one per slot)**

| Offset | Name | Access | Reset | Description |
| --- | --- | --- | --- | --- |
| `0x00` | <a id="SPI_DATA"></a>**SPI_DATA** | rw | — | Direct CPU access: a write pushes the TX FIFO, a read pops the RX FIFO |
| `0x01` | <a id="SPI_CMD"></a>**SPI_CMD** | wo | — | Job command |
| `0x02` | <a id="SPI_LEN_L"></a>**SPI_LEN_L** | rw | — | Job length in bytes [7:0] |
| `0x03` | <a id="SPI_LEN_H"></a>**SPI_LEN_H** | rw | — | Job length in bytes [15:8] |
| `0x04` | <a id="SPI_CTRL"></a>**SPI_CTRL** | rw | — | Control |
| `0x05` | <a id="SPI_STATUS"></a>**SPI_STATUS** | rw | — | Status |
| `0x06` | <a id="SPI_FILL"></a>**SPI_FILL** | rw | 0xFF | Byte sent on MOSI in RX_ONLY mode |
| `0x07` | <a id="SPI_RSV"></a>**SPI_RSV** | ro | — | Reserved |

**SPI_DATA** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="D"></a>**D** | [7:0] | 8 | — |

**SPI_CMD** (`0x01`)

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7] | 1 | — | — | Reserved |
| <a id="ABORT"></a>**ABORT** | [6] | 1 | wo | 0 | Abort the job and flush both FIFOs |
| <a id="START"></a>**START** | [5] | 1 | wo | 0 | Start the job |
| <a id="WAIT_DREQ"></a>**WAIT_DREQ** | [4] | 1 | wo | 0 | Wait for GPIO0_DREQ_N = 0 before the first byte |
| <a id="LAST"></a>**LAST** | [3] | 1 | wo | 0 | Release CS_N after the last byte (packet end) |
| <a id="FIRST"></a>**FIRST** | [2] | 1 | wo | 0 | Assert CS_N before the first byte (packet start) |
| <a id="MODE"></a>**MODE** | [1:0] | 2 | wo | 0x0 | Transfer mode [`alex_spi_modes`](alex_spi_modes.md) |

**SPI_LEN_L** (`0x02`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="LEN"></a>**LEN** | [7:0] | 8 | — |

**SPI_LEN_H** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="LEN"></a>**LEN** | [7:0] | 8 | — |

**SPI_CTRL** (`0x04`)

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="IRQE"></a>**IRQE** | [7] | 1 | rw | 0 | Interrupt on DONE |
| <a id="CPHA"></a>**CPHA** | [6] | 1 | rw | 0 | Clock phase |
| <a id="CPOL"></a>**CPOL** | [5] | 1 | rw | 0 | Clock polarity |
| <a id="DIV"></a>**DIV** | [4:1] | 4 | rw | 0xF | SCK divider: f = f_sys / (2 * (DIV + 1)) |
| <a id="EN"></a>**EN** | [0] | 1 | rw | 0 | Enable the controller |

**SPI_STATUS** (`0x05`)

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:5] | 3 | — | — | Reserved |
| <a id="CSA"></a>**CSA** | [4] | 1 | ro | 0 | CS_N is currently asserted |
| <a id="DREQ"></a>**DREQ** | [3] | 1 | ro | 0 | GPIO0_DREQ_N level (0 = module ready) |
| <a id="STALL"></a>**STALL** | [2] | 1 | w1c | 0 | SCK was stopped at least once because DMA could not keep up |
| <a id="DONE"></a>**DONE** | [1] | 1 | w1c | 0 | Job finished and the RX FIFO has been drained to memory |
| <a id="BUSY"></a>**BUSY** | [0] | 1 | ro | 0 | Job in progress |

**SPI_FILL** (`0x06`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="FILL"></a>**FILL** | [7:0] | 8 | — |

**SPI_RSV** (`0x07`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:0] | 8 | Reserved |
