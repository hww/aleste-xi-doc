# GFX Coprocessor visual documentation

Generated SVGs live in `../output/`. Reference them from Markdown:

```markdown
![Register file](../output/register_map.svg)
![Microinstruction format](../output/microinstruction.svg)
![MODE register](../output/mode_register.svg)
![Operand map](../output/operand_map.svg)
![ALU operations](../output/alu_map.svg)
```

The architecture block diagram and datapath sheet should be drawn by hand in
draw.io, not generated. Save as `architecture.drawio` and export to SVG for the
docs.

Keep `spec/*.yaml` as the source of truth. Regenerate after every change:

```bash
python generators/generate_all.py
```