from common import load_yaml, svg_start, write_svg, esc

def main():
    data = load_yaml("operand_map.yaml")
    entries = data["entries"]

    W = 1160
    row_h = 44
    top = 108
    height = top + len(entries) * row_h + 40

    parts = [svg_start(W, height, "MICROCODE OPERAND ADDRESS MAP", f'{data["width"]}-bit operand field · {len(entries)} windows')]

    parts.append(f'<text x="42" y="96" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">ADDR</text>')
    parts.append(f'<text x="140" y="96" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">NAME</text>')
    parts.append(f'<text x="330" y="96" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">READ</text>')
    parts.append(f'<text x="740" y="96" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">WRITE</text>')

    for i, e in enumerate(entries):
        y = top + i * row_h
        bg = "#FFFFFF" if i % 2 == 0 else "#EAF0F3"
        parts.append(f'<rect x="32" y="{y}" width="1096" height="38" rx="6" fill="{bg}"/>')
        parts.append(f'<rect x="32" y="{y}" width="6" height="38" rx="3" fill="#426F9D"/>')

        addr = str(e["address"])
        is_register_range = "-" in addr
        weight = "font-weight: 700;" if is_register_range else ""
        parts.append(f'<text x="58" y="{y+24}" style="font: 13px \'Menlo\', \'Consolas\', monospace; fill: #203342; {weight}">{esc(addr)}</text>')
        parts.append(f'<text x="140" y="{y+24}" style="font: 700 13px \'Inter\', \'Arial\', sans-serif; fill: #203342;">{esc(e["name"])}</text>')
        parts.append(f'<text x="330" y="{y+24}" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">{esc(e["read"])}</text>')
        parts.append(f'<text x="740" y="{y+24}" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">{esc(e["write"])}</text>')

    write_svg("operand_map.svg", "".join(parts))

if __name__ == "__main__":
    main()