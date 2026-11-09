import subprocess
from pathlib import Path
from common import load_yaml, OUT

def render_graphviz(spec_file, output_file):
    data = load_yaml(spec_file)
    
    dot = 'digraph G {\n'
    dot += '  rankdir=TB;\n'
    dot += '  node [shape=box, fontname="Helvetica", fontsize=14, style="filled", fillcolor="white", color="black"];\n'
    dot += '  edge [fontname="Helvetica", fontsize=12, color="black"];\n\n'
    
    for name, algo in data["algorithms"].items():
        dot += f'  subgraph cluster_{name} {{\n'
        dot += f'    label="{algo["title"]}"; fontsize=18; fontname="Helvetica-Bold";\n'
        
        # Узлы
        for n in algo["nodes"]:
            shape = "box"
            style = "filled,rounded"
            fill = "white"
            if n.get("type") == "start" or n.get("type") == "end":
                shape = "oval"
                fill = "#F2F2F2"
            elif n.get("type") == "decision":
                shape = "diamond"
                fill = "#E0E0E0"
            
            # Заменяем \n на \l для переноса строк в Graphviz
            label = n["text"].replace("\\n", "\\l")
            dot += f'    {n["id"]} [label="{label}\\l", shape={shape}, fillcolor="{fill}"];\n'
            
        # Связи
        for e in algo["edges"]:
            label = f' [label="{e.get("label", "")}"]' if "label" in e else ''
            dot += f'    {e["from"]} -> {e["to"]}{label};\n'
            
        dot += '  }\n'
    
    dot += '}\n'
    
    dot_file = OUT / f"{output_file}.dot"
    dot_file.write_text(dot, encoding="utf-8")
    
    svg_file = OUT / f"{output_file}.svg"
    try:
        subprocess.run(["dot", "-Tsvg", str(dot_file), "-o", str(svg_file)], check=True)
        print(f"Wrote {svg_file}")
    except FileNotFoundError:
        print("ERROR: Graphviz (dot) not found. Install it: sudo apt install graphviz")

if __name__ == "__main__":
    render_graphviz("algorithms.yaml", "algorithms")