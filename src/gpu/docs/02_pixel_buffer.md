# LX-GPU: pixel buffer block architecture

Goal: validate the architectural idea and the main hardware constraints, not to build an exact RTL or cycle-accurate simulator.

## 1. Structure

A single shared buffer module with four logical entries:

| Number | Purpose |
|---|---|
| 0 | SRC — source pixels |
| 1 | DST — read-modify-write destination pixels |
| 2 | STM — plain 16-bit words (microcode stream) |
| 3 | RSV — reserved |

**Implementation:** `PixelBuffer` — one class, `BufferEntry e_[4]`:

```cpp
struct BufferEntry {
    uint16_t tag;      // word address within the page (addr24 >> 1)
    uint16_t data;     // 16-bit content
    uint8_t  page;     // high 8 bits of the address
    bool     valid;
    bool     dirty;    // for DST; always false for SRC/STM
};
```

Not "BRAM with 4 entries" — four C++ structs. BRAM width is not fixed (deferred to RTL). `page` (8 bits) is not part of TAG (16 bits): `page_of(addr24) = addr24 >> 16`, `tag_of(addr24) = (addr24 >> 1) & 0xFFFF`.

## 2. Pixel formats

The buffer works with 16-bit words. `fmt` lives in `PixelPacker`, not in the buffer.

[include](channel_mode-table.md)

1 bpp is a source format (masks, fonts); `AddrPacker` and `PixelPacker` support it as a destination too (16 pixels per word).

## 3. Addressing

Address arithmetic does not belong in the buffer. `AddrPacker` produces `addr24` + `pos` from `idx` (pixel index inside the page), `page` (8 bits) and `fmt`. The buffer receives a ready `addr24` (24 bits) and `pos` (0..15).

`addr24 = (page << 16) | ((idx >> shift) << 1)`. The `base` (low 16 bits) is optional: in FPGA only the high 8 bits are used; the simulator keeps all 24 bits.

The video controller addresses 64 KB pages. TAG is 16 bits (word address), `page` is 8 bits. A page change uses `set_page(ch, page)` (write back dirty, reset the channel).

## 4. Channel purposes

**SRC** — read source pixels. `SRC.PIX` reads, `SRC.W16` reads a word, `SRC.IDX` sets the pixel index, `SRC.STEP` sets the signed step.

**DST** — read + write. `DST.PIX` reads/writes with fmt packing; `DST.W16` reads/writes a word; dirty is a single flag per entry (not a byte mask): the whole word is written with `write16`.

**STM** — read-only. `STM.W16` reads a raw word, `STM.W24` reads two words into a 24-bit value, `STM.PIX` reads a pixel with fmt. `STM.PTR` is the stream pointer.

**RSV** — reserved, unused.

## 5. HIT/MISS

`BufferEntry`: `{tag, data, page, valid, dirty}`. **DIRTY — one flag** (no byte mask). Writes always use a full 16-bit `write16`.

On access:
1. Check `valid` and `tag == tag_of(addr)` and `page == page_of(addr)`.
2. HIT → return `data`, `hits++`.
3. MISS → if dirty, `write16(page<<16 | tag<<1, data)`, `writebacks++`; then `data = read16(addr)`, `valid=true`, `dirty=false`, `misses++`.

Under `#ifdef SIMULATE_CACHE`, a read/write to a valid entry with a different page sets `error_` (microcode forgot `set_page`).

`MISS_CYCLES = 6` — a model constant, not counted in execution time (mathematical model).

## 6. Memory access

`Memory16` is a wrapper over a `uint8_t*` (composition; `Memory16(base, size)`). `read16`/`write16` operate on 16-bit little-endian words. In `Machine`: `gpu_mem_(mem.data(), MEM_SIZE)` — does not own the buffer (`owns_=false`).

Wishbone is the shared interface. Four logical entries are not four parallel ports. One transaction at a time.

## 7. Implementation principles

- One buffer, not three caches. `PixelBuffer` is a single class with a `ch` enum (0..3).
- `AddrPacker` lives inside the port, not the buffer.
- `STM` is read-only.
- `set_page` is per-channel (write back that channel's dirty entry, reset it).
- `flush` is global (write back all dirty entries, invalidate all).
- `MISS_CYCLES` is a model constant, not RTL.

## 8. What the model must demonstrate

Implemented:
- four entries (`BufferEntry e_[4]`);
- `TAG` / `VALID` / `DIRTY`;
- `HIT` / `MISS`;
- dirty DST writeback before eviction;
- fill on MISS;
- `set_page` (channel writeback, reset);
- `flush` (all writebacks, invalidate);
- `buffer_error()` under `SIMULATE_CACHE` (write/read to a foreign page without `set_page`);
- counters `hits`, `misses`, `writebacks`.

Tests: `test_addr`, `test_fill`, `test_sprite`, `test_sprite8`, `test_loop`, `test_setpage`, `test_page_error`, `test_pass`, `test_1bpp`, `test_affine`, `test_flags`, `test_cond`, `test_mul`, `test_shadow`, `test_jmpr`, `test_mov_special`, `test_mmio` — all passing.

**`test_page_error`** demonstrates the error (`buffer_error()`) instead of hiding it. That matters more than convenience: if the microcode forgets `set_page`, the GPU must not silently write to a foreign page.

**Note:** exact BRAM width, dirty structure (flag vs byte mask), FSM, and ready/wait interface are deferred to RTL. The model uses a single flag and writes the whole word.

**Removed in this revision:** `SETMASK`, pixel mask, bit-plane layers, `mask_` in the GPU. Partial updates and layer-like effects are done by microcode (per-pixel writes plus `COND`).
