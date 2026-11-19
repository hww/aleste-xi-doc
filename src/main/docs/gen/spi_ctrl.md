**SPIn_CTRL · 8 bits**

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:6] | 2 | — | — | Reserved |
| <a id="CSA"></a>**CSA** | [5] | 1 | rw | 0 | 1 = keep CS_N asserted |
| <a id="DIV"></a>**DIV** | [4:1] | 4 | rw | 0xF | SCK divider: f = f_sys / (2·(DIV+1)) |
| <a id="EN"></a>**EN** | [0] | 1 | rw | 0 | Enable the slot controller |
