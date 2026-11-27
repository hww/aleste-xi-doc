**SPIn_STATUS · 8 bits**

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:5] | 3 | — | — | Reserved |
| <a id="CSA"></a>**CSA** | [4] | 1 | ro | 0 | CS_N is currently asserted |
| <a id="DREQ"></a>**DREQ** | [3] | 1 | ro | 0 | GPIO0_DREQ_N level (0 = module ready) |
| <a id="STALL"></a>**STALL** | [2] | 1 | w1c | 0 | SCK was stopped at least once because DMA could not keep up |
| <a id="DONE"></a>**DONE** | [1] | 1 | w1c | 0 | Job finished and the RX FIFO has been drained to memory |
| <a id="BUSY"></a>**BUSY** | [0] | 1 | ro | 0 | Job in progress |
