import sys
from common import load_yaml, FIELD_COLORS, svg_start, write_svg, esc

def render(spec_file, output_file, title):
    data = load_yaml(spec_file)
    width_bits = int(data["width"])
    fields = data["fields"]

    # Validate bit ranges: valid, non-overlapping, full coverage.
    occupied = {}
    for f in fields:
        msb, lsb = int(f["msb"]), int(f["lsb"])
        if msb < lsb or msb >= width_bits or lsb < 0:
            raise ValueError(f'Invalid bit range in {f["name"]}: [{msb}:{lsb}] for width {width_bits}')
        for bit in range(lsb, msb + 1):
            if bit in occupied:
                raise ValueError(f'Overlap at bit {bit}: {occupied[bit]} and {f["name"]}')
            occupied[bit] = f["name"]
    missing = sorted(set(range(width_bits)) - set(occupied))
    if missing:
        raise ValueError(f"Unspecified bits: {missing}")

    W = 1160
    left = 32
    top = 112
    bar_w = 1096
    bar_h = 74
    total_units = width_bits

    # Динамический расчет высоты: 218 (начало таблицы) + строки + отступ
    H = 218 + (len(fields) * 34) + 40

    parts = [svg_start(
        W, H, title,
        f'{width_bits}-bit field layout · MSB on left · LSB on right',
    )]

    ordered = sorted(fields, key=lambda f: int(f["msb"]), reverse=True)

    x = left
    for idx, f in enumerate(ordered):
        nbits = int(f["msb"]) - int(f["lsb"]) + 1
        w = bar_w * nbits / total_units
        color = FIELD_COLORS[idx % len(FIELD_COLORS)]
        parts.append(
            f'<rect x="{x:.2f}" y="{top}" width="{w:.2f}" height="{bar_h}" '
            f'rx="4" fill="{color}" stroke="#F4F6F8" stroke-width="2"/>'
        )
        if w >= 44:
            # Название поля
            parts.append(
                f'<text x="{x+w/2:.2f}" y="{top+31}" text-anchor="middle" '
                f'style="font: 700 14px \'Inter\', \'Arial\', sans-serif; fill: #FFFFFF;">{esc(f["name"])}</text>'
            )
            # Количество бит
            parts.append(
                f'<text x="{x+w/2:.2f}" y="{top+52}" text-anchor="middle" '
                f'style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #FFFFFF;">{nbits} bit</text>'
            )
        x += w

    # Bit ruler
    parts.append(f'<text x="{left}" y="{top-12}" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">BIT {width_bits-1}</text>')
    parts.append(f'<text x="{left+bar_w}" y="{top-12}" text-anchor="end" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">BIT 0</text>')

    # Detail list
    y = 218
    for idx, f in enumerate(ordered):
        msb, lsb = int(f["msb"]), int(f["lsb"])
        nbits = msb - lsb + 1
        color = FIELD_COLORS[idx % len(FIELD_COLORS)]
        parts.append(f'<rect x="32" y="{y}" width="1096" height="30" rx="4" fill="#FFFFFF"/>')
        parts.append(f'<rect x="32" y="{y}" width="6" height="30" rx="3" fill="{color}"/>')
        parts.append(f'<text x="52" y="{y+20}" style="font: 700 13px \'Inter\', \'Arial\', sans-serif; fill: #203342;">{esc(f["name"])}</text>')
        parts.append(f'<text x="190" y="{y+20}" style="font: 13px \'Menlo\', \'Consolas\', monospace; fill: #203342;">[{msb}:{lsb}] · {nbits} bit</text>')
        parts.append(f'<text x="390" y="{y+20}" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">{esc(f["description"])}</text>')
        y += 34

    write_svg(output_file, "".join(parts))

TARGETS = {
    "microinstruction": ("microinstruction.yaml", "microinstruction.svg", "MICROINSTRUCTION · 36 BIT"),
    "mode":             ("mode.yaml",             "mode_register.svg",    "MODE REGISTER · 24 BIT"),
}

def main(argv):
    key = argv[1] if len(argv) > 1 else "microinstruction"
    if key not in TARGETS:
        raise SystemExit(f"Choose one of: {', '.join(TARGETS)}")
    render(*TARGETS[key])

if __name__ == "__main__":
    main(sys.argv)