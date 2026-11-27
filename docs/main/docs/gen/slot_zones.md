**Connector zones and placement rules**

| Pos. | Zone | Contents |
| --- | --- | --- |
| 1-3 | <a id="Analog_block"></a>**Analog block** | +12 V (B2) opposite -12 V (A2), AGND on both sides (B1, B3, A1, A3) |
| 4-6 | <a id="Digital_power"></a>**Digital power** | +3.3 V (B5, A4, A5), DGND (B4, A6), reserve (B6) |
| 7-9 | <a id="Management"></a>**Management** | I2C (B7, A7), DETECT_N (B8), PERIPH_RST_N (A8), INT_N (B9), GPIO1 (A9) |
| 10-11 | <a id="SPI_handshake"></a>**SPI handshake** | DREQ_N (B10), CS_N (B11), reserve (A10, A11), next to the key |
| 12-18 | <a id="Fast_path"></a>**Fast path** | SCK, MOSI, MISO, BCLK, FS, MCLK, DOUT, DIN with six DGND; every clock line sits between DGND contacts |

**Notes:**

- The analog block and the fast path are at opposite ends of the connector, with the key between them.
- Each clock line (BCLK, FS, MCLK) is opposite a DGND contact on the other face of the module.
- SPI_SCK opposite SPI_MOSI is the only exception; without MCLK zone 2 becomes a perfect signal/ground checkerboard.
- The +/-12 V rails are a symmetric pair, one contact each, enough for the planning current.
