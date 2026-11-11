# Example: filling a rectangle with a solid colour

Destination is a normal rectangle `(DX, DY, DW, DH)`. No source is read. The colour comes from `FG` (foreground register R12). Clipping is done before the loop.

Before calling the microprogram, Z80 fills:

- `DX, DY, DW, DH` — destination rectangle;
- `DSTRIDE, DBASE` — destination layout;
- `FG` — fill colour;
- `MODE` — destination format (`DFMT`).

## Pseudocode

```
FILL_RECT:
    ; --- clip X ---
    ; x0 = MAX(DX, CX0)
    ; x1 = MIN(DX + DW, CX1)
    ; W' = x1 - x0
    ; if W' == 0: JMP DONE
    ; (same as DRAW_SPRITE, omitted here)

    ; --- clip Y ---
    ; y0 = MAX(DY, CY0)
    ; y1 = MIN(DY + DH, CY1)
    ; H' = y1 - y0
    ; if H' == 0: JMP DONE

    ; T0 = y0 * DSTRIDE + x0   (word address of the first pixel)
    ; T1 = W'
    ; T2 = H'

    LDX T1
    LDCNT                   ; loop counter = W' (single row)

ROW:
    ; --- inner loop, W' pixels ---
PIX:
    ; A = (y << 12) | x   (current source-less coordinate)
    ; ... build A from T0 (word address) → need x, y separately
    ; Simpler: keep x and y as counters and use ADDR ch
    LDX XREG
    STR T6                  ; save x
    LDX YREG
    SHR 12
    ; A[23:12] = y, A[11:0] = x  (via LDH/LDL from T6/XREG)
    ; ADDR DEST
    ; LDR FG
    ; PACKER_WR DEST
    ; XREG++ ; T1--
    ; if T1 != 0: JMP PIX

    ; T1 = W' (reload)
    ; YREG++ ; T2--
    ; if T2 != 0: JMP ROW

DONE:
    FLUSH
    IRQ
    HALT 0
```

## Revised, microcode-accurate version

```
; registers used:
;   R0 = X (current destination x)
;   R1 = Y (current destination y)
;   R2 = W' (remaining pixels in row)
;   R3 = H' (remaining rows)
;   R12 = FG (fill colour)
;   R8 = DSTRIDE, R10 = DBASE

FILL_RECT:
    ; --- clip X ---
    ; x0 = MAX(DX, CX0); x1 = MIN(DX + DW, CX1)
    ; W' = x1 - x0
    LDX T0                  ; A = W'
    CMP 0                   ; flags from A - 0
    ; COND Z, MASK CTRL
    JMP DONE

    ; --- clip Y ---
    ; y0 = MAX(DY, CY0); y1 = MIN(DY + DH, CY1)
    ; H' = y1 - y0
    LDX T1                  ; A = H'
    CMP 0
    JMP DONE                ; COND Z, MASK CTRL

    LDX x0
    STR R0                  ; X = x0
    LDX y0
    STR R1                  ; Y = y0

ROW:
    LDX W'
    STR R2                  ; R2 = W'
    LDX R0
    STR R4                  ; R4 = X (working x)

PIX:
    ; A = (Y << 12) | X   (coordinate for AddrPacker)
    LDX R4
    STR T6                  ; T6 = X
    LDX R1
    SHR 12
    ; LDH: A[23:12] = Y_int; A[11:0] = X (from T6)
    ; In the simulator: LDI X; LDH Y_int
    LDX T6
    STR A                   ; A = X (low 12)
    LDX R1
    SHR 12                  ; A = Y_int
    LDH A                   ; A[23:12] = Y_int, A[11:0] unchanged

    ; ADDR DEST: AddrPacker computes ADDR_ = addr24, pos
    ; PACKER_WR DEST: write FG at ADDR_
    LDR FG
    PACKER_WR DEST

    ; R4++ ; R2--
    LDX R4
    LDI_PUSH 1
    ADD                     ; A = X + 1
    STR R4

    LDX R2
    LDI_PUSH 1
    SUB                     ; A = R2 - 1
    STR R2
    CMP 0
    JMP PIX                 ; COND NZ, MASK CTRL

    ; R1++ ; R3--
    LDX R1
    LDI_PUSH 1
    ADD
    STR R1

    LDX R3
    LDI_PUSH 1
    SUB
    STR R3
    CMP 0
    JMP ROW                 ; COND NZ, MASK CTRL

DONE:
    FLUSH
    IRQ
    HALT 0
```

## Notes

1. **`COND`/`MASK` on `JMP`.** The condition is encoded in the `COND`/`MASK` fields of the `JMP` micro-word. `MASK CTRL` blocks the jump when the condition is false, so execution falls through. This is the standard pattern: `CMP 0; JMP target` with `COND NZ, MASK CTRL` means "jump if non-zero".

2. **No `IMM 12` as an operand.** `LD SRCk, IMM` is not a microcode instruction; use `LDI` (replaces A) or `LDL`/`LDH` (partial writes). The assembler may add a pseudo-op that expands `LD SRCk, IMM` into `LDI` + `LDH` depending on the value.

3. **Coordinates and `AddrPacker`.** The destination is addressed by `x`/`y` in 12.12. `AddrPacker` takes `(x_int << 12) | y_int` from A (built with `LDI x_int; LDH y_int`), `base`/`stride` from `R10`/`R8`, and `fmt` from `ch_mode_[DEST]`. The resulting `addr24` and `pos` go into `ADDR_`.

4. **No `MUL` in microcode.** The multiplication `Y * DSTRIDE` is done by the DSP **inside `AddrPacker`**, not by the ALU. Microcode never issues `MUL`.

5. **Loop counter.** `LDCNT` loads `CNT` with A. `LOOP X` decrements `CNT` and jumps if non-zero. This is the cleanest loop construct. `CMP 0` + `JMP` is used when the loop count is not needed after the loop.
