**SPIn_STATUS · 8 bits**

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:3] | 5 | — | — | Reserved |
| <a id="DREQ"></a>**DREQ** | [2] | 1 | ro | 0 | GPIO0_DREQ_N level (0 = module ready) |
| <a id="RXV"></a>**RXV** | [1] | 1 | ro | 0 | Received byte ready |
| <a id="BUSY"></a>**BUSY** | [0] | 1 | ro | 0 | Byte transfer in progress |
