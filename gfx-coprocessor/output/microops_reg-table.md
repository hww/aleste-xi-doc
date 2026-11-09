### Микрокоманды

| Микрокоманда | Слот | Действие | Тактов |
| --- | --- | --- | --- |
| LD SRC1, Rn | reg | SRC1 ← R[n] | 1 |
| LD SRC1, DST | reg | SRC1 ← DST (результат предыдущей АЛУ-операции) | 1 |
| LDL SRC1, IMM12 | reg | SRC1 ← X (константа из микрослова) | 1 |
| LDH SRC1, IMM12 | reg | SRC1 ← X (константа из микрослова) | 1 |
| LD SRC2, Rn | reg | SRC2 ← R[n] | 1 |
| LD SRC2, DST12 | reg | SRC2 ← DST | 1 |
| LDL SRC2, IMM12 | reg | SRC2 ← X | 1 |
| LDH SRC2, IMM12 | reg | SRC2 ← X | 1 |
| ST Rn, DST | reg | R[n] ← DST | 1 |
| SIDX Rn | io | Задать индекс источника | 1 |
| DIDX Rn | io | Задать индекс приёмника | 1 |
| READ SRCk, IDXk | io | Читать пиксель источника в SRCk | зависит |
| READ SRCk, IDXk | io | Записать пиксель приёмника из SRCk | 1 |
| WRITE IDXk, DST | io | Читать пиксель источника в SRCk | зависит |
| WRITE IDXk, DST | io | Записать пиксель приёмника из SRCk | 1 |
| SYNC | io | Сброс DW в память | зависит |
