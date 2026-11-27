**Connector contact budget**

| Name | Value | Description |
| --- | --- | --- |
| <a id="_12_V"></a>**+12 V** | 1 | B2 |
| <a id="-12_V"></a>**-12 V** | 1 | A2 |
| <a id="AGND"></a>**AGND** | 4 | B1, B3, A1, A3 (around the +/-12 V pair) |
| <a id="_3.3_V"></a>**+3.3 V** | 3 | B5, A4, A5 |
| <a id="DGND"></a>**DGND** | 8 | B4, A6 (zone 1); B13, B15, B17, A14, A16, A18 (zone 2) |
| <a id="Signals"></a>**Signals** | 16 | SPI 4, I2C 2, control 3, GPIO 2, audio 5 |
| <a id="Reserve"></a>**Reserve** | 3 | B6, A10, A11 |

**Notes:**

- 36 contacts in total.
- If MCLK turns out to be unnecessary, B18 can become DGND.
- Position numbering and the key location are quoted from memory; verify against the connector datasheet.
