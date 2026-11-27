**Alex I/O port map (draft)**

| Range | Name | Size | Access | Purpose |
| --- | --- | --- | --- | --- |
| `0x00`–`0x07` | <a id="SLOTS"></a>**SLOTS** | 8 B | rw | Slot power and status |
| `0x08`–`0x0B` | <a id="I2C"></a>**I2C** | 4 B | rw | I2C controller |
| `0x10`–`0x17` | <a id="SPI0"></a>**SPI0** | 8 B | rw | SPI, slot 0 |
| `0x18`–`0x1F` | <a id="SPI1"></a>**SPI1** | 8 B | rw | SPI, slot 1 |
| `0x20`–`0x27` | <a id="SPI2"></a>**SPI2** | 8 B | rw | SPI, slot 2 |
| `0x28`–`0x2F` | <a id="SPI3"></a>**SPI3** | 8 B | rw | SPI, slot 3 |
| `0x30`–`0x3F` | <a id="AUDIO"></a>**AUDIO** | 16 B | rw | Audio routing and control (TBD) |
