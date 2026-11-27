**SPIn_CTRL · 8 bits**

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="IRQE"></a>**IRQE** | [7] | 1 | rw | 0 | Interrupt on DONE |
| <a id="CPHA"></a>**CPHA** | [6] | 1 | rw | 0 | Clock phase |
| <a id="CPOL"></a>**CPOL** | [5] | 1 | rw | 0 | Clock polarity |
| <a id="DIV"></a>**DIV** | [4:1] | 4 | rw | 0xF | SCK divider: f = f_sys / (2 * (DIV + 1)) |
| <a id="EN"></a>**EN** | [0] | 1 | rw | 0 | Enable the controller |
