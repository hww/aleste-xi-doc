# Example: filling a rectangle with a solid colour

Destination is a normal rectangle `(DX, DY, DW, DH)`. No source is read. Colour comes from `FG` (R12). Clipping is done before the loop.

Before calling the microprogram, Z80 fills:

- `R0..R3` (`DX, DY, DW, DH`);
- `R8` (`DSTRIDE`), `R10` (`DBASE`);
- `R12` (`FG`) — fill colour;
- `DST.PAGE`, `DST.MODE` — channel setup.

```
FILL_RECT:
    ; --- clip X: x0 = MAX(DX, CX0), x1 = MIN(DX+DW, CX1) ---
    MOV T0, R0
    MOV T1, R15
    CMP T0, T1
    MOV T0, T1              ; COND CC — x0 = CX0
    MOV T2, R0
    ADD T2, R2              ; x1 = DX + DW
    MOV T3, R17
    CMP T2, T3
    MOV T2, T3              ; COND CS — x1 = CX1
    SUB T2, T0              ; W' = x1 - x0
    TST T2, T2
    JMP DONE                ; COND EQ

    ; --- clip Y: y0 = MAX(DY, CY0), y1 = MIN(DY+DH, CY1) ---
    MOV T3, R1
    MOV T4, R16
    CMP T3, T4
    MOV T3, T4              ; COND CC — y0 = CY0
    MOV T5, R1
    ADD T5, R3              ; y1 = DY + DH
    MOV T6, R18
    CMP T5, T6
    MOV T5, T6              ; COND CS — y1 = CY1
    SUB T5, T3              ; H' = y1 - y0
    TST T5, T5
    JMP DONE                ; COND EQ

    ; --- destination IDX = y0 * DSTRIDE/2 + x0 ---
    MOV T6, T3
    MUL T6, R8
    SHR T6, 1
    ADD T6, T0
    MOV DST.IDX, T6

    ; --- LOOP: count = W', target = PIX ---
    ; LOOP = (W' << 12) | PIX
    MOV T7, T2
    SHL T7, 12
    LDI24 T8, PIX
    OR  T7, T8
    MOV LOOP, T7

    MOV R2, T5              ; R2 = H' (rows left)

ROW:
    MOV DST.PIX, R12        ; write FG; DST.IDX += DST.STEP (1)
    ; L=1 above; LOOP decrements count, jumps to PIX until 0.

    ; --- next row ---
    ; DST.IDX = DST.IDX + DSTRIDE/2 - W'  (rewind to row start + stride)
    MOV T0, R8
    SHR T0, 1
    SUB T0, T2
    MOV T1, DST.IDX
    ADD T1, T0
    MOV DST.IDX, T1

    ; --- restore LOOP for next row ---
    MOV T7, T2
    SHL T7, 12
    LDI24 T8, PIX
    OR  T7, T8
    MOV LOOP, T7

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

1. **`LOOP` register** — `count | target`. The instruction with `L=1` (here `MOV DST.PIX, R12`) runs, then `LOOP` decrements `count` and jumps to `target` if `count > 1`, else falls through.
2. **`MOV ch.PIX, R`** writes one pixel, advances `ch.IDX` by `ch.STEP`.
3. **`MUL`** — 24×24 → low 24 bits. Stride is in bytes; `SHR 1` converts to words. For 4 bpp, `DST.IDX` is a pixel index, so `DSTRIDE` is used as pixels-per-row, not bytes — adjust the test setup accordingly.
4. **`LDI24 T8, PIX`** — load a 24-bit constant (the loop target). `PIX` is a microcode label; the assembler resolves it.

