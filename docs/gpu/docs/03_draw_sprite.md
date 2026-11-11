## 4. `03_draw_sprite.md`

```markdown
# Пример: рисование спрайта под углом 45°

Аффинный режим: источник сэмплируется с шагом `(SDX, SDY)` в формате 12.12, приёмник — обычная прямоугольная область `(DX, DY, DW, DH)`.

Перед вызовом микропрограммы Z80 заполняет:

- `DX, DY, DW, DH` — область приёмника;
- `SBASE, SSTRIDE` — источник;
- `SX, SY` — начальная точка в источнике (12.12);
- `SDX, SDY` — приращения (12.12). Для поворота на 45°: `SDX = 0x1000`, `SDY = 0x1000`;
- `MODE` — формат пикселей и операция `COMB`.

Клиппинг по X показан полностью; клиппинг по Y аналогичен через `MIN`/`MAX` и здесь опущен.

```
DRAW_SPRITE:
    ; --- клиппинг по X ---
    LD SRC1, DX
    LD SRC2, CX0
    ALU MAX
    ST T3, DST                 ; T3 = x0 = MAX(DX, CX0)

    LD SRC1, DX
    LD SRC2, DW
    ALU ADD
    LD SRC2, CX1
    ALU MIN
    ST T4, DST                 ; T4 = x1 = MIN(DX + DW, CX1)

    LD SRC1, T4
    LD SRC2, T3
    ALU SUB
    ST T4, DST                 ; T4 = W' = x1 - x0
    ; COND=Z, MASK=CTRL
    JMP DONE

    LD SRC1, DH
    ST T2, DST                 ; T2 = H'

ROW:
    ; T0 = DY * DSTRIDE + x0
    LD SRC1, DY
    LD SRC2, DSTRIDE
    ALU MUL
    LD SRC2, T3
    ALU ADD
    ST T0, DST

    LD SRC1, T4
    ST T1, DST                 ; T1 = W'

PIX:
    ; sidx = (SY >> 12) * SSTRIDE + (SX >> 12)
    LD SRC1, SY
    LD SRC2, IMM 12
    ALU SHR
    LD SRC2, SSTRIDE
    ALU MUL
    ST T6, DST                 ; T6 = (SY >> 12) * SSTRIDE

    LD SRC1, SX
    LD SRC2, IMM 12
    ALU SHR
    LD SRC2, T6
    ALU ADD
    ST T6, DST                 ; T6 = sidx

    SIDX T6
    DIDX T0
    ALU COMB                   ; DPIX = COMB(SPIX, DPIX)
    WRITE DIDX, DST

    ; SX += SDX; SY += SDY
    LD SRC1, SX
    LD SRC2, SDX
    ALU ADD
    ST SX, DST

    LD SRC1, SY
    LD SRC2, SDY
    ALU ADD
    ST SY, DST

    ; T0++; T1--
    LD SRC1, T0
    LD SRC2, IMM 1
    ALU ADD
    ST T0, DST

    LD SRC1, T1
    LD SRC2, IMM 1
    ALU SUB
    ST T1, DST
    ; COND=NZ, MASK=CTRL
    JMP PIX

    ; DY++; T2--
    LD SRC1, DY
    LD SRC2, IMM 1
    ALU ADD
    ST DY, DST

    LD SRC1, T2
    LD SRC2, IMM 1
    ALU SUB
    ST T2, DST
    ; COND=NZ, MASK=CTRL
    JMP ROW

DONE:
    SYNC
    JMP MAIN
```

## Замечания по согласованию мнемоник

1. **`JMP X` с условием.** В таблице `CTRL` есть только `JMP X`. Условие задаётся полями `COND`/`MASK` того же микрослова. В примере я оставил комментарий `; COND=Z, MASK=CTRL` — это указание ассемблеру, какие поля выставить. Если хочешь мнемонический сахар `JZ`/`JNZ` — это уровень ассемблера, не микрокода; в спецификации оставляем `JMP X` + поля.
2. **`IMM 12` как операнд `ALU SHR`.** В таблице ALU операция `SHR` должна принимать `SRC2` как величину сдвига. В примере `LD SRC2, IMM 12` + `ALU SHR` — это ровно та семантика. Но `LD SRC2, IMM` в таблице нет — есть `LDL/LDH SRC2, IMM12`. Надо либо добавить в таблицу псевдоним `LD SRCk, IMM` (ассемблер раскладывает в `LDL`/`LDH` по значению), либо в примерах писать `LDL SRC2, IMM12`. **Рекомендую** добавить в таблицу строку-псевдоним:
   - `LD SRCk, IMM` — ассемблерный псевдоним: `LDL`, если IMM ≤ 0xFFF, иначе `LDH`.
   Тогда примеры остаются читаемыми.
3. **`SIDX T6` / `DIDX T0`** — согласовано с таблицей (`SIDX Rn`, `DIDX Rn`). В старом примере было `ST DIDX, T0` — исправлено.
4. **`WRITE DIDX, DST`** — согласовано с таблицей. `ALU COMB` читает `SPIX`/`DPIX` по текущим `SIDX`/`DIDX`, результат в `DST`; `WRITE` его фиксирует.
5. **`SYNC` в конце** — согласовано.

---

## Что осталось решить (открытые вопросы)

1. **Псевдоним `LD SRCk, IMM`** — добавляем в таблицу или в примерах пишем `LDL/LDH`? (Рекомендую добавить.)
2. **`COMB` в таблице ALU** — сейчас `COMB` упомянут в разделе 12 и в примерах, но в `microops_alu-table.md` его нет. Надо добавить строку `ALU COMB | DPIX ← COMB(SPIX, DPIX); DST ← DPIX | 1 (зависит от памяти)`. Пришлёшь текущий `microops_alu-table.md` — впишу.
3. **`04_fill_rect.md` и `05_copy_transparent.md`** — собрать по тому же шаблону? Скажи, и я выдам их следом (с учётом исправленных мнемоник: `DW`/`DH` вместо `W`/`H`, `SIDX`/`DIDX`, `SYNC`, `LD SRCk, IMM`).