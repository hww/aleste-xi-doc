**Connector pin balance**

| Count | Name | Composition |
| --- | --- | --- |
| 2 | <a id="_12_V"></a>**+12 V** | B1, B2 |
| 1 | <a id="_12_V"></a>**−12 V** | A5 |
| 3 | <a id="AGND"></a>**AGND** | B4, A4, A6 |
| 3' | <a id="_3.3_V"></a>**+3.3 V** | B8, A9, A10 |
| 7 | <a id="DGND"></a>**DGND** | B7, B13, B15, B17, A12, A14, A16 |
| 16 | <a id="Signals"></a>**Signals** | SPI 4, I2C 2, control 3, GPIO 2, audio 5 |
| 4 | <a id="NC"></a>**NC** | B3, B10, A2, A3 (protection against a real PCIe card) |

**Notes:**

- 36 pins total. No free reserve: the NC positions are occupied for protection reasons.
- PCIe position assignments are from memory; verify against PCIe CEM and the connector datasheet.
