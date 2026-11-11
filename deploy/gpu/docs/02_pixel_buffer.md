# LX-GPU: архитектура пиксельного буферного блока

Цель — проверить архитектурную идею и основные ограничения будущего железа, а не строить точный RTL- или цикл-в-цикл симулятор.

## 1. Общая структура

Один общий буферный модуль с четырьмя логическими записями:

| Номер | Назначение |
|---|---|
| 0 | SOURCE — чтение исходных пикселей |
| 1 | DESTINATION — чтение и изменение пикселей назначения с последующей записью |
| 2 | DATA — поток обычных 16-битных слов |
| 3 | RESERVED — резерв |

**Реализация:** `PixelBuffer` — один класс, `BufferEntry e_[4]`:

```cpp
struct BufferEntry {
    uint16_t tag;      // младшие 16 бит адреса слова
    uint16_t data;     // 16-битное содержимое
    uint8_t  page;     // старшие 8 бит адреса (страница)
    bool     valid;
    bool     dirty;    // для DEST; для SOURCE/DATA всегда false
};
```

**Не** «BRAM 4 записи» — **4 структуры** в C++. Ширина BRAM — **не фиксирована** (отложено до RTL). `page` (8 бит) — **не входит** в TAG (16 бит): `page_of(addr24) = addr24 >> 16`, `tag_of(addr24) = addr24 & 0xFFFF`.

## 2. Форматы пикселей

Буфер работает с 16-битными словами. `fmt` — в `PixelPacker` (не в буфере). 8 кодов:

| Код | Формат | Пикселей в слове |
|---|---|---|
| 0 | 1 bpp | 16 |
| 1 | резерв | — |
| 2 | 4 bpp | 4 |
| 3 | 8 bpp | 2 |
| 4 | 16 bpp | 1 |
| 5 | PASS_LO8 | — |
| 6 | PASS_HI8 | — |
| 7 | PASS16 | — |

1 bpp — **источник** (маски, шрифты), но `AddrPacker`/`PixelPacker` **умеют** и как приёмник (16 пикселей/слово).

## 3. Адресация

Адресную арифметику **не** переносить внутрь буфера. `AddrPacker` (отдельный класс) формирует `addr24` + `pos` из `x_int`/`y_int` (в `ACC`), `base`/`stride` (в регистрах), `fmt` (`ch_mode_[ch]`). Буфер получает **готовый `addr24`** (24 бита) и **`pos`** (0..15).

Видеоконтроллер адресует страницы по 64 КБ. TAG — **16 бит** (младшие), `page` — **8 бит** (старшие). При смене страницы — `set_page(ch, page)` (writeback dirty, сброс канала).

## 4. Назначение каналов

**SOURCE** — чтение исходных пикселей. `PACKER_RD ch=SOURCE`, `pos` из `AddrPacker`, `fmt` из `ch_mode_[SOURCE]`.

**DESTINATION** — чтение + запись. `PACKER_RD ch=DEST` (read), `PACKER_WR ch=DEST` (write, с `mask_`). Dirty — **флаг на запись** (не маска байтов): пишется **всё слово** (`write16`).

**DATA** — 16-битные слова, без пиксельной логики. `PACKER_RD/WR ch=DATA` — через `DPTR` (не `AddrPacker`), `fmt` из `ch_mode_[DATA]` (`PASS16`/`PASS_LO8`/`PASS_HI8`).

**RSV** — резерв, не используется.

## 5. HIT/MISS

`BufferEntry`: `{tag, data, page, valid, dirty}`. **DIRTY — один флаг** (не маска байтов). Запись — **всё слово** (`write16`).

При обращении:
1. Проверить `valid` и `tag == tag_of(addr)` и `page == page_of(addr)`.
2. HIT → `data`, `hits++`, 1 такт.
3. MISS → если `dirty`, `write16(page<<16 | tag, data)`, `writebacks++`, `MISS_CYCLES`; заполнить `data = read16(addr)`, `valid=true`, `dirty=false`, `misses++`, `MISS_CYCLES`.

`MISS_CYCLES = 6` — **модель**, не RTL.

## 6. Доступ к памяти

`Memory16` — обёртка над `uint8_t*` (композиция, `Memory16(base, size)`). `read16`/`write16` — 16-битные, little-endian. В `Machine`: `gpu_mem_(mem.data(), MEM_SIZE)` — **не владеет** (`owns_=false`).

Wishbone — общий интерфейс. 4 записи — **не** 4 параллельных порта. Одна транзакция за раз.

## 7. Принципы реализации

- Один буфер, **не** три кэша. `PixelBuffer` — один класс, `ch` — enum (0..3).
- `AddrPacker` — **вне** буфера, **в** `GPU`.
- `DATA` — `DPTR` (нет отдельного инкрементатора).
- `set_page` — **на канал** (writeback dirty канала, сброс).
- `flush` — **глобальный** (writeback всех dirty, инвалидация).
- `MISS_CYCLES = 6` — модель, не RTL.

## 8. Что требуется от модели

Реализовано:
- 4 записи (`BufferEntry e_[4]`);
- `TAG`/`VALID`/`DIRTY`;
- `HIT`/`MISS`;
- writeback dirty DEST перед вытеснением;
- fill при MISS;
- `set_page` (writeback канала, сброс);
- `flush` (writeback всех, инвалидация);
- `buffer_error()` — модель **показывает** ошибку (обращение к чужой странице без `set_page`);
- счётчики `hits`/`misses`/`writebacks`.

Тесты: `test_fill`, `test_sprite`, `test_sprite8`, `test_loop`, `test_setpage`, `test_page_error`, `test_mask`, `test_1bpp`, `test_pass`, `test_mmio` — **15 тестов PASS**.

**`test_page_error`** — **модель показывает ошибку** (`buffer_error()`), **не скрывает**. Это **важнее** «удобства»: если микрокод забыл `set_page`, GPU **не должен** молча писать в чужую страницу.

**Важно:** точная ширина BRAM, структура dirty-масок (флаг vs маска байтов), FSM, интерфейс ожидания/готовности — **отложены** до RTL. В модели — **флаг** (проще, пишется всё слово).
