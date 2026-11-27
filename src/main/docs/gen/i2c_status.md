**I2C_STATUS · 8 bits**

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:3] | 5 | — | — | Reserved |
| <a id="DONE"></a>**DONE** | [2] | 1 | w1c | 0 | Byte completed |
| <a id="NACK"></a>**NACK** | [1] | 1 | ro | 0 | Last answer from the module was NACK |
| <a id="BUSY"></a>**BUSY** | [0] | 1 | ro | 0 | Operation in progress |
