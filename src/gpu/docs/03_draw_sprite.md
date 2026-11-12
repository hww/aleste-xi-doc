# Example: drawing a sprite rotated 45°

Affine mode: source is sampled with step `(SDX, SDY)` in 12.12 format; destination is a normal rectangle `(DX, DY, DW, DH)`.

Before calling the microprogram, Z80 fills:

- `R0..R3` (`DX, DY, DW, DH`) — destination rectangle;
- `R8` (`DSTRIDE`), `R9` (`SSTRIDE`) — strides (bytes);
- `R19` (`SDX`), `R20` (`SDY`) — increments (12.12). For 45°: `0x1000`, `0x1000`;
- `SRC.PAGE`, `SRC.MODE`, `DST.PAGE`, `DST.MODE` — channel setup;
- `CX0..CY1` — clip window.

Clipping is shown for X only; Y is symmetric.

```
DRAW_SPRITE:
    ; --- clip X: x0 = MAX(DX, CX0), x1 = MIN(DX+DW, CX1) ---
    MOV T0, R0              ; T0 = DX
    MOV T1, R15             ; T1 = CX0
    CMP T0, T1
    ; if T0 < T1: T0 = T1
    MOV T0, T1              ; COND CC (unsigned <) — T0 = CX0
    MOV T2, R0
    ADD T2, R2              ; T2 = DX + DW
    MOV T3, R17             ; T3 = CX1
    CMP T2, T3
    MOV T2, T3              ; COND CS (unsigned >=) — T2 = CX1
    SUB T2, T0              ; T2 = W' = x1 - x0
    TST T2, T2
    JMP DONE                ; COND EQ — W' == 0

    ; --- H' = DH (Y-clip omitted) ---
    MOV T4, R3              ; T4 = H' = DH

    ; --- destination IDX = y0 * DSTRIDE/2 + x0 ---
    ; (stride in bytes; word-stride = DSTRIDE >> 1)
    MOV T5, R1              ; T5 = y0 = DY
    MUL T5, R8              ; T5 = DY * DSTRIDE
    SHR T5, 1               ; T5 = DY * (DSTRIDE/2)
    ADD T5, T0              ; T5 = y0*stride_words + x0
    MOV DST.IDX, T5

    ; --- source IDX = y0 * SSTRIDE/2 + x0 (assume aligned) ---
    MOV T6, R1
    MUL T6, R9
    SHR T6, 1
    ADD T6, T0
    MOV SRC.IDX, T6

ROW:
    MOV T7, T2              ; T7 = W' (pixels left in row)

PIX:
    ; --- read source pixel (affine: source advanced by SDX/SDY) ---
    MOV T8, SRC.PIX         ; T8 = source pixel

    ; --- write destination pixel ---
    MOV DST.PIX, T8

    ; --- advance source by (SDX, SDY) in 12.12 ---
    ; (in this example stride is 1 pixel per step; affine uses MUL/SHR)
    ; source IDX += 1 (linear); for true affine, rebuild IDX from SX/SY
    MOV T0, SRC.IDX
    ADD T0, 1
    MOV SRC.IDX, T0

    ; --- loop ---
    MOV T7, T7              ; T7 -= 1
    SUB T7, 1
    TST T7, T7
    JMP PIX                 ; COND NE — more pixels in row; L via LOOP

    ; --- next row ---
    MOV DST.IDX, T5         ; restore row start
    ADD T5, R8              ; T5 += DSTRIDE (next row, bytes)
    SHR T5, 1               ; word offset
    MOV T4, T4
    SUB T4, 1
    TST T4, T4
    JMP ROW                 ; COND NE — more rows

DONE:
    MOV FLUSH, ZERO
    IRQ 0
    HALT 0
```

**Notes**

1. **`MOV R, ch.PIX` / `MOV ch.PIX, R`** — read/write a pixel; `fmt` from `ch.MODE`, address from `ch.IDX`. Source advances on read, destination on write by `ch.STEP`.
2. **`MOV ch.IDX, R`** — set pixel index; next `PIX` access uses it.
3. **Affine mode** rebuilds `SRC.IDX` from `SX/SY` each pixel:
   ```
   ADD R4, R19             ; SX += SDX
   ADD R5, R20             ; SY += SDY
   MOV T6, R5
   SHR T6, 12              ; SY_int
   MOV T5, R4
   SHR T5, 12              ; SX_int
   MUL T6, R9              ; SY_int * SSTRIDE
   SHR T6, 1
   ADD T6, T5              ; + SX_int
   MOV SRC.IDX, T6
   ```
4. **`JMP` with `COND`** — the condition is in `COND` of the same word. `JMP DONE` with `COND EQ` means "jump if zero".
5. **End of packet:** `MOV FLUSH, ZERO; IRQ 0; HALT 0`.

