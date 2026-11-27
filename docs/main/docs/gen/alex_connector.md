**Alex slot connector (PCIe x1, 36 contacts; key between positions 11 and 12)**

| Name | Pin | Dir | Width | Group | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="AGND"></a>**AGND** | B1 | gnd | 1 | ground_analog | — |
| <a id="_12V"></a>**+12V** | B2 | pwr | 1 | power_analog | Analog supply +12 V |
| <a id="AGND__2"></a>**AGND** | B3 | gnd | 1 | ground_analog | — |
| <a id="DGND"></a>**DGND** | B4 | gnd | 1 | ground_digital | — |
| <a id="_3V3"></a>**+3V3** | B5 | pwr | 1 | power_digital | Digital supply +3.3 V |
| <a id="RSV0"></a>**RSV0** | B6 | nc | 1 | reserve | Reserved |
| <a id="I2C_SCL"></a>**I2C_SCL** | B7 | inout | 1 | i2c | — |
| <a id="DETECT_N"></a>**~DETECT_N** | B8 | in | 1 | control | Module present (tied to DGND on the module) |
| <a id="INT_N"></a>**~INT_N** | B9 | in | 1 | control | Module interrupt request |
| <a id="GPIO0_DREQ_N"></a>**~GPIO0_DREQ_N** | B10 | in | 1 | gpio | Module ready for data exchange |
| <a id="SPI_CS_N"></a>**~SPI_CS_N** | B11 | out | 1 | spi | Module chip select |
| <a id="AGND__3"></a>**AGND** | A1 | gnd | 1 | ground_analog | — |
| <a id="-12V"></a>**-12V** | A2 | pwr | 1 | power_analog | Analog supply -12 V |
| <a id="AGND__4"></a>**AGND** | A3 | gnd | 1 | ground_analog | — |
| <a id="_3V3__2"></a>**+3V3** | A4 | pwr | 1 | power_digital | — |
| <a id="_3V3__3"></a>**+3V3** | A5 | pwr | 1 | power_digital | — |
| <a id="DGND__2"></a>**DGND** | A6 | gnd | 1 | ground_digital | — |
| <a id="I2C_SDA"></a>**I2C_SDA** | A7 | inout | 1 | i2c | — |
| <a id="PERIPH_RST_N"></a>**~PERIPH_RST_N** | A8 | out | 1 | control | Module reset, one per slot |
| <a id="GPIO1"></a>**GPIO1** | A9 | inout | 1 | gpio | Module specific |
| <a id="RSV1"></a>**RSV1** | A10 | nc | 1 | reserve | Reserved |
| <a id="RSV2"></a>**RSV2** | A11 | nc | 1 | reserve | Reserved |
| <a id="SPI_SCK"></a>**SPI_SCK** | B12 | out | 1 | spi | — |
| <a id="DGND__3"></a>**DGND** | B13 | gnd | 1 | ground_digital | — |
| <a id="AUDIO_BCLK"></a>**AUDIO_BCLK** | B14 | out | 1 | audio | 24.576 MHz bit clock |
| <a id="DGND__4"></a>**DGND** | B15 | gnd | 1 | ground_digital | — |
| <a id="AUDIO_FS"></a>**AUDIO_FS** | B16 | out | 1 | audio | Frame sync, 48 kHz |
| <a id="DGND__5"></a>**DGND** | B17 | gnd | 1 | ground_digital | — |
| <a id="AUDIO_MCLK"></a>**AUDIO_MCLK** | B18 | out | 1 | audio | 12.288 MHz master clock |
| <a id="SPI_MOSI"></a>**SPI_MOSI** | A12 | out | 1 | spi | — |
| <a id="SPI_MISO"></a>**SPI_MISO** | A13 | in | 1 | spi | — |
| <a id="DGND__6"></a>**DGND** | A14 | gnd | 1 | ground_digital | — |
| <a id="AUDIO_DOUT"></a>**AUDIO_DOUT** | A15 | out | 1 | audio | Audio, host to module |
| <a id="DGND__7"></a>**DGND** | A16 | gnd | 1 | ground_digital | — |
| <a id="AUDIO_DIN"></a>**AUDIO_DIN** | A17 | in | 1 | audio | Audio, module to host |
| <a id="DGND__8"></a>**DGND** | A18 | gnd | 1 | ground_digital | — |
