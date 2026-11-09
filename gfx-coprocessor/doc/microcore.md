# Микроядро графического сопроцессора

...

## 3. Операнды

Каждое поле операнда в микрослове — 6 бит.

| Адрес | Имя | Чтение | Запись |
| --- | --- | --- | --- |
| 0-31 | **R0-R31** | 24-bit register file | 24-bit register file |
| 32 | **ZERO** | Constant zero | Ignored |
| 33 | **ACC** | Previous ALU result | Not writable |
| 34 | **P** | Multiplier result | Not writable |
| 35 | **FIFO8** | Pop one byte; wait while empty | Not writable |
| 36 | **FIFO16** | Pop two bytes, low byte first | Not writable |
| 37 | **FIFO16S** | Pop two bytes, sign-extended | Not writable |
| 38 | **SPIX** | Source pixel from SW | Not writable |
| 39 | **DPIX** | Destination pixel from DW | Write pixel to DW, mark dirty |
| 40 | **SIDX** | Not readable | Set source linear pixel index |
| 41 | **DIDX** | Not readable | Set destination linear pixel index |
| 42 | **FLUSH** | Not readable | Flush dirty destination word |
| 43 | **PALI** | Not readable | Palette index |
| 44 | **PALD** | Not readable | Palette colour |
| 45 | **IMM** | 9-bit immediate from X field | Not writable |
| 46 | **STAT** | Status flags | Request interrupt |


Модель трёхадресная (`DST = OP(A, B)`), поэтому один аккумулятор не становится бутылочным горлышком.

## 4. Регистровый файл

32 регистра по 24 бита.

### Регистровый файл · R0–R31

| Регистр | Имя | Назначение | Группа |
| --- | --- | --- | --- |
| R0 | **DX** | Destination X coordinate | destination |
| R1 | **DY** | Destination Y coordinate | destination |
| R2 | **DW** | Destination width | destination |
| R3 | **DH** | Destination height | destination |
| R4 | **SX** | Source X coordinate | source |
| R5 | **SY** | Source Y coordinate | source |
| R6 | **SW** | Source width | source |
| R7 | **SH** | Source height | source |
| R8 | **DSTRIDE** | Destination row stride (screen width) | memory |
| R9 | **SSTRIDE** | Source row stride (screen width) | memory |
| R10 | **DBASE** | Destination base address | memory |
| R11 | **SBASE** | Source base address | memory |
| R12 | **FG** | Foreground colour | pixel |
| R13 | **BG** | Background colour | pixel |
| R14 | **MODE** | Pixel formats and combine operation | pixel |
| R15 | **CX0** | Clip window left | clipping |
| R16 | **CY0** | Clip window top | clipping |
| R17 | **CX1** | Clip window right | clipping |
| R18 | **CY1** | Clip window bottom | clipping |
| R19 | **SDX** | Source delta X (12.12) | increment |
| R20 | **SDY** | Source delta Y (12.12) | increment |
| R21 | **DDX** | Destination delta X (12.12) | increment |
| R22 | **DDY** | Destination delta Y (12.12) | increment |
| R23 | **T0** | Временный регистр | temporary |
| R24 | **T1** | Временный регистр | temporary |
| R25 | **T2** | Временный регистр | temporary |
| R26 | **T3** | Временный регистр | temporary |
| R27 | **T4** | Временный регистр | temporary |
| R28 | **T5** | Временный регистр | temporary |
| R29 | **T6** | Временный регистр | temporary |
| R30 | **T7** | Временный регистр | temporary |
| R31 | **T8** | Временный регистр | temporary |


## 6. Операции АЛУ

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


`COMB(A = пиксель источника, B = пиксель приёмника)` управляется регистром MODE:

![Регистр MODE](../output/mode_register.svg)