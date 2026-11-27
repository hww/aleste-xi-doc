**SPI transfer modes (SPI_CMD.MODE)**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="TX_ONLY"></a>**TX_ONLY** | Transmit only; received bytes are discarded (one DMA stream) |
| 1 | <a id="RX_ONLY"></a>**RX_ONLY** | Receive only; SPI_FILL is sent on MOSI (one DMA stream) |
| 2 | <a id="DUPLEX"></a>**DUPLEX** | Full duplex: TX buffer out, RX buffer in (two DMA streams) |
| 3 | <a id="reserved"></a>**reserved** | Reserved |
