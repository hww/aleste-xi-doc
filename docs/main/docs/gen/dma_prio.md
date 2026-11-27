**PRIO[ch] · 8 bits**

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:3] | 5 | — | — | Reserved |
| <a id="MASK"></a>**MASK** | [2:0] | 3 | rw | 0x0 | Priority mask; a larger mask wins, ties go to the lower channel number |
