from common import load_yaml, svg_start, write_svg, esc

def draw_icon(name, x, y, color="#FFFFFF"):
    if name == "cpu":
        return f'''<g stroke="{color}" stroke-width="1.5" fill="none" transform="translate({x-10},{y-10})">
        <rect x="4" y="4" width="12" height="12" rx="2"/><rect x="7" y="7" width="6" height="6" rx="1"/>
        <path d="M9 1v3m2-3v3m-2 12v3m2-3v3M1 9h3m-3 2h3m12-2h3m-3 2h3"/></g>'''
    elif name == "layers":
        return f'''<g stroke="{color}" stroke-width="1.5" fill="none" transform="translate({x-10},{y-10})">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 12l10 5 10-5M2 17l10 5 10-5"/></g>'''
    return ""

def main():
    data = load_yaml("architecture_layout.yaml")
    w_canvas = data["canvas"]["width"]
    h_canvas = data["canvas"]["height"]

    parts = [svg_start(w_canvas, h_canvas, "GFX Coprocessor — Architecture", "BLOCK DIAGRAM · REV 1.0")]
    b_map = {b["id"]: b for b in data["blocks"]}

    for c in data.get("connectors", []):
        b1 = b_map[c["from"]]
        b2 = b_map[c["to"]]
        if "w" not in b1 or "h" not in b1 or "w" not in b2 or "h" not in b2: continue
            
        x1, y1 = b1["x"] + b1["w"]/2, b1["y"] + b1["h"]
        x2, y2 = b2["x"] + b2["w"]/2, b2["y"]
        
        if c.get("type") == "vertical":
            parts.append(f'<path d="M{x1} {y1} L{x1} {y2-6}" stroke="#8A9BA8" stroke-width="2" fill="none"/>')
            parts.append(f'<polygon points="{x1-4},{y2-8} {x1+4},{y2-8} {x1},{y2}" fill="#8A9BA8"/>')
        elif c.get("type") == "horizontal":
            mid_y = b1["y"] + b1["h"]/2
            parts.append(f'<path d="M{x1+6} {mid_y} L{x2-6} {mid_y}" stroke="#8A9BA8" stroke-width="2" fill="none"/>')
            parts.append(f'<polygon points="{x2-8},{mid_y-4} {x2-8},{mid_y+4} {x2},{mid_y}" fill="#8A9BA8"/>')

    for b in data["blocks"]:
        x = b.get("x", 0)
        y = b.get("y", 0)
        
        if "align" in b:
            if b["align"] == "center":
                parts.append(f'<text x="{w_canvas/2}" y="{y}" text-anchor="middle" style="font: 700 14px \'Inter\', \'Arial\', sans-serif; fill: #FFFFFF;">{esc(b["title"])}</text>')
            else:
                parts.append(f'<text x="{x}" y="{y}" style="font: 700 14px \'Inter\', \'Arial\', sans-serif; fill: #FFFFFF;">{esc(b["title"])}</text>')
            continue

        if "w" in b and "h" in b:
            w, h = b["w"], b["h"]
            color = b.get("color", "#536779")
            
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{color}"/>')
            
            if "title" in b:
                if "subtitle" in b:
                    parts.append(f'<text x="{x+w/2}" y="{y+h/2-2}" text-anchor="middle" style="font: 700 14px \'Inter\', \'Arial\', sans-serif; fill: #FFFFFF;">{esc(b["title"])}</text>')
                    parts.append(f'<text x="{x+w/2}" y="{y+h/2+16}" text-anchor="middle" style="font: 13px \'Inter\', \'Arial\', sans-serif; fill: #D7E7F5;">{esc(b["subtitle"])}</text>')
                else:
                    parts.append(f'<text x="{x+w/2}" y="{y+h/2+6}" text-anchor="middle" style="font: 700 14px \'Inter\', \'Arial\', sans-serif; fill: #FFFFFF;">{esc(b["title"])}</text>')

            if "icon" in b:
                parts.append(draw_icon(b["icon"], x+w/2, y+32))

    parts.append('<rect x="1020" y="48" width="36" height="20" rx="10" fill="#D1FAE5"/>')
    parts.append(f'<text x="1038" y="62" text-anchor="middle" style="font: 700 11px \'Inter\', \'Arial\', sans-serif; fill: #065F46;">FPGA</text>')

    footer = data.get("footer", "")
    parts.append(f'<text x="32" y="{h_canvas-12}" style="font: 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">{esc(footer)}</text>')

    write_svg("architecture.svg", "".join(parts))

if __name__ == "__main__":
    main()