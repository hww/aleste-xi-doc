**AMEB-36 slot connector (PCIe x1, 36 pins; key between positions 11 and 12)**

| Name | Pin | Dir | Width | Group | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="_12V_1_"></a>**+12V(1)** | B1 | power | 1 | power_analog | Analog power +12 V |
| <a id="_12V_2_"></a>**+12V(2)** | B2 | power | 1 | power_analog | Analog power +12 V |
| <a id="NC_B3"></a>**NC_B3** | B3 | nc | 1 | nc | In PCIe this is +12 V; not connected |
| <a id="AGND_1_"></a>**AGND(1)** | B4 | gnd | 1 | ground_analog | — |
| <a id="I2C_SCL"></a>**I2C_SCL** | B5 | inout | 1 | i2c | Matches SMCLK in PCIe |
| <a id="I2C_SDA"></a>**I2C_SDA** | B6 | inout | 1 | i2c | Matches SMDAT in PCIe |
| <a id="DGND_1_"></a>**DGND(1)** | B7 | gnd | 1 | ground_digital | — |
| <a id="_3V3_1_"></a>**+3V3(1)** | B8 | power | 1 | power_digital | Digital power +3.3 V |
| <a id="SPI_CS_N"></a>**~SPI_CS_N** | B9 | out | 1 | spi | Module select |
| <a id="NC_B10"></a>**NC_B10** | B10 | nc | 1 | nc | In PCIe this is +3.3 V aux; not connected |
| <a id="INT_N"></a>**~INT_N** | B11 | in | 1 | control | Interrupt request from the module |
| <a id="DETECT_N"></a>**~DETECT_N** | A1 | in | 1 | control | Module is inserted (shorted to DGND on the module) |
| <a id="NC_A2"></a>**NC_A2** | A2 | nc | 1 | nc | In PCIe this is +12 V; not connected |
| <a id="NC_A3"></a>**NC_A3** | A3 | nc | 1 | nc | In PCIe this is +12 V; not connected |
| <a id="AGND_2_"></a>**AGND(2)** | A4 | gnd | 1 | ground_analog | — |
| <a id="-12V"></a>**-12V** | A5 | power | 1 | power_analog | Analog power −12 V |
| <a id="AGND_3_"></a>**AGND(3)** | A6 | gnd | 1 | ground_analog | — |
| <a id="GPIO0_DREQ_N"></a>**~GPIO0_DREQ_N** | A7 | in | 1 | gpio | Module is ready for data exchange (DMA request) |
| <a id="GPIO1"></a>**GPIO1** | A8 | inout | 1 | gpio | Module-specific |
| <a id="_3V3_2_"></a>**+3V3(2)** | A9 | power | 1 | power_digital | — |
| <a id="_3V3_3_"></a>**+3V3(3)** | A10 | power | 1 | power_digital | — |
| <a id="PERIPH_RST_N"></a>**~PERIPH_RST_N** | A11 | out | 1 | control | Module reset in the slot |
| <a id="SPI_SCK"></a>**SPI_SCK** | B12 | out | 1 | spi | — |
| <a id="DGND"></a>**DGND** | B13 | gnd | 1 | ground_digital | — |
| <a id="SPI_MISO"></a>**SPI_MISO** | B14 | in | 1 | spi | — |
| <a id="DGND_2_"></a>**DGND(2)** | B15 | gnd | 1 | ground_digital | — |
| <a id="AUDIO_DIN"></a>**AUDIO_DIN** | B16 | in | 1 | audio | Audio module → host |
| <a id="DGND_3_"></a>**DGND(3)** | B17 | gnd | 1 | ground_digital | — |
| <a id="AUDIO_BCLK"></a>**AUDIO_BCLK** | B18 | out | 1 | audio | 24.576 MHz |
| <a id="DGND_4_"></a>**DGND(4)** | A12 | gnd | 1 | ground_digital | — |
| <a id="SPI_MOSI"></a>**SPI_MOSI** | A13 | out | 1 | spi | — |
| <a id="DGND_5_"></a>**DGND(5)** | A14 | gnd | 1 | ground_digital | — |
| <a id="AUDIO_DOUT"></a>**AUDIO_DOUT** | A15 | out | 1 | audio | Audio host → module |
| <a id="DGND_6_"></a>**DGND(6)** | A16 | gnd | 1 | ground_digital | — |
| <a id="AUDIO_FS"></a>**AUDIO_FS** | A17 | out | 1 | audio | Frame sync, 48 kHz |
| <a id="AUDIO_MCLK"></a>**AUDIO_MCLK** | A18 | out | 1 | audio | 12.288 MHz; next to BCLK with no ground between them |
