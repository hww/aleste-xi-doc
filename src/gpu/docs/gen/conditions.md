# COND (4 bits, ARM-style)

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="AL"></a>**AL** | Always |
| 1 | <a id="EQ"></a>**EQ** | Z=1 |
| 2 | <a id="NE"></a>**NE** | Z=0 |
| 3 | <a id="CS"></a>**CS** | C=1 (unsigned >=) |
| 4 | <a id="CC"></a>**CC** | C=0 (unsigned <) |
| 5 | <a id="MI"></a>**MI** | N=1 |
| 6 | <a id="PL"></a>**PL** | N=0 |
| 7 | <a id="VS"></a>**VS** | V=1 |
| 8 | <a id="VC"></a>**VC** | V=0 |
| 9 | <a id="HI"></a>**HI** | C=1 and Z=0 |
| 10 | <a id="LS"></a>**LS** | C=0 or Z=1 |
| 11 | <a id="GE"></a>**GE** | N=V |
| 12 | <a id="LT"></a>**LT** | N!=V |
| 13 | <a id="GT"></a>**GT** | Z=0 and N=V |
| 14 | <a id="LE"></a>**LE** | Z=1 or N!=V |
| 15 | <a id="NV"></a>**NV** | Never (default=false) |
