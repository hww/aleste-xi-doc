**SLOTn_CTRL · 8 bits**

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:3] | 5 | — | — | Reserved |
| <a id="EN12"></a>**EN12** | [2] | 1 | rw | 0 | Enable ±12 V (allowed only after ID_CHECK) |
| <a id="RST_REL"></a>**RST_REL** | [1] | 1 | rw | 0 | 1 = release PERIPH_RST_N |
| <a id="EN3V3"></a>**EN3V3** | [0] | 1 | rw | 0 | Enable slot +3.3 V |
