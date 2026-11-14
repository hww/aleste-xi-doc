# 8255 PPI Port B — VSYNC, Cassette, Printer

![8255 PPI Port B — VSYNC, Cassette, Printer](gen/L_PPI_PORTB.svg)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="CASSETTE"></a>**CASSETTE** | [7] | 1 | Cassette data |
| <a id="PRNBUSY"></a>**PRNBUSY** | [6] | 1 | 1=busy, 0=ready |
| <a id="EXP"></a>**EXP** | [5] | 1 | Expansion signal |
| <a id="REFRESH"></a>**REFRESH** | [4] | 1 | 1=50Hz, 0=60Hz |
| <a id="MFG"></a>**MFG** | [3:1] | 3 | Manufacturer code [`L_PPI_MFG`](gen/L_PPI_MFG.md) |
| <a id="VSYNC"></a>**VSYNC** | [0] | 1 | 1=active |
