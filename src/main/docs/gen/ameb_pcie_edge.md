**PCIe x1 — Edge connector**

*edge, 2 row(s) × 18, pitch 2.54 mm, numbering rowwise, pin 1 at top-left, key slot after position 11, drawn rotated 0°*

| Pin | Signal | Dir | Group | Description |
| --- | --- | --- | --- | --- |
| B1 | <a id="_12V_1_"></a>**+12V(1)** | power | power_analog | Analog power +12 V |
| B2 | <a id="_12V_2_"></a>**+12V(2)** | power | power_analog | Analog power +12 V |
| B3 | **NC_B3** | NC | nc | In PCIe this is +12 V; not connected |
| B4 | <a id="AGND_1_"></a>**AGND(1)** | gnd | ground_analog | — |
| B5 | <a id="I2C_SCL"></a>**I2C_SCL** | inout | i2c | Matches SMCLK in PCIe |
| B6 | <a id="I2C_SDA"></a>**I2C_SDA** | inout | i2c | Matches SMDAT in PCIe |
| B7 | <a id="DGND_1_"></a>**DGND(1)** | gnd | ground_digital | — |
| B8 | <a id="_3V3_1_"></a>**+3V3(1)** | power | power_digital | Digital power +3.3 V |
| B9 | <a id="SPI_CS_N"></a>**SPI_CS_N** | out | spi | Module select |
| B10 | **NC_B10** | NC | nc | In PCIe this is +3.3 V aux; not connected |
| B11 | <a id="INT_N"></a>**INT_N** | in | control | Interrupt request from the module |
| B12 | <a id="SPI_SCK"></a>**SPI_SCK** | out | spi | — |
| B13 | <a id="DGND"></a>**DGND** | gnd | ground_digital | — |
| B14 | <a id="SPI_MISO"></a>**SPI_MISO** | in | spi | — |
| B15 | <a id="DGND_2_"></a>**DGND(2)** | gnd | ground_digital | — |
| B16 | <a id="AUDIO_DIN"></a>**AUDIO_DIN** | in | audio | Audio module → host |
| B17 | <a id="DGND_3_"></a>**DGND(3)** | gnd | ground_digital | — |
| B18 | <a id="AUDIO_BCLK"></a>**AUDIO_BCLK** | out | audio | 24.576 MHz |
| A1 | <a id="DETECT_N"></a>**DETECT_N** | in | control | Module is inserted (shorted to DGND on the module) |
| A2 | **NC_A2** | NC | nc | In PCIe this is +12 V; not connected |
| A3 | **NC_A3** | NC | nc | In PCIe this is +12 V; not connected |
| A4 | <a id="AGND_2_"></a>**AGND(2)** | gnd | ground_analog | — |
| A5 | <a id="-12V"></a>**-12V** | power | power_analog | Analog power −12 V |
| A6 | <a id="AGND_3_"></a>**AGND(3)** | gnd | ground_analog | — |
| A7 | <a id="GPIO0_DREQ_N"></a>**GPIO0_DREQ_N** | in | gpio | Module is ready for data exchange (DMA request) |
| A8 | <a id="GPIO1"></a>**GPIO1** | inout | gpio | Module-specific |
| A9 | <a id="_3V3_2_"></a>**+3V3(2)** | power | power_digital | — |
| A10 | <a id="_3V3_3_"></a>**+3V3(3)** | power | power_digital | — |
| A11 | <a id="PERIPH_RST_N"></a>**PERIPH_RST_N** | out | control | Module reset in the slot |
| A12 | <a id="DGND_4_"></a>**DGND(4)** | gnd | ground_digital | — |
| A13 | <a id="SPI_MOSI"></a>**SPI_MOSI** | out | spi | — |
| A14 | <a id="DGND_5_"></a>**DGND(5)** | gnd | ground_digital | — |
| A15 | <a id="AUDIO_DOUT"></a>**AUDIO_DOUT** | out | audio | Audio host → module |
| A16 | <a id="DGND_6_"></a>**DGND(6)** | gnd | ground_digital | — |
| A17 | <a id="AUDIO_FS"></a>**AUDIO_FS** | out | audio | Frame sync, 48 kHz |
| A18 | <a id="AUDIO_MCLK"></a>**AUDIO_MCLK** | out | audio | 12.288 MHz; next to BCLK with no ground between them |
