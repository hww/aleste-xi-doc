**PCIe x1 — Connector's edge**

*edge, 2 row(s) × 18, pitch 2.54 mm, numbering rowwise, pin 1 at top-left, key slot after position 11, drawn rotated 0°*

| Pin | Signal | Dir | Group | Description |
| --- | --- | --- | --- | --- |
| B1 | <a id="AGND"></a>**AGND** | gnd | ground_analog | — |
| B2 | <a id="_12V"></a>**+12V** | pwr | power_analog | Analog supply +12 V |
| B3 | **AGND** | gnd | ground_analog | — |
| B4 | <a id="DGND"></a>**DGND** | gnd | ground_digital | — |
| B5 | <a id="_3V3"></a>**+3V3** | pwr | power_digital | Digital supply +3.3 V |
| B6 | **RSV0** | NC | reserve | Reserved |
| B7 | <a id="I2C_SCL"></a>**I2C_SCL** | inout | i2c | — |
| B8 | <a id="DETECT_N"></a>**DETECT_N** | in | control | Module present (tied to DGND on the module) |
| B9 | <a id="INT_N"></a>**INT_N** | in | control | Module interrupt request |
| B10 | <a id="GPIO0_DREQ_N"></a>**GPIO0_DREQ_N** | in | gpio | Module ready for data exchange |
| B11 | <a id="SPI_CS_N"></a>**SPI_CS_N** | out | spi | Module chip select |
| B12 | <a id="SPI_SCK"></a>**SPI_SCK** | out | spi | — |
| B13 | **DGND** | gnd | ground_digital | — |
| B14 | <a id="AUDIO_BCLK"></a>**AUDIO_BCLK** | out | audio | 24.576 MHz bit clock |
| B15 | **DGND** | gnd | ground_digital | — |
| B16 | <a id="AUDIO_FS"></a>**AUDIO_FS** | out | audio | Frame sync, 48 kHz |
| B17 | **DGND** | gnd | ground_digital | — |
| B18 | <a id="AUDIO_MCLK"></a>**AUDIO_MCLK** | out | audio | 12.288 MHz master clock |
| A1 | **AGND** | gnd | ground_analog | — |
| A2 | <a id="-12V"></a>**-12V** | pwr | power_analog | Analog supply -12 V |
| A3 | **AGND** | gnd | ground_analog | — |
| A4 | **+3V3** | pwr | power_digital | — |
| A5 | **+3V3** | pwr | power_digital | — |
| A6 | **DGND** | gnd | ground_digital | — |
| A7 | <a id="I2C_SDA"></a>**I2C_SDA** | inout | i2c | — |
| A8 | <a id="PERIPH_RST_N"></a>**PERIPH_RST_N** | out | control | Module reset, one per slot |
| A9 | <a id="GPIO1"></a>**GPIO1** | inout | gpio | Module specific |
| A10 | **RSV1** | NC | reserve | Reserved |
| A11 | **RSV2** | NC | reserve | Reserved |
| A12 | <a id="SPI_MOSI"></a>**SPI_MOSI** | out | spi | — |
| A13 | <a id="SPI_MISO"></a>**SPI_MISO** | in | spi | — |
| A14 | **DGND** | gnd | ground_digital | — |
| A15 | <a id="AUDIO_DOUT"></a>**AUDIO_DOUT** | out | audio | Audio, host to module |
| A16 | **DGND** | gnd | ground_digital | — |
| A17 | <a id="AUDIO_DIN"></a>**AUDIO_DIN** | in | audio | Audio, module to host |
| A18 | **DGND** | gnd | ground_digital | — |
