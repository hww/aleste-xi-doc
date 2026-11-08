from common import load_yaml, PALETTE, svg_start, write_svg, esc

def main():
    data = load_yaml("registers.yaml")
    regs = data["registers"]

    assert len(regs) == data["count"], f'Declared count {data["count"]} != listed {len(regs)}'
    assert sorted(r["index"] for r in regs) == list(range(data["count"])), "Register indices must be unique and contiguous"

    W = 1120
    row_h = 42
    top = 100
    height = top + len(regs) * row_h + 45

    parts = [svg_start(W, height, "REGISTER FILE · R0–R31", f'{data["count"]} × {data["width"]}-bit · {data["read_ports"]} read ports')]

    parts.append(f'<text x="42" y="88" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">INDEX</text>')
    parts.append(f'<text x="130" y="88" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">REGISTER</text>')
    parts.append(f'<text x="330" y="88" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">FUNCTION</text>')
    parts.append(f'<text x="1050" y="88" text-anchor="end" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">GROUP</text>')

    for i, r in enumerate(regs):
        y = top + i * row_h
        color = PALETTE.get(r["group"], PALETTE["default"])
        bg = "#FFFFFF" if i % 2 == 0 else "#EAF0F3"
        parts.append(f'<rect x="32" y="{y}" width="1056" height="36" rx="6" fill="{bg}"/>')
        parts.append(f'<rect x="32" y="{y}" width="7" height="36" rx="3" fill="{color}"/>')
        parts.append(f'<text x="58" y="{y+23}" style="font: 13px \'Inter\', \'Arial\', sans-serif; fill: #203342;">{r["index"]:02d}</text>')
        parts.append(f'<text x="130" y="{y+23}" style="font: 700 13px \'Inter\', \'Arial\', sans-serif; fill: #203342;">{esc(r["name"])}</text>')
        parts.append(f'<text x="330" y="{y+23}" style="font: 13px \'Inter\', \'Arial\', sans-serif; fill: #203342;">{esc(r["description"])}</text>')
        parts.append(f'<text x="1055" y="{y+23}" text-anchor="end" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">{esc(r["group"].upper())}</text>')

    write_svg("register_map.svg", "".join(parts))

if __name__ == "__main__":
    main()