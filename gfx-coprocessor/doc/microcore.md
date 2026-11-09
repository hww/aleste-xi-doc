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

| № | Имя | Назначение | Группа |
| --- | --- | --- | --- |
| 00 | **DX** | Destination X coordinate | destination |
| 01 | **DY** | Destination Y coordinate | destination |
| 02 | **W** | Rectangle width | destination |
| 03 | **H** | Rectangle height | destination |
| 04 | **SX** | Source X coordinate | source |
| 05 | **SY** | Source Y coordinate | source |
| 06 | **DSTRIDE** | Destination row stride | memory |
| 07 | **SSTRIDE** | Source row stride | memory |
| 08 | **DBASE** | Destination base address | memory |
| 09 | **SBASE** | Source base address | memory |
| 10 | **FG** | Foreground colour | pixel |
| 11 | **BG** | Background colour | pixel |
| 12 | **MODE** | Pixel formats and combine operation | pixel |
| 13 | **CX0** | Clip window left | clipping |
| 14 | **CY0** | Clip window top | clipping |
| 15 | **CX1** | Clip window right | clipping |
| 16 | **CY1** | Clip window bottom | clipping |
| 17 | **STA** | Affine horizontal U increment | affine |
| 18 | **STB** | Affine horizontal V increment | affine |
| 19 | **STC** | Affine vertical U increment | affine |
| 20 | **STD** | Affine vertical V increment | affine |
| 21 | **T0** | Temporary 0; commonly destination linear index | temporary |
| 22 | **T1** | Temporary 1; commonly inner-loop counter | temporary |
| 23 | **T2** | Temporary 2; commonly outer-loop counter | temporary |
| 24 | **T3** | Temporary 3; commonly clipped X start | temporary |
| 25 | **T4** | Temporary 4; commonly clipped width or X end | temporary |
| 26 | **T5** | Temporary 5; commonly current Y | temporary |
| 27 | **T6** | Temporary 6; commonly source linear index | temporary |
| 28 | **T7** | General temporary register | temporary |
| 29 | **T8** | General temporary register | temporary |
| 30 | **T9** | General temporary register | temporary |
| 31 | **T10** | General temporary register | temporary |


## 6. Операции АЛУ

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


`COMB(A = пиксель источника, B = пиксель приёмника)` управляется регистром MODE:

![Регистр MODE](../output/mode_register.svg)