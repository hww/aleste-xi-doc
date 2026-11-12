**Legacy Device Sub-registers**

| Device | Cpc_port | Rtl_status | Lx |
| --- | --- | --- | --- |
| Gate Array | 7Fxx (D7/D6) | implemented | Mandatory |
| CRTC 6845 | BCXX/BDXX | implemented | Mandatory |
| PPI 8255 | F4XX–F7XX | implemented | Mandatory |
| FDC 765 | FA7E/FB7E/FB7F | implemented | Mandatory |
| Upper ROM Select | DFXX | implemented | Mandatory |
| Printer port | EFXX | (via PPI) | Optional |
| Cassette tape | (via PPI) | (via PPI) | Optional |
| Joysticks | (via PPI/keyboard) | (via PPI) | Optional |
| SIO/DART | FADC–FADF | not implemented | Optional |
| 8253 Timer | FBDC–FBDF | not implemented | Optional |
