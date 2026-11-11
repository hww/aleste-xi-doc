# Example: drawing a sprite rotated 45°

Affine mode: source sampled with step `(SDX, SDY)` in 12.12 format; destination is a normal rectangle `(DX, DY, DW, DH)`.

Before calling the microprogram, Z80 fills:

- `DX, DY, DW, DH` — destination rectangle;
- `SBASE, SSTRIDE` — source;
- `SX, SY` — initial source point (12.12);
- `SDX, SDY` — increments (12.12). For a 45° rotation: `SDX = 0x1000`, `SDY = 0x1000`;
- `MODE` — pixel formats and `TR` bit.

X clipping shown in full; Y clipping is symmetric (via `CMP` + `COND`/`MASK`).

```
DRAW_SPRITE:
    ; --- clip X ---
    LDX CX0
    STR T3                 ; T3 = CX0
    LDX DX
    STR T0                 ; T0 = DX
    ; if DX < CX0: T3 = CX0, else T3 = DX
    ; CMP T0, T3
    LDX T0
    LDI_PUSH T3
    ; ... SUB, COND N, MASK REG to keep max
    ; (pseudo — real code uses CMP + COND/MASK)

    ; x1 = MIN(DX + DW, CX1)
    LDX DX
    LDI_PUSH DW
    ; ADD -> A = DX + DW
    STR T4
    LDX CX1
    STR T5
    ; CMP T4, T5 -> keep min

    ; W' = x1 - x0
    LDX T4
    LDI_PUSH T3
    ; SUB -> W'
    STR T4

    ; if W' == 0: JMP DONE (COND Z, MASK CTRL)

    ; H' = DH
    LDX DH
    STR T2

ROW:
    ; T0 = DY * DSTRIDE + x0  (AddrPacker-style arithmetic in microcode)
    LDX DY
    LDI_PUSH DSTRIDE
    ; (multiplication: shift/add for small values; full DSP not exposed to ALU)
    ; then ADD x0
    STR T0

    ; T1 = W'
    LDX T4
    STR T1

PIX:
    ; SX += SDX
    LDX SX
    LDI_PUSH SDX
    ; ADD (12.12 addition)
    STR SX

    ; SY += SDY
    LDX SY
    LDI_PUSH SDY
    ; ADD
    STR SY

    ; A = (SY_int << 12) | SX_int
    LDX SX
    STR T6
    LDX SY
    SHR 12
    ; LDH T6?  -> A[23:12] = SY_int, A[11:0] = SX_int
    ; (in the simulator: LDI SX_int; LDH SY_int)

    ; ADDR SRC: ADDR_ = AddrPacker(A), pos
    ; PACKER_RD SRC  -> A = source pixel
    ; STR T7
    ; ADDR DEST
    ; LDR T7
    ; PACKER_WR DEST

    ; T0++; T1--
    ; if T1 != 0: JMP PIX

    ; DY++; T2--
    ; if T2 != 0: JMP ROW

DONE:
    FLUSH
    IRQ
    HALT 0
```

**Notes on mnemonics**

1. **`JMP X` with a condition.** `CTRL_OP` has `JMP X`; the condition lives in `COND`/`MASK` of the same micro-word. Mnemonic sugar like `JZ`/`JNZ` is assembler-level, not microcode.
2. **`LDI` vs `LDH`/`LDL`.** `LDI` replaces A entirely (sign-extended). `LDH`/`LDL` modify only the upper/lower 12 bits, so `LDI low; LDH high` builds a 24-bit value.
3. **`SIDX`/`DIDX` set via `ADDR ch`.** The address is computed by `AddrPacker` and stored in `ADDR_`; `PACKER_RD/WR` consume it.
4. **`WRITE`** is `PACKER_WR ch=REG_ADDR[1:0]`.
5. **`FLUSH` + `IRQ` + `HALT 0`** at the end of the packet, in that order.

---

## Open questions

1. **`LD SRCk, IMM` pseudo-op** — add or use `LDI`/`LDH`/`LDL` explicitly? (Recommendation: add assembler pseudo-op that expands into `LDI` + `LDH` if the value is 12-bit, otherwise `LDH` only.)
2. **`COMB`** — removed from the ALU. Transparency is done via `COND Z` + `MASK CTRL` on `PACKER_WR`. Blending is shift-based (`SHR` + `ADD`).
3. **`04_fill_rect.md`, `05_copy_transparent.md`** — should I generate them next, using the updated mnemonics (`DW`/`DH`, `SIDX`/`DIDX`, `FLUSH`, `LDI`/`LDH`/`LDL`)?
```

---

## Summary of changes baked into the docs

| Item | Old | New |
|---|---|---|
| Data model | `ACC`/`OPR` parallel | **Stack A/B/C**, push/pop, C=0 on pop |
| Microcode | 36-bit, `CTRL_OP` 5 | 36-bit, `REG_OP` 5, `ALU_OP` 5, **`CTRL_OP` 3** |
| ALU | 16 ops incl. MUL/MIN/MAX/ADDS/SUBS/COMB | **16 `LOGIC` LUT + ADD/SUB/CMP/SHL/SHR/SAR**, rest reserved |
| Multiplication | `MUL` in ALU | **DSP inside `AddrPacker`** |
| Saturation | `ADDS`/`SUBS` | **removed** (via `SUB` + `COND`) |
| Combiner | `COMB` | **removed** (logic via `LOGIC`, transparency via `COND`/`MASK`) |
| `SKIP_IF_Z` | in `CTRL_OP` | **removed** |
| `FAULT` | in `REG_OP` | **removed** (`HALT X`, `X != 0`) |
| `SETMASK`, `mask_` | in `REG_OP` / GPU | **removed** |
| `LDH`/`LDL` | replace A | **partial write** (`A[23:12]`, `A[11:0]`) |
| `OperandMap` | 32..44 | **`DeviceMap` 0..31**, flags + inverses |
| `WAIT_FLAG` | `IMM[5:0]` | **`REG_ADDR`** (device number, 5 bits) |
| `PACKER_*` | `ACC` = `(y<<12)|x` | **`ADDR` fills `ADDR_`**, `PACKER_*` consume it |
| Affine | `ACC[11:0]=x`, `ACC[23:12]=y` | **A = `(y<<12)|x`** via `LDI`/`LDH` |
