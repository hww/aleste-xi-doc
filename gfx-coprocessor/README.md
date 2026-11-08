# GFX Coprocessor — Visual Specification

Structured YAML definitions + Python generators for the microcore architecture
documentation. Generates clean, editable SVG diagrams from data, not from prose.

## Quick start

```bash
python -m pip install -r requirements.txt
python generators/generate_all.py
```

Output appears in `output/`:

| File | Content |
| --- | --- |
| `register_map.svg` | R0–R31 register file map |
| `microinstruction.svg` | 36-bit microinstruction layout |
| `mode_register.svg` | 24-bit MODE register |
| `operand_map.svg` | Microcode operand address map (0–46) |
| `alu_map.svg` | ALU opcode table |

## Individual generators

```bash
python generators/register_map.py
python generators/bitfields.py microinstruction
python generators/bitfields.py mode
python generators/operand_map.py
python generators/alu_map.py
```

## Design rules

- YAML in `spec/` is the source of truth. Never edit generated SVG by hand.
- Generators validate their input: contiguous register indices, non-overlapping
  bit fields, full bit coverage, unique opcodes.
- Fixed geometry, not auto-layout. Predictable output every run.
- SVG only. No raster.

## Engineering assumptions to verify against RTL

1. `registers.yaml`: T0–T6 descriptions are inferred from the microcode examples
   in the architecture doc. T7–T10 are generic. Verify against actual microcode.
2. `mode.yaml`: bits 7–23 are marked reserved. Confirm whether MODE is really
   24 writable bits or a narrower hardware register.
3. `microinstruction.yaml`: `SB = 45` (IMM) selects the 9-bit immediate carried
   in the `X` field. Confirm this encoding.
4. `commands.yaml`: only opcode dispatch is recorded. Per-command payload
   layouts and lengths are not yet specified.
5. `architecture.yaml`: 256-byte FIFO is a concrete choice from the stated
   64–256 byte range.

## Next additions

- WaveDrom timing diagram (fetch / stall / pixel).
- Manual `architecture.drawio` after bus directions are finalized.
- Per-command payload schemas in `commands.yaml`.

## Usage

```bash
cd ~/gfx-coprocessor
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python generators/generate_all.py
```
