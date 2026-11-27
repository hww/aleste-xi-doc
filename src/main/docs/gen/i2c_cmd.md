**I2C_CMD · 8 bits (a write starts the operation)**

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:5] | 3 | — | — | Reserved |
| <a id="NACK"></a>**NACK** | [4] | 1 | wo | 0 | With RD: answer NACK (last byte) |
| <a id="RD"></a>**RD** | [3] | 1 | wo | 0 | Receive a byte into I2C_DATA |
| <a id="WR"></a>**WR** | [2] | 1 | wo | 0 | Transmit the byte in I2C_DATA |
| <a id="STOP"></a>**STOP** | [1] | 1 | wo | 0 | Issue STOP |
| <a id="START"></a>**START** | [0] | 1 | wo | 0 | Issue START (or repeated START) |
