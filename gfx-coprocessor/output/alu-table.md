| Код | Имя | Действие |
| --- | --- | --- |
| 0 | **MOV** | A |
| 1 | **ADD** | 24-bit addition; updates Z and N |
| 2 | **SUB** | 24-bit subtraction; updates Z and N |
| 3 | **AND** | Bitwise AND |
| 4 | **OR** | Bitwise OR |
| 5 | **XOR** | Bitwise XOR |
| 6 | **SHL** | Shift left by B[4:0] |
| 7 | **SHR** | Logical shift right by B[4:0] |
| 8 | **SAR** | Arithmetic shift right by B[4:0] |
| 9 | **MIN** | Signed minimum |
| 10 | **MAX** | Signed maximum |
| 11 | **MUL** | A[11:0] × B[11:0] → P |
| 12 | **ADDS** | Saturating addition |
| 13 | **SUBS** | Saturating subtraction |
| 14 | **COMB** | Pixel combine controlled by MODE |
