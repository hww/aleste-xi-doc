from common import load_yaml, svg_start, write_svg, esc

def main():
    data = load_yaml("alu.yaml")
    ops = data["operations"]

    codes = sorted(o["code"] for o in ops)
    if codes != list(range(len(ops))):
        raise ValueError(f"ALU codes must be unique and contiguous from 0; got {codes}")

    W = 1120
    row_h = 40
    top = 108
    height = top + len(ops) * row_h + 40

    parts = [svg_start(W, height, "ALU OPERATIONS", f'{len(ops)} opcodes · {data["width"]}-bit datapath')]

    parts.append(f'<text x="42" y="96" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">CODE</text>')
    parts.append(f'<text x="130" y="96" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">NAME</text>')
    parts.append(f'<text x="310" y="96" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">ACTION</text>')

    for i, o in enumerate(ops):
        y = top + i * row_h
        bg = "#FFFFFF" if i % 2 == 0 else "#EAF0F3"
        accent = "#8061A1" if o["name"] == "COMB" else "#365E91"
        parts.append(f'<rect x="32" y="{y}" width="1056" height="34" rx="6" fill="{bg}"/>')
        parts.append(f'<rect x="32" y="{y}" width="6" height="34" rx="3" fill="{accent}"/>')
        parts.append(f'<text x="58" y="{y+22}" style="font: 13px \'Menlo\', \'Consolas\', monospace; fill: #203342;">{o["code"]:02d}</text>')
        parts.append(f'<text x="130" y="{y+22}" style="font: 700 13px \'Inter\', \'Arial\', sans-serif; fill: #203342;">{esc(o["name"])}</text>')
        parts.append(f'<text x="310" y="{y+22}" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">{esc(o["description"])}</text>')

    write_svg("alu_map.svg", "".join(parts))

if __name__ == "__main__":
    main()