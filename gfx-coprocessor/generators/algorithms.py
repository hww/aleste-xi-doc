from common import load_yaml, svg_start, write_svg, esc

W_NODE, H_NODE = 220, 70

def draw_node(n):
    x, y = n["x"], n["y"]
    ntype = n.get("type", "process")
    lines = n["text"].split("\n")
    
    if ntype in ("start", "end"):
        shape = f'<rect x="{x}" y="{y}" width="{W_NODE}" height="{H_NODE}" rx="{H_NODE/2}" fill="#2F7564" />'
    elif ntype == "decision":
        cx, cy = x + W_NODE/2, y + H_NODE/2
        pts = f"{cx},{y} {x+W_NODE},{cy} {cx},{y+H_NODE} {x},{cy}"
        shape = f'<polygon points="{pts}" fill="#A56B35" />'
    else:
        shape = f'<rect x="{x}" y="{y}" width="{W_NODE}" height="{H_NODE}" rx="8" fill="#355A78" />'
        
    texts = []
    start_y = y + H_NODE/2 - (len(lines)-1)*9
    for i, line in enumerate(lines):
        ty = start_y + i * 18
        texts.append(f'<text x="{x+W_NODE/2}" y="{ty}" text-anchor="middle" dominant-baseline="middle" style="font: 13px \'Inter\', \'Arial\', sans-serif; fill: #FFFFFF;">{esc(line)}</text>')
    
    return shape + "".join(texts)

def draw_edge(e, nodes):
    b1, b2 = nodes[e["from"]], nodes[e["to"]]
    x1, y1 = b1["x"] + W_NODE/2, b1["y"] + H_NODE/2
    x2, y2 = b2["x"] + W_NODE/2, b2["y"] + H_NODE/2
    
    side = e.get("side", "straight")
    label = e.get("label", "")
    svg = ""
    lx, ly = 0, 0

    if side == "straight":
        path = f"M{x1} {y1+H_NODE/2} L{x2} {y2-H_NODE/2}"
        svg += f'<path d="{path}" stroke="#8A9BA8" stroke-width="2" fill="none" />'
        svg += f'<polygon points="{x2-6},{y2-H_NODE/2-8} {x2+6},{y2-H_NODE/2-8} {x2},{y2-H_NODE/2}" fill="#8A9BA8" />'
        lx, ly = x1 + 10, (y1 + y2)/2
        
    elif side == "left":
        offset = 80
        px = b1["x"] - offset
        path = f"M{b1['x']} {y1} L{px} {y1} L{px} {y2} L{b2['x']} {y2}"
        svg += f'<path d="{path}" stroke="#8A9BA8" stroke-width="2" fill="none" />'
        svg += f'<polygon points="{b2["x"]-8},{y2-6} {b2["x"]-8},{y2+6} {b2["x"]},{y2}" fill="#8A9BA8" />'
        lx, ly = px - 20, (y1 + y2)/2
        
    elif side == "right":
        offset = 80
        px = b1["x"] + W_NODE + offset
        path = f"M{b1['x']+W_NODE} {y1} L{px} {y1} L{px} {y2-H_NODE/2-20} L{x2} {y2-H_NODE/2-20} L{x2} {y2-H_NODE/2}"
        svg += f'<path d="{path}" stroke="#8A9BA8" stroke-width="2" fill="none" />'
        svg += f'<polygon points="{x2-6},{y2-H_NODE/2-8} {x2+6},{y2-H_NODE/2-8} {x2},{y2-H_NODE/2}" fill="#8A9BA8" />'
        lx, ly = px + 10, y1

    if label:
        svg += f'<rect x="{lx-15}" y="{ly-12}" width="30" height="16" fill="#F4F6F8" opacity="0.9" rx="4"/>'
        svg += f'<text x="{lx}" y="{ly}" text-anchor="middle" style="font: 700 11px \'Inter\', \'Arial\', sans-serif; fill: #526574;">{esc(label)}</text>'
        
    return svg

def main():
    data = load_yaml("algorithms.yaml")
    for name, algo in data["algorithms"].items():
        max_y = max(n["y"] for n in algo["nodes"])
        W, H = 800, max_y + 150
        parts = [svg_start(W, H, algo["title"], "Микрокод: блок-схема")]

        node_map = {n["id"]: n for n in algo["nodes"]}
        for e in algo["edges"]:
            parts.append(draw_edge(e, node_map))
        for n in algo["nodes"]:
            parts.append(draw_node(n))

        write_svg(f"algo_{name}.svg", "".join(parts))

if __name__ == "__main__":
    main()