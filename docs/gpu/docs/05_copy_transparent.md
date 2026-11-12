# Example: copying a sprite with transparency

Source pixel equal to key `FG` is **not** written (skip, not blend).

Before calling the microprogram, Z80 fills:

- `R0..R3` (`DX, DY, DW, DH`);
- `R8` (`DSTRIDE`), `R10` (`DBASE`);
- `R9` (`SSTRIDE`), `R11` (`SBASE`);
- `R12` (`FG`) — transparent key;
- `SRC.PAGE`, `SRC.MODE`, `DST.PAGE`, `DST.MODE`.

```
COPY_TRANSPARENT:
    ; --- clip (same as DRAW_SPRITE) ---
    ; compute W' (T2), H' (T5), x0 (T0), y0 (T3)
    ; if W' == 0 or H' == 0: JMP DONE

    ; --- SRC.IDX = y0 * SSTRIDE/2 + x0 ---
    MOV T6, T3
    MUL T6, R9
    SHR T6, 1
    ADD T6, T0
    MOV SRC.IDX, T6

    ; --- DST.IDX = y0 * DSTRIDE/2 + x0 ---
    MOV T7, T3
    MUL T7, R8
    SHR T7, 1
    ADD T7, T0
    MOV DST.IDX, T7

    MOV R2, T5              ; R2 = H'

ROW:
    MOV T7, T2              ; T7 = W'
    MOV T8, SRC.IDX         ; T8 = row-start SRC.IDX
    MOV T9, DST.IDX         ; T9 = row-start DST.IDX

PIX:
    MOV T0, SRC.PIX         ; T0 = source pixel
    ; --- transparency test: skip if T0 == FG ---
    CMP T0, R12
    JMP SKIP                ; COND EQ

    MOV DST.PIX, T0         ; write source pixel

SKIP:
    ; --- advance source linearly (affine: rebuild from SX/SY) ---
    MOV T1, SRC.IDX
    ADD T1, 1
    MOV SRC.IDX, T1

    MOV T1, T7
    SUB T1, 1
    MOV T7, T1
    TST T7, T7
    JMP PIX                 ; COND NE

    ; --- next row: rewind SRC.IDX and DST.IDX to row start, add stride ---
    MOV T1, T8
    ADD T1, R9              ; SRC.IDX += SSTRIDE (bytes)
    SHR T1, 1
    MOV SRC.IDX, T1

    MOV T1, T9
    ADD T1, R8              ; DST.IDX += DSTRIDE
    SHR T1, 1
    MOV DST.IDX, T1

    MOV R2, R2
    SUB R2, 1
    TST R2, R2
    JMP ROW                 ; COND NE

DONE:
    MOV FLUSH, ZERO
    IRQ 0
    HALT 0
```

**Notes**

1. **Transparency is a skip.** `CMP T0, R12` sets `Z` when source == `FG`. `JMP SKIP` with `COND EQ` bypasses `MOV DST.PIX, T0`. No `COMB`, no blending.
2. **`SRC.PIX` on read advances `SRC.IDX` by `SRC.STEP`.** If `STEP=1`, the explicit `SRC.IDX += 1` is redundant — remove it. If `STEP=0` (manual advance for affine), keep the explicit `ADD`.
3. **Row rewind.** `SRC.IDX` and `DST.IDX` are saved at row start (`T8`, `T9`), then advanced by stride at the end of the row.
4. **No `SKIP_IF_Z`.** The skip is a `JMP` with `COND EQ`. This is the same as `01_architecture.md` says: transparency via `COND` on a jump, not a special instruction.
5. **End of packet:** `MOV FLUSH, ZERO; IRQ 0; HALT 0`.
