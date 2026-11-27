**SysDMA bus load of one duplex SPI slot**

| SCK | One slot, duplex | Four slots, duplex |
| --- | --- | --- |
| 12 MHz | <a id="3.0_MB_s"></a>**3.0 MB/s** | 12 MB/s, does not fit |
| 4 MHz | <a id="1.0_MB_s"></a>**1.0 MB/s** | 4 MB/s, does not fit the sustained estimate |
| 2 MHz | <a id="0.5_MB_s"></a>**0.5 MB/s** | 2 MB/s, fits the sustained estimate |
| 1 MHz | <a id="0.25_MB_s"></a>**0.25 MB/s** | 1 MB/s |

**Notes:**

- Load = 2 memory accesses per byte (read TX buffer, write RX buffer) = SCK_MHz / 4 MB/s per duplex slot; half that in TX_ONLY or RX_ONLY.
- The SPI side does not use the 8-bit bus: FIFOs connect to SysDMA through an internal port.
- If DMA cannot keep up, SCK stops at a byte boundary (STALL) instead of losing data.
