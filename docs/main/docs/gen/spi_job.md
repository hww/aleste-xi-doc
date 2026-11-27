**SPI job controller**

| State | Output | Description |
| --- | --- | --- |
| <a id="IDLE"></a>**IDLE** (initial) | sck=0 | No job |
| <a id="CS_SETUP"></a>**CS_SETUP** | cs_n=0 | Asserting CS_N (FIRST) |
| <a id="WAIT_DREQ"></a>**WAIT_DREQ** | sck=0 | Waiting for the module |
| <a id="SHIFT"></a>**SHIFT** | sck=run | Shifting one byte per 8 SCK clocks |
| <a id="STALL"></a>**STALL** | sck=0 stall=1 | TX FIFO empty or RX FIFO full: SCK held at a byte boundary |
| <a id="CS_RELEASE"></a>**CS_RELEASE** | cs_n=1 | Releasing CS_N (LAST) |
| <a id="DONE"></a>**DONE** | done=1 | Job complete |

| From | To | Condition | Action |
| --- | --- | --- | --- |
| IDLE | CS_SETUP | START & FIRST | — |
| IDLE | WAIT_DREQ | START & !FIRST & WAIT_DREQ | — |
| IDLE | SHIFT | START & !FIRST & !WAIT_DREQ | — |
| CS_SETUP | WAIT_DREQ | WAIT_DREQ | — |
| CS_SETUP | SHIFT | !WAIT_DREQ | — |
| WAIT_DREQ | SHIFT | DREQ_N == 0 | — |
| WAIT_DREQ | IDLE | ABORT | — |
| SHIFT | SHIFT | bytes_left > 0 & fifo_ok | shift byte |
| SHIFT | STALL | tx_empty \| rx_full | — |
| SHIFT | CS_RELEASE | bytes_left == 0 & LAST | — |
| SHIFT | DONE | bytes_left == 0 & !LAST | — |
| SHIFT | IDLE | ABORT | — |
| STALL | SHIFT | fifo_ok | — |
| STALL | IDLE | ABORT | — |
| CS_RELEASE | DONE | — | — |
| DONE | IDLE | — | — |
