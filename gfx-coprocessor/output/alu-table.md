### Операции АЛУ

| Код | Имя | Действие |
| --- | --- | --- |
| 0 | **ADD** | DST = SRC1 + SRC2; обновляет FLAGS (Z, N) |
| 1 | **SUB** | DST = SRC1 − SRC2; обновляет FLAGS (Z, N) |
| 2 | **AND** | DST = SRC1 & SRC2 |
| 3 | **OR** | DST = SRC1 | SRC2 |
| 4 | **XOR** | DST = SRC1 ^ SRC2 |
| 5 | **SHL** | DST = SRC1 << SRC2[4:0] |
| 6 | **SHR** | DST = SRC1 >> SRC2[4:0] (логический) |
| 7 | **SAR** | DST = SRC1 >> SRC2[4:0] (арифметический) |
| 8 | **MIN** | DST = min(SRC1, SRC2) со знаком |
| 9 | **MAX** | DST = max(SRC1, SRC2) со знаком |
| 10 | **MUL** | DST = SRC1[11:0] × SRC2[11:0]; задержка определяется FPGA |
| 11 | **ADDS** | DST = saturate(SRC1 + SRC2) |
| 12 | **SUBS** | DST = saturate(SRC1 − SRC2) |
| 13 | **COMB** | DST = combine(SRC1, SRC2) по регистру MODE |
