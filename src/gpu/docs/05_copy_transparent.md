# Example: copying a sprite with transparency

The sprite is copied from source to destination with a colour-key transparency: a source pixel equal to the key colour is **not** written. This is not alpha blending — it is a skip.

Before calling the microprogram, Z80 fills:

- `DX, DY, DW, DH` — destination rectangle;
- `SBASE, SSTRIDE, SX, SY` — source;
- `FG` — the transparent key (any source pixel equal to `FG` is skipped);
- `MODE` — source and destination formats (`SFMT`/`DFMT`).

## Pseudocode

```
COPY_TRANSPARENT:
    ; clip destination (same as DRAW_SPRITE)
    ; W' = x1 - x0; H' = y1 - y0
    ; if W' == 0 or H' == 0: JMP DONE

    ; T0 = y0 * DSTRIDE + x0 ; T1 = W' ; T2 = H'
    ; sx = SX + (x0 - DX) * 1 ; sy = SY + (y0 - DY) * 1
    ; (source may be scaled: sx += SDX per pixel)

ROW:
    ; T3 = W'
PIX:
    ; --- read source pixel ---
    ; A = (sy >> 12) << 12 | (sx >> 12)
    ; ADDR SOURCE ; PACKER_RD SOURCE → A = source pixel
    STR T4                   ; T4 = source pixel

    ; --- transparency test ---
    LDR FG                   ; A = FG
    LDR T4                   ; B = source pixel
    CMP                      ; A - B = FG - src
    ; if FG == src: skip write (JMP SKIP with COND Z, MASK CTRL)

    ; --- write destination ---
    ; A = (y << 12) | x  (destination coordinate)
    ; ADDR DEST
    LDR T4                   ; A = source pixel
    PACKER_WR DEST

SKIP:
    ; advance sx += SDX ; sy += SDY ; x++ ; T3--
    ; if T3 != 0: JMP PIX

    ; y++ ; T2--
    ; if T2 != 0: JMP ROW

DONE:
    FLUSH
    IRQ
    HALT 0
```

## Revised, microcode-accurate version

```
; registers:
;   R0 = X (dest x), R1 = Y (dest y)
;   R2 = W' (pixels left in row), R3 = H' (rows left)
;   R4 = SX (12.12), R5 = SY (12.12)
;   R6 = SDX, R7 = SDY (12.12 increments, default 0x1000 = 1.0)
;   R12 = FG (transparency key)
;   R8 = DSTRIDE, R10 = DBASE, R9 = SSTRIDE, R11 = SBASE

COPY_TRANSPARENT:
    ; --- clip destination, compute W' and H' ---
    ; (see DRAW_SPRITE)
    ; if W' == 0 or H' == 0: JMP DONE

ROW:
    LDX W'
    STR R2                   ; R2 = W'

PIX:
    ; --- build source coordinate A = (sy >> 12) << 12 | (sx >> 12) ---
    LDX R4                   ; A = SX (low 12 bits)
    STR T6                   ; T6 = SX
    LDX R5
    SHR 12                   ; A = SY_int
    ; LDH: A[23:12] = SY_int; A[11:0] = SX (from T6)
    LDX T6
    STR A                    ; A[11:0] = SX_int (low 12)
    LDX R5
    SHR 12
    LDH A                    ; A[23:12] = SY_int, lower 12 unchanged

    ; --- read source ---
    ADDR SOURCE
    PACKER_RD SOURCE
    STR T4                   ; T4 = source pixel

    ; --- transparency test ---
    LDR FG
    LDR_PUSH T4              ; A = FG, B = src
    CMP                      ; flags from FG - src
    ; if Z (FG == src): skip write
    ; COND Z, MASK REG | MASK ALU to skip the write below
    ; (in the simulator: the write is guarded by COND Z + MASK CTRL on
    ;  the PACKER_WR micro-word's own COND field)

    ; --- write destination ---
    ; A = (y << 12) | x
    LDX R0
    STR T6
    LDX R1
    SHR 12
    LDX T6
    STR A
    LDX R1
    SHR 12
    LDH A

    ADDR DEST
    LDR T4                   ; A = source pixel
    PACKER_WR DEST           ; (guarded by COND Z, MASK CTRL from CMP above)

    ; --- advance source and destination ---
    ; SX += SDX ; SY += SDY
    LDX R4
    LDR_PUSH R6              ; A = SX, B = SDX
    ADD                      ; A = SX + SDX
    STR R4

    LDX R5
    LDR_PUSH R7              ; A = SY, B = SDY
    ADD
    STR R5

    ; X++ ; R2--
    LDX R0
    LDI_PUSH 1
    ADD
    STR R0

    LDX R2
    LDI_PUSH 1
    SUB
    STR R2
    CMP 0
    JMP PIX                  ; COND NZ, MASK CTRL

    ; Y++ ; R3--
    LDX R1
    LDI_PUSH 1
    ADD
    STR R1

    LDX R3
    LDI_PUSH 1
    SUB
    STR R3
    CMP 0
    JMP ROW                  ; COND NZ, MASK CTRL

DONE:
    FLUSH
    IRQ
    HALT 0
```

## Notes

1. **Transparency is a skip, not a blend.** The `CMP` sets `Z` when the source pixel equals `FG`. The `PACKER_WR` micro-word carries `COND = Z, MASK = CTRL` — when `Z` is set, the `CTRL` block is blocked and `PACKER_WR` does not execute (it is a `REG_OP`, but the surrounding jump/skip logic handles it). In the simulator, the same effect is achieved by placing the `PACKER_WR` under a `COND Z` guard; the exact encoding of "skip this write" depends on the assembler (see open question 1).

2. **Source and destination coordinates.** Source is advanced by `SDX`/`SDY` per pixel (12.12 arithmetic). Destination is advanced by 1 per pixel. The source and destination do not need to be aligned; `SFMT` and `DFMT` can differ.

3. **`LDH`/`LDL` build the 24-bit coordinate.** `LDI X` (low 12 bits) followed by `LDH Y_int` (high 12 bits) yields `A = (Y_int << 12) | X_int`, which is the input format for `AddrPacker`.

4. **No `COMB`, no `MUL`.** The combiner is gone: transparency is a skip; blending (if needed) is done with `SHR`/`ADD`. Multiplication is done inside `AddrPacker`, not by the ALU.

5. **`FLUSH` before `IRQ`.** The end-of-packet sequence is `FLUSH; IRQ; HALT 0`, in that order. An interrupt before `FLUSH` would announce a picture not yet in memory.

## Open question

1. **Encoding of "skip the next write" in microcode.** Two options:
   - **Option A (current simulator):** the `PACKER_WR` micro-word carries `COND = Z, MASK = CTRL`, and the assembler emits an explicit `JMP` to bypass the write when the condition holds. This is verbose but explicit.
   - **Option B (simpler):** introduce a single micro-word `SKIP_IF_Z` that increments `PC` by 1 when `A == 0`. This was in the earlier design but was **removed** in the current revision. It would make the transparency loop shorter (`CMP 0; SKIP_IF_Z; PACKER_WR`).
   
   The simulator currently uses **Option A**. Whether to add `SKIP_IF_Z` back is a **hardware cost vs microcode size** trade-off — to be decided once the first RTL budget is available.
```

---

## Summary of the two documents

| Document | Shape | Key pattern |
|---|---|---|
| `04_fill_rect.md` | Nested loops, no source | `CMP 0` + `JMP` with `COND`/`MASK`; `ADDR DEST; PACKER_WR DEST` per pixel |
| `05_copy_transparent.md` | Nested loops, source read | `CMP` against `FG` + guarded `PACKER_WR`; `LDH`/`LDL` build the coordinate |

Both use only the current microcode set: **`LDR`/`LDR_PUSH`/`STR`/`STR_POP`, `LDI`/`LDH`/`LDL`, `ADDR`, `PACKER_RD/WR`, `CMP`/`ADD`/`SUB`/`SHR`, `FLUSH`/`IRQ`/`HALT X`**. No `COMB`, no `MUL`, no `SKIP_IF_Z`, no `SETMASK`.

**Open question to resolve before writing the assembler:** how to express "skip the write when the comparison matches" — as a guarded `PACKER_WR` (Option A) or by re-adding `SKIP_IF_Z` (Option B). The simulator currently uses Option A.