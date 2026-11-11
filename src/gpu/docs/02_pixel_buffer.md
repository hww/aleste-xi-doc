# LX-GPU: pixel buffer block architecture

Goal: validate the architectural idea and the main hardware constraints, not to build an exact RTL or cycle-accurate simulator.

## 1. Structure

A single shared buffer module with four logical entries:

| Number | Purpose |
|---|---|
| 0 | SOURCE — read source pixels |
| 1 | DESTINATION — read-modify-write destination pixels |
| 2 | DATA — plain 16-bit words |
| 3 | RESERVED |

**Implementation:** `PixelBuffer` — one class, `BufferEntry e_[4]`:

```cpp
struct BufferEntry {
    uint16_t tag;      // low 16 bits of the word address
    uint16_t data;     // 16-bit content
    uint8_t  page;     // high 8 bits of the address (page)
    bool     valid;
    bool     dirty;    // for DEST; always false for SOURCE/DATA
};
```

Not "BRAM with 4 entries" — four C++ structs. BRAM width is not fixed (deferred to RTL). `page` (8 bits) is not part of TAG (16 bits): `page_of(addr24) = addr24 >> 16`, `tag_of(addr24) = addr24 & 0xFFFF`.

## 2. Pixel formats

The buffer works with 16-bit words. `fmt` lives in `PixelPacker`, not in the buffer. 8 codes:

| Code | Format | Pixels per word |
|---|---|---|
| 0 | 1 bpp | 16 |
| 1 | reserved | — |
| 2 | 4 bpp | 4 |
| 3 | 8 bpp | 2 |
| 4 | 16 bpp | 1 |
| 5 | PASS_LO8 | — |
| 6 | PASS_HI8 | — |
| 7 | PASS16 | — |

1 bpp is a source format (masks, fonts); `AddrPacker` and `PixelPacker` support it as a destination too (16 pixels per word).

## 3. Addressing

Address arithmetic does not belong in the buffer. `AddrPacker` (a separate class) produces `addr24` + `pos` from `x_int`/`y_int` (in A), `base`/`stride` (in registers), and `fmt` (`ch_mode_[ch]`). The buffer receives a ready `addr24` (24 bits) and `pos` (0..15).

The video controller addresses 64 KB pages. TAG is 16 bits (low), `page` is 8 bits (high). A page change uses `set_page(ch, page)` (write back dirty, reset the channel).

## 4. Channel purposes

**SOURCE** — read source pixels. `PACKER_RD ch=SOURCE`, `pos` from `AddrPacker`, `fmt` from `ch_mode_[SOURCE]`.

**DESTINATION** — read + write. `PACKER_RD ch=DEST` (read), `PACKER_WR ch=DEST` (write). Dirty is a **single flag per entry** (not a byte mask): the whole word is written with `write16`.

**DATA** — plain 16-bit words, no pixel logic. `PACKER_RD/WR ch=DATA` goes through `DPTR` (not `AddrPacker`); `fmt` from `ch_mode_[DATA]` (`PASS16`/`PASS_LO8`/`PASS_HI8`).

**RSV** — reserved, unused.

## 5. HIT/MISS

`BufferEntry`: `{tag, data, page, valid, dirty}`. **DIRTY — one flag** (no byte mask). Writes always use a full 16-bit `write16`.

On access:
1. Check `valid` and `tag == tag_of(addr)` and `page == page_of(addr)`.
2. HIT → return `data`, `hits++`, 1 cycle.
3. MISS → if dirty, `write16(page<<16 | tag, data)`, `writebacks++`, `MISS_CYCLES`; then `data = read16(addr)`, `valid=true`, `dirty=false`, `misses++`, `MISS_CYCLES`.

`MISS_CYCLES = 6` — a model constant, not RTL.

## 6. Memory access

`Memory16` is a wrapper over a `uint8_t*` (composition; `Memory16(base, size)`). `read16`/`write16` operate on 16-bit little-endian words. In `Machine`: `gpu_mem_(mem.data(), MEM_SIZE)` — does not own the buffer (`owns_=false`).

Wishbone is the shared interface. Four logical entries are not four parallel ports. One transaction at a time.

## 7. Implementation principles

- One buffer, not three caches. `PixelBuffer` is a single class with a `ch` enum (0..3).
- `AddrPacker` lives outside the buffer, inside `GPU`.
- `DATA` uses `DPTR` (no dedicated incrementer).
- `set_page` is per-channel (write back that channel's dirty entry, reset it).
- `flush` is global (write back all dirty entries, invalidate all).
- `MISS_CYCLES = 6` — model constant, not RTL.

## 8. What the model must demonstrate

Implemented:
- four entries (`BufferEntry e_[4]`);
- `TAG` / `VALID` / `DIRTY`;
- `HIT` / `MISS`;
- dirty DEST writeback before eviction;
- fill on MISS;
- `set_page` (channel writeback, reset);
- `flush` (all writebacks, invalidate);
- `buffer_error()` — the model surfaces the error (write to a foreign page without `set_page`);
- counters `hits`, `misses`, `writebacks`.

Tests: `test_fill`, `test_sprite`, `test_sprite8`, `test_loop`, `test_setpage`, `test_page_error`, `test_1bpp`, `test_pass`, `test_affine`, `test_comb_alu`, `test_mmio` — all passing.

**`test_page_error`** demonstrates the error (`buffer_error()`) instead of hiding it. That matters more than convenience: if the microcode forgets `set_page`, the GPU must not silently write to a foreign page.

**Note:** exact BRAM width, dirty structure (flag vs byte mask), FSM, and ready/wait interface are deferred to RTL. The model uses a single flag and writes the whole word.

**Removed in this revision:** `SETMASK`, pixel mask, bit-plane layers, `mask_` in the GPU. Partial updates and layer-like effects are done by microcode (per-pixel writes plus `COND`/`MASK`).
