**SLOTn_STAT · 8 bits**

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:6] | 2 | — | — | Reserved |
| <a id="INT"></a>**INT** | [5] | 1 | ro | 0 | INT_N level (1 = request) |
| <a id="READY"></a>**READY** | [4] | 1 | rw | 0 | Software marked the module as ready |
| <a id="FAULT"></a>**FAULT** | [3] | 1 | w1c | 0 | Overcurrent protection tripped |
| <a id="PG12"></a>**PG12** | [2] | 1 | ro | 0 | ±12 V within range |
| <a id="PG3V3"></a>**PG3V3** | [1] | 1 | ro | 0 | +3.3 V within range |
| <a id="PRESENT"></a>**PRESENT** | [0] | 1 | ro | 0 | DETECT_N == 0 |
