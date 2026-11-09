import sys
from common import load_yaml, svg_start, write_svg, esc, COLOR_GRID, COLOR_TEXT, COLOR_FILL_LIGHT, COLOR_FILL_MED

def render(spec_file, output_file, title):
    data = load_yaml(spec_file)
    width_bits = int(data["width"])
    fields = data["fields"]

    occupied = {}
    for f in fields:
        msb, lsb = int(f["msb"]), int(f["lsb"])
        for bit in range(lsb, msb + 1):
            if bit in occupied: raise ValueError(f"Overlap bit {bit}")
            occupied[bit] = f["name"]
    if sorted(set(range(width_bits)) - set(occupied)):
        raise ValueError("Missing bits")

    W = 1200
    left = 32
    top = 120
    col_w = (W - left * 2) / width_bits
    row_h = 50
    H = top + row_h + 50

    parts = [svg_start(W, H, title, f"{width_bits}-bit register map")]

    for i in range(width_bits):
        bit_num = width_bits - 1 - i
        x = left + i * col_w
        parts.append(f'<text x="{x + col_w/2}" y="{top - 10}" text-anchor="middle" style="font: 12px monospace; fill: #666;">{bit_num}</text>')
        if i > 0:
            parts.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top + row_h}" stroke="{COLOR_GRID}" stroke-width="1" stroke-dasharray="2,2"/>')

    ordered = sorted(fields, key=lambda f: int(f["msb"]), reverse=True)
    for idx, f in enumerate(ordered):
        msb, lsb = int(f["msb"]), int(f["lsb"])
        nbits = msb - lsb + 1
        start_col = width_bits - 1 - msb
        x = left + start_col * col_w
        w = nbits * col_w
        fill = COLOR_FILL_LIGHT if idx % 2 == 0 else COLOR_FILL_MED
        parts.append(f'<rect x="{x}" y="{top}" width="{w}" height="{row_h}" fill="{fill}" stroke="{COLOR_GRID}" stroke-width="2"/>')
        parts.append(f'<text x="{x + w/2}" y="{top + row_h/2 + 6}" text-anchor="middle" style="font: 700 16px sans-serif; fill: {COLOR_TEXT};">{esc(f["name"])}</text>')

    write_svg(output_file, "".join(parts))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "mode":
        render("mode.yaml", "mode_register.svg", "MODE REGISTER · 24 BIT")
    else:
        render("microinstruction.yaml", "microinstruction.svg", "MICROINSTRUCTION · 36 BIT")