# Графический сопроцессор для Z80: архитектура

*Источник для генератора документации. YAML-декларации в `gen/` порождают SVG и MD-таблицы; `[include]` вставляет их сюда. Цифры ориентировочные, детали уточняются на симуляторе.*

## 1. Принципы

1. **Простота важнее пиковой скорости.** Узкое место — память, поэтому ядро можно делать простым.
2. **Ядро программируемое, а не жёстко-автоматное.** Микрокод в BRAM, новый алгоритм — новый микрокод, а не новая логика.
3. **В железо выносится только горячий путь:** буферы слова, адресные генераторы, упаковка пикселя.
4. **Экранные координаты внутри, адреса снаружи не видны.** CPU говорит «нарисуй в (x, y)».
5. **Два формата пикселя: 4 и 8 bpp.** 1 bpp — только как источник (шрифты, маски). 16 bpp — через `PASS16` (слово насквозь).
6. **Никакого аппаратного скроллинга.** Вместо него быстрое копирование блоков.
7. **Команды — следствие раскладки микрослова.** Сначала поля, из них видны команды.
8. **`REG_ADDR` — resource select.** Поле не обязано иметь одну семантику: `LDR`/`STR` — регистр, `PACKER_*`/`SETPAGE`/`SETMODE`/`ADDR` — канал.
9. **`IMM` — универсальный аргумент.** Его потребители: `LDI`/`LDH`/`LDL` (константа), `LDX`/`STX` (код операнда), `JMP`/`CALL`/`LOOP` (адрес), `HALT` (код ошибки), `WAIT_FLAG` (код флага). В одном слове — один потребитель, проверяет ассемблер.

## 2. Общая картина

![Архитектура микроядра](images/lx-gpu-architecture.webp)

*Граница доменов: логика команд и регистров — в 8-битном домене; ядро, буферы слов и видеоконтроллер — 16-битная память. Пересечение — в регистрах ядра.*

GPU → Wishbone → VideoMemoryArbiter. Работу видеоарбитра не обсуждаем; у развёртки высший приоритет.

## 3. Микрослово

![Формат микрослова](gen/microinstruction.svg)

<!-- table: generated -->
**MICROINSTRUCTION · 36 BIT**

| Поле | Биты | Ширина | Описание |
| --- | --- | --- | --- |
| **REG_OP** | [35:31] | 5 | Операция передачи данных (5 бит) |
| **ALU_OP** | [30:26] | 5 | Арифметическая или логическая операция (5 бит) |
| **CTRL_OP** | [25:23] | 3 | Управление потоком (3 бита) |
| **REG_ADDR** | [22:18] | 5 | Resource select (5 бит): регистр (LDR/STR) или канал (PACKER_*/SETPAGE/SETMODE/ADDR) |
| **MASK** | [17:15] | 3 | Что блокировать при выполнении условия |
| **COND** | [14:12] | 3 | Условие (Z, NZ, N, NN, C, NC + 2) |
| **IMM** | [11:0] | 12 | 12-битный аргумент. Семантика зависит от команды: константа (LDI/LDH/LDL), адрес (JMP/CALL/LOOP), код IRQ, код операнда (LDX/STX), код флага (WAIT_FLAG), код ошибки (HALT X) |


**Порядок выполнения.** Три блока (REG_OP, ALU_OP, CTRL_OP) работают параллельно: все читают ACC и OPR на начало такта, запись — в конце. АЛУ считает на старом OPR, REG_OP грузит следующий OPR; `STR` сохраняет ACC после предыдущего слова.

**Условие и маска.** Флаги Z, N, C — из предыдущего слова. COND (3 бита) выбирает условие; если оно выполняется, MASK (3 бита) блокирует отмеченные блоки (бит 0 — REG_OP, бит 1 — ALU_OP, бит 2 — CTRL_OP). MASK = 0 — безусловно.

<!-- table: generated -->
**CONDITION**

| Code | Name | Description |
| --- | --- | --- |
| 0 | Z | Zero = 1 |
| 1 | NZ | Zero = 0 |
| 2 | N | Negative = 1 |
| 3 | NN | Negative = 0 |
| 4 | C | Carry = 1 |
| 5 | NC | Carry = 0 |
| 6 | RES0 | Запас |
| 7 | RES1 | Запас |


<!-- table: generated -->
**MASK**

| Code | Name | Description |
| --- | --- | --- |
| 0 | REG | Блокировать REG_OP |
| 1 | ALU | Блокировать ALU_OP |
| 2 | CTRL | Блокировать CTRL_OP |


**`IMM` — 12 бит, универсальный аргумент.** Семантика зависит от команды:

| Команда | Что в `IMM` |
|---|---|
| `LDI`/`LDH`/`LDL` | константа (12 бит) |
| `LDX`/`STX` | код операнда (`OperandMap`, 6 бит) |
| `JMP`/`CALL`/`LOOP` | адрес (12 бит) |
| `HALT X` | код ошибки (12 бит) |
| `WAIT_FLAG` | код флага (`IMM[5:0]`) + инверсия (`IMM[6]`) |
| `PACKER_RD`/`WR`/`SETPAGE`/`SETMODE`/`ADDR`/`IRQ` | не используется (канал — в `REG_ADDR`, код `IRQ` — в `ACC`) |

**Правило:** в одном микрослове — **один** потребитель `IMM`. `LDI` + `JMP` — можно. `LDI` + `LDX` — **нельзя** (оба хотят `IMM`). Проверяет **ассемблер**.

## 4. Тракт ACC/OPR

![Внутренняя структура АЛУ](images/lx-gpu-alu-architecture.webp)

```
          память (Wishbone 16 бит)
            ^        ^        ^
          [S]      [D]     [DATA]
         SIDX     DIDX      DPTR
            |        |        |
          SPIX     DPIX     слово данных
            \        |        /
         [мультиплексор OPR] <-- IMM, R[n], ZERO
                     |
                     v
   ACC ---A---> [АЛУ 24 бита] <---B--- OPR
    ^                |
    +----результат-----+        [DSP 12x12] -> ACC
```

Мультиплексор только на входе OPR. ACC загружается исключительно из АЛУ; «загрузка» — операция `PASS` (ACC = OPR). Входы DSP подключены к ACC и OPR. `MUL` — обычная операция АЛУ (`ACC = ACC[11:0] × OPR[11:0]`), два такта; если следующее слово использует АЛУ, железо само вставляет такт ожидания.

**Пиксельный путь.** `PACKER_RD`/`PACKER_WR` — единый путь для пикселей/слова. `SPIX`/`DPIX` доступны **только** через `PACKER_*` (или `LDX SPIX`/`STX DPIX` для отладки). `LDSP`/`LDDP`/`STDP` — **убраны** (зарезервированы).

**AddrPacker** — отдельный класс: `x_int`/`y_int` из `ACC` (`ACC[11:0]=x`, `ACC[23:12]=y`), `base`/`stride` из регистров, `fmt` из `ch_mode_[ch]` → `addr24` + `pos`. `PACKER_RD/WR` вызывают `AddrPacker` внутри. **`CH_DATA`** — `DPTR` напрямую (не `AddrPacker`), `fmt` — `ch_mode_[DATA]` (`PASS16`/`PASS_LO8`/`PASS_HI8`).

## 5. Микрокоманды

<!-- table: generated -->
**REG_OP — Передача данных и служебное**

| Code | Name | Description | Cycles | Imm |
| --- | --- | --- | --- | --- |
| 0 | NOP | — | 1 | — |
| 1 | PASS | ACC = OPR | 1 | — |
| 2 | LDR | OPR = operand[REG_ADDR] | 1 | — |
| 3 | STR | operand[REG_ADDR] = ACC | 1 | — |
| 4 | LDD | OPR = слово из памяти по DPTR (16 бит), DPTR += 2 | 1 | — |
| 5 | LDDS | То же, со знаком | 1 | — |
| 6 | SETS | SIDX = ACC | 1 | — |
| 7 | SETD | DIDX = ACC | 1 | — |
| 8 | SETP | DPTR = ACC | 1 | — |
| 9 | LDCNT | Счётчик цикла = ACC | 1 | — |
| 10 | FLUSH | Сбросить dirty всех каналов в память | зависит | — |
| 11 | LDX | OPR = operand[IMM[5:0]] | 1 | opnum[5:0] |
| 12 | STX | operand[IMM[5:0]] = ACC | 1 | opnum[5:0] |
| 13 | LDI | OPR = IMM со знаком | 1 | константа[11:0] |
| 14 | LDH | OPR = IMM × 4096 | 1 | константа[11:0] |
| 15 | LDL | OPR[11:0] = IMM | 1 | константа[11:0] |
| 16 | PACKER_RD | Чтение пикселя/слова | 1+miss | — |
| 17 | PACKER_WR | Запись пикселя/слова | 1+miss | — |
| 18 | SETMODE | ch_mode_[REG_ADDR].fmt = ACC[2:0] | 1 | — |
| 19 | SETPAGE | set_page(REG_ADDR, ACC) | зависит | — |
| 20 | ADDR | AddrPacker(REG_ADDR): ACC=(y<<12)|x | 1 | — |
| 21 | SETMASK | mask_ = ACC[15:0] | 1 | — |
| 22 | IRQ | irq_pending_=1, irq_code_=ACC[11:0] | 1 | — |
| 23 | резерв | — | — | — |


<!-- table: generated -->
**ALU_OP — Арифметика и логика**

| Code | Name | Description | Cycles |
| --- | --- | --- | --- |
| 0 | NOP | ACC не меняется | 1 |
| 1 | PASS | ACC = OPR | 1 |
| 2 | ADD | ACC = ACC + OPR; Z, N, C | 1 |
| 3 | SUB | ACC = ACC - OPR; Z, N, C | 1 |
| 4 | AND | ACC = ACC & OPR | 1 |
| 5 | OR | ACC = ACC | OPR | 1 |
| 6 | XOR | ACC = ACC ^ OPR | 1 |
| 7 | SHL | ACC = ACC << OPR[4:0] | 1 |
| 8 | SHR | ACC = ACC >> OPR[4:0] (логический) | 1 |
| 9 | SAR | ACC = ACC >> OPR[4:0] (арифметический) | 1 |
| 10 | MIN | ACC = min(ACC, OPR) со знаком | 1 |
| 11 | MAX | ACC = max(ACC, OPR) со знаком | 1 |
| 12 | MUL | ACC = ACC[11:0] × OPR[11:0] | 2 |
| 13 | ADDS | ACC = saturate(ACC + OPR) | 1 |
| 14 | SUBS | ACC = saturate(ACC - OPR) | 1 |
| 15 | резерв | — | — |


<!-- table: generated -->
**CTRL_OP — Управление потоком**

| Code | Name | Description | Imm | Cycles |
| --- | --- | --- | --- | --- |
| 0 | NOP | Ничего не делать | — | 1 |
| 1 | JMP | Безусловный переход на X | адрес[11:0] | 1 |
| 2 | CALL | Вызов подпрограммы по адресу X | адрес[11:0] | 1 |
| 3 | RET | Возврат | — | 1 |
| 4 | LOOP | Уменьшить счётчик; если не ноль — перейти на X | адрес[11:0] | 1 |
| 5 | JMPA | Переход на адрес из ACC[8:0] | — | 1 |
| 6 | HALT | X=0 → IDLE; X!=0 → ERROR | код[11:0] | 1 |
| 7 | WAIT_FLAG | Ждать флаг (IMM[5:0]), инверсия (IMM[6]) | флаг[5:0]+inv[6] | 1+ |


**REG_OP** — передача данных и служебное (5 бит, 24 кода): `NOP`, `PASS`, `LDR`, `STR`, `LDD`, `LDDS`, `SETS`, `SETD`, `SETP`, `LDCNT`, `FLUSH`, `LDX`, `STX`, `LDI`, `LDH`, `LDL`, `PACKER_RD`, `PACKER_WR`, `SETMODE`, `SETPAGE`, `ADDR`, `SETMASK`, `IRQ` + резерв.

**ALU_OP** — 16 кодов из 16. `COMB` **убран**, логика (`AND`/`OR`/`XOR`) — через ALU. `ADDS`/`SUBS` — ширина канала из `ch_mode_[DEST].fmt`.

**CTRL_OP** — 3 бита, 8 команд: `NOP`, `JMP`, `CALL`, `RET`, `LOOP`, `JMPA`, `HALT X`, `WAIT_FLAG`. `LDI`/`LDH`/`LDL`/`IRQ`/`FAULT`/`SKIP_IF_Z` — **убраны** (в `REG_OP`).

## 6. Карта операндов

![Карта операндов](gen/operand_map.svg)

<!-- table: generated -->
**Карта операндов микрокода**

| Code | Name | Read | Write |
| --- | --- | --- | --- |
| 0–31 | R0–R31 | Регистровый файл, 24 бита | То же |
| 32 | ZERO | 0 | Игнорируется |
| 33 | ACC | Результат предыдущей операции | — |
| 34 | SPIX | Через PACKER_RD (CH_SOURCE) | — |
| 35 | DPIX | Через PACKER_RD (CH_DEST) | Через PACKER_WR (CH_DEST), с mask_ |
| 36 | SIDX | LDX SIDX | STX SIDX |
| 37 | DIDX | LDX DIDX | STX DIDX |
| 38 | DPTR | LDX DPTR | STX DPTR / SETP |
| 39 | FLAG | Z, N, C | — |
| 40 | CNT | LDX CNT | STX CNT / LDCNT |
| 41 | FLAG_BUSY | 1 если wait_ > 0 | — |
| 42 | FLAG_IRQ | 1 если irq_pending_ | — |
| 43 | FLAG_DMA | заглушка, 0 | — |
| 44 | FLAG_CNT_ZERO | 1 если loop_cnt_ == 0 | — |


`ZERO` — операнд; при комбинаторном взрыве на мультиплексоре OPR заменяется на `LDI 0`.

`SPIX`/`DPIX` — **через `PACKER_RD/WR`**, не через `LDX`/`STX` (последние читают значение, не пиксель).

Флаги (`FLAG_BUSY`, `FLAG_IRQ`, `FLAG_DMA`, `FLAG_CNT_ZERO`) — однобитные операнды для `WAIT_FLAG` и `LDX`.

## 7. Регистровый файл

![Регистры](gen/registers.svg)

<!-- table: generated -->
**Регистровый файл · R0–R31**

| Index | Name | Description | Group |
| --- | --- | --- | --- |
| R0 | DX | Destination X | destination |
| R1 | DY | Destination Y | destination |
| R2 | DW | Destination width | destination |
| R3 | DH | Destination height | destination |
| R4 | SX | Source X | source |
| R5 | SY | Source Y | source |
| R6 | SW | Source width | source |
| R7 | SH | Source height | source |
| R8 | DSTRIDE | Destination row stride | memory |
| R9 | SSTRIDE | Source row stride | memory |
| R10 | DBASE | Destination base address | memory |
| R11 | SBASE | Source base address | memory |
| R12 | FG | Foreground colour | pixel |
| R13 | BG | Background colour | pixel |
| R14 | MODE | Pixel formats and combine operation | pixel |
| R15 | CX0 | Clip window left | clipping |
| R16 | CY0 | Clip window top | clipping |
| R17 | CX1 | Clip window right | clipping |
| R18 | CY1 | Clip window bottom | clipping |
| R19 | SDX | Source delta X (12.12) | increment |
| R20 | SDY | Source delta Y (12.12) | increment |
| R21 | DDX | Destination delta X (12.12) | increment |
| R22 | DDY | Destination delta Y (12.12) | increment |
| R23 | T0 | Временный регистр | temporary |
| R24 | T1 | Временный регистр | temporary |
| R25 | T2 | Временный регистр | temporary |
| R26 | T3 | Временный регистр | temporary |
| R27 | T4 | Временный регистр | temporary |
| R28 | T5 | Временный регистр | temporary |
| R29 | T6 | Временный регистр | temporary |
| R30 | T7 | Временный регистр | temporary |
| R31 | T8 | Временный регистр | temporary |


`SDX`, `SDY`, `DDX`, `DDY` — соглашение микрокода (аффинный режим, 12.12), не отдельная аппаратная фича.

## 8. Форматы пикселя и MODE

![Mode Register](gen/channel_mode.svg)
<!-- table: generated -->
**CHANNEL MODE**

| Fmt | Name | Description |
| --- | --- | --- |
| 0 | 1 bpp | 16 пикселей в слове |
| 1 | резерв | неопределённое поведение |
| 2 | 4 bpp | 4 пикселя в слове |
| 3 | 8 bpp | 2 пикселя в слове |
| 4 | 16 bpp | 1 пиксель в слове |
| 5 | PASS_LO8 | Младший байт |
| 6 | PASS_HI8 | Старший байт |
| 7 | PASS16 | Слово насквозь (16 бит) |


**`MODE` (R14) — только `TR`** (бит 0). Формат канала — в `ch_mode_[4]` (3 бита `fmt` на канал), ставится `SETMODE` (`REG_ADDR[1:0]` = канал, `ACC[2:0]` = fmt). **`COP` убран** (комбайнера нет).

<!-- table: generated -->
*[Cycle: channel_mode-table.md]*

**Порядок пикселей:** для 4 bpp `pos=0` — старшая тетрада, `pos=3` — младшая; для 8 bpp `pos=0` — старший байт, `pos=1` — младший; для 1 bpp `pos=0` — бит 15, `pos=15` — бит 0.

## 9. Загрузчик и пакеты

**Загрузчик — полная замена старому протоколу обмена.** Защищённая область BRAM 0–31 занята загрузчиком, не перезаписывается (попытка → `HALT 1`). Понятия «загрузка микрокода» и «защищённая область» — новые; это новая архитектура, не надстройка.

Три адресных канала: `S` (SIDX → SPIX), `D` (DIDX → DPIX), `DATA` (DPTR → слово данных). Третий канал — поток данных, читаемый программно самим ядром.

**Формат пакета:** последовательность блоков, каждый начинается 16-битным заголовком `{kind[15:12], arg[11:0]}`:

<!-- table: generated -->
**Заголовки пакетов загрузчика**

| Code | Name | Arg | Description |
| --- | --- | --- | --- |
| 0 | END | — | Конец, IDLE |
| 1 | ENDI | код IRQ | Конец с прерыванием |
| 2 | CODE | число микрослов | Загрузка микрокода; далее адрес и по 3 слова на микрослово |
| 3 | RUN | точка входа | Запуск микропрограммы |
| 4 | JUMP | — | Следующие 2 слова — новый DPTR |


`CODE`: arg = число микрослов; следующее слово — адрес в микрокоде; дальше по 3 слова на микрослово (36 бит в трёх 16-битных словах: `w0[15:0]`, `w1[31:16]`, `w2[35:32]`, `w2[15:4]` — резерв). `RUN`: arg = точка входа; программа сама читает свои данные и возвращается к загрузчику. `JUMP`: следующие 2 слова — новый DPTR.

Конец пакета собирается из команд, а не прячется в одной:

```
END:   FLUSH               ; REG_OP: память согласована
       IRQ 1               ; REG_OP: ACC=1, выставить код прерывания
       HALT 0              ; CTRL_OP: IDLE (успех)
```

Порядок важен: прерывание до `FLUSH` сообщило бы о рисунке, которого в памяти ещё нет. `FLUSH` синхронный. `END` (без прерывания) и `ENDI` (с ним) — разные типы заголовка.

## 10. Системные команды

| Команда | Одна функция | Чего не делает |
|---|---|---|
| `JMP`, `CALL`, `RET`, `LOOP`, `JMPA` | управление потоком | |
| `LDI`, `LDH`, `LDL` | загрузка константы из `IMM` в `OPR` | |
| `WAIT_FLAG X` | ждать, пока флаг (`IMM[5:0]`) не станет `(inv ? 0 : 1)` | не ждёт тактов, только флагов |
| `FLUSH` | согласовать память | не прерывает CPU и не останавливает ядро |
| `IRQ` | выставить событие | не сливает память и не останавливает ядро |
| `HALT X` | `X=0` → IDLE (успех); `X!=0` → ERROR | не прерывает CPU |

`SYNC` убран: его три функции разложены на `FLUSH` / `IRQ` / `HALT`. `STOP`/`CONTINUE` — команды CPU через порт. `ERROR` снимается только новым `START` (или `reset()`).

## 11. Эталонные циклы

**Заливка одним цветом** (перед циклом `DIDX` установлен через `SETD`, счётчик загружен через `LDCNT`):

```
;        REG_OP          ALU     CTRL
PIX:     PACKER_RD DEST  -       -           ; OPR = пиксель приёмника
         LDR FG          PASS    -           ; ACC = FG, OPR = пиксель
         -               AND/OR/XOR/...       ; ACC = ACC op OPR
         PACKER_WR DEST  -       LOOP PIX    ; пиксель записан
```

**Копирование спрайта**:

```
PIX:     PACKER_RD SRC   -       -
         PASS            -       -           ; ACC = пиксель источника
         STR T0          -       -           ; T0 = пиксель
         PACKER_RD DEST  -       -
         LDR T0          PASS    -           ; ACC = пиксель приёмника, OPR = T0
         PACKER_WR DEST  -       LOOP PIX
```

**Аффинный режим** — источник считается на каждый пиксель:

```
    LDX SX              ; OPR = SX (x_int)
    LDI SDX             ; OPR = SDX (12.12)
    ADD                 ; ACC = SX + SDX
    STR SX              ; SX = ACC
    SHR 12              ; ACC = x_int
    ; ... аналогично y, затем AddrPacker
```

## 12. Клиппинг и аффинный режим

Регистры клиппинга (`CX0`, `CY0`, `CX1`, `CY1`) и инкремента аффинного режима (`SDX`, `SDY`, `DDX`, `DDY`) специфицированы. **Микрокод не написан** — соглашение микрокода, не железо.

## 13. Что осознанно не делаем

- Аппаратный скроллинг и page flip.
- LUT цвет×цвет.
- Форматы 2 и 3 bpp (коды `fmt=1`, резерв).
- Третий источник (заменяется двумя проходами через скрытую страницу).
- Быстрая заливка по целому слову (решается программно).
- Палитра (не часть процессора).
- **Комбайнер (`COMB`)** — убран, логика через ALU (`AND`/`OR`/`XOR`).
- **`SKIP_IF_Z`** — убран, прозрачность через `COND Z` + `MASK CTRL`.
- **`LDSP`/`LDDP`/`STDP`** — убраны (заменены `PACKER_RD/WR`).
- **`FAULT`** — убран (`HALT X`).

## 14. Открытые вопросы

1. **`WAIT_FLAG`** (реализован).
2. **Точная раскладка микрослова** — 36 бит, `w2[3:0]` — `reg_op` (4 бита), `w2[15:4]` — резерв. **`reg_op` 5 бит** — в `w1[4:0]`? — **уточнить** в `MicroWord::pack/unpack`.
3. **Место `FLUSH`** → **`REG_OP`** (`R_FLUSH`).
4. **Аппаратные детекторы `FAULT`** — открыты.
5. **`kind` 4 бита** — хватает.
6. **36 бит vs 16** → **36 бит**, 3×16.
7. **Аффинный режим** — `SDX`/`SDY` (12.12), микрокод **не написан**.
8. **Клиппинг** — `CX0..CY1`, микрокод **не написан**.
9. **Блендинг** — `BLEND_SHIFT`, **не реализован**.
10. **Интеграция с `machine.cpp`** — `gpu_mmio` (страница 3), `set_line(5)`, `tick(t)` — **в процессе**.
