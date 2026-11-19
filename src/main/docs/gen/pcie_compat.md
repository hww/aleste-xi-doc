**Correspondence to PCIe functions (protection against incorrect insertion)**

| Pos. | Name | Function in PCIe |
| --- | --- | --- |
| A1 | <a id="DETECT_N"></a>**DETECT_N** | PRSNT1# |
| A5 | <a id="-12V"></a>**-12V** | TCK (JTAG), not connected on ordinary cards |
| A11 | <a id="PERIPH_RST_N"></a>**PERIPH_RST_N** | PERST# |
| B5 | <a id="I2C_SCL"></a>**I2C_SCL** | SMCLK |
| B6 | <a id="I2C_SDA"></a>**I2C_SDA** | SMDAT |
| B11 | <a id="INT_N"></a>**INT_N** | WAKE# |
| B3, A2, A3 | <a id="NC"></a>**NC** | +12 V in PCIe: not connected here |

**Notes:**

- Slot power-up order (see the slot_power state machine): ±12 V is applied only after the ID-EEPROM has been read successfully.
