**I2C_CTRL · 8 bits**

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:4] | 4 | — | — | Reserved |
| <a id="IRQE"></a>**IRQE** | [3] | 1 | rw | 0 | Interrupt on DONE |
| <a id="EN"></a>**EN** | [2] | 1 | rw | 0 | Enable the controller |
| <a id="SLOT"></a>**SLOT** | [1:0] | 2 | rw | 0x0 | Slot number for the multiplexer (0..3) |
