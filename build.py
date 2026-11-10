#!/usr/bin/env python3
import re
import shutil
import subprocess
import sys
import filecmp
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "out"

import html
import yaml

COLOR_BG = "#FFFFFF"
COLOR_TEXT = "#000000"
COLOR_GRID = "#000000"
COLOR_FILL_LIGHT = "#F2F2F2"
COLOR_FILL_MED = "#E0E0E0"

def esc(value):
    return html.escape(str(value), quote=True)

def svg_start(width, height, title, subtitle=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="background: {COLOR_BG}; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
<text x="32" y="45" style="font: 700 24px sans-serif; fill: {COLOR_TEXT};">{esc(title)}</text>
<text x="32" y="75" style="font: 16px sans-serif; fill: #555555;">{esc(subtitle)}</text>
'''

def svg_end():
    return "</svg>"

def write_text(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def write_svg(path, content):
    write_text(path, content + svg_end())

def load_yaml(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))

def smart_copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and filecmp.cmp(src, dst, shallow=False):
        return
    shutil.copy2(src, dst)

# ---------- рендереры ----------
def render_bitfield_md(data, name, gen_dir):
    md = f"**{data.get('title', data['name'])}**\n\n"
    md += "| Поле | Биты | Ширина | Описание |\n| --- | --- | --- | --- |\n"
    for f in sorted(data["fields"], key=lambda x: -int(x["msb"])):
        n = int(f["msb"]) - int(f["lsb"]) + 1
        md += f'| **{f["name"]}** | [{f["msb"]}:{f["lsb"]}] | {n} | {f["description"]} |\n'
    write_text(gen_dir / f"{name}-table.md", md)

def render_table_md(data, name, gen_dir):
    md = f"### {data.get('title', data['name'])}\n\n"
    cols = list(data["columns"])
    autoindex = data.get("autoindex")
    if autoindex is not None:
        cols = [{"key": "__autoindex__", "label": data.get("autoindex_label", "#")}] + cols
    md += "| " + " | ".join(c["label"] for c in cols) + " |\n"
    md += "| " + " | ".join("---" for _ in cols) + " |\n"
    for i, row in enumerate(data["rows"]):
        cells = []
        for c in cols:
            if c["key"] == "__autoindex__":
                v = autoindex.format(i)
            else:
                v = row.get(c["key"], "")
                if c.get("bold"):
                    v = f"**{v}**"
            cells.append(str(v))
        md += "| " + " | ".join(cells) + " |\n"
    write_text(gen_dir / f"{name}-table.md", md)

def render_bitfield_svg(data, name, gen_dir):
    width_bits = int(data["width"])
    fields = data["fields"]
    W, left, top, row_h = 1200, 32, 120, 50
    col_w = (W - left * 2) / width_bits
    H = top + row_h + 50
    parts = [svg_start(W, H, data["title"], f"{width_bits}-bit register map")]
    for i in range(width_bits):
        bit_num = width_bits - 1 - i
        x = left + i * col_w
        parts.append(f'<text x="{x+col_w/2}" y="{top-10}" text-anchor="middle" style="font: 12px monospace; fill:#666;">{bit_num}</text>')
        if i > 0:
            parts.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top+row_h}" stroke="{COLOR_GRID}" stroke-dasharray="2,2"/>')
    ordered = sorted(fields, key=lambda f: int(f["msb"]), reverse=True)
    for idx, f in enumerate(ordered):
        msb, lsb = int(f["msb"]), int(f["lsb"])
        nbits = msb - lsb + 1
        x = left + (width_bits - 1 - msb) * col_w
        w = nbits * col_w
        fill = COLOR_FILL_LIGHT if idx % 2 == 0 else COLOR_FILL_MED
        parts.append(f'<rect x="{x}" y="{top}" width="{w}" height="{row_h}" fill="{fill}" stroke="{COLOR_GRID}" stroke-width="2"/>')
        parts.append(f'<text x="{x+w/2}" y="{top+row_h/2+6}" text-anchor="middle" style="font: 700 16px sans-serif;">{esc(f["name"])}</text>')
    write_svg(gen_dir / f"{name}.svg", "".join(parts))

def render_timing_svg(data, name, gen_dir):
    W = data.get("width", 800)
    signals = data["signals"]
    num_ticks = next((len(s["states"]) for s in signals if "states" in s), 0)
    left, top, row_h = 150, 120, 40
    col_w = (W - left - 32) / num_ticks
    H = top + len(signals) * row_h + 40
    parts = [svg_start(W, H, data["title"], data.get("subtitle", ""))]
    for i in range(num_ticks + 1):
        x = left + i * col_w
        parts.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top+len(signals)*row_h}" stroke="#CCCCCC" stroke-width="1"/>')
        if i < num_ticks:
            parts.append(f'<text x="{x+col_w/2}" y="{top-15}" text-anchor="middle" style="font: 12px monospace; fill:#666;">T{i+1}</text>')
    for idx, sig in enumerate(signals):
        y_top = top + idx * row_h
        y_bot = y_top + row_h
        y_mid = y_top + row_h / 2
        parts.append(f'<text x="{left-10}" y="{y_mid+5}" text-anchor="end" style="font: 700 14px monospace;">{esc(sig["name"])}</text>')
        if sig.get("type") == "clock":
            path = f"M{left} {y_bot} "
            for i in range(num_ticks):
                x1 = left + i * col_w
                x2 = x1 + col_w
                path += f"L{x1} {y_bot} L{x1} {y_top} L{x2} {y_top} L{x2} {y_bot} "
            parts.append(f'<path d="{path}" fill="none" stroke="{COLOR_GRID}" stroke-width="2"/>')
        elif "states" in sig:
            states = sig["states"]
            for i, state in enumerate(states):
                x = left + i * col_w
                if state not in ("0", "1"):
                    parts.append(f'<rect x="{x}" y="{y_top+5}" width="{col_w}" height="{row_h-10}" fill="{COLOR_FILL_LIGHT}" stroke="{COLOR_GRID}" stroke-width="1"/>')
                    parts.append(f'<text x="{x+col_w/2}" y="{y_mid+5}" text-anchor="middle" style="font: 13px monospace;">{esc(state)}</text>')
                else:
                    y_val = y_top + 5 if state == "1" else y_bot - 5
                    parts.append(f'<line x1="{x}" y1="{y_val}" x2="{x+col_w}" y2="{y_val}" stroke="{COLOR_GRID}" stroke-width="2"/>')
                    if i > 0 and states[i-1] != state and states[i-1] in ("0", "1"):
                        y_prev = y_top + 5 if states[i-1] == "1" else y_bot - 5
                        parts.append(f'<line x1="{x}" y1="{y_prev}" x2="{x}" y2="{y_val}" stroke="{COLOR_GRID}" stroke-width="2"/>')
    write_svg(gen_dir / f"{name}.svg", "".join(parts))

# ---------- препроцессор [include](...) ----------
INCLUDE_RE = re.compile(r'\[(?:include|insert)\]\(([^)]+)\)')

def process_file(filepath, gen_dir, src_dir, seen=None):
    if seen is None:
        seen = set()
    filepath = Path(filepath).resolve()
    if filepath in seen:
        return f"*[Cycle: {filepath.name}]*"
    seen.add(filepath)

    text = filepath.read_text(encoding="utf-8")

    def replacer(match):
        rel = match.group(1)
        
        # Очищаем путь от "./" в начале
        if rel.startswith("./"):
            rel = rel[2:]
            
        p = gen_dir / rel
        if not p.exists():
            p = src_dir / rel
            
        if not p.exists():
            print(f"    ⚠️  not found: {rel} (in {filepath.name})")
            return f"*[Missing: {rel}]*"
        return process_file(p, gen_dir, src_dir, seen)

    return INCLUDE_RE.sub(replacer, text)

# ---------- сборка одного проекта ----------
def build_project(project_dir):
    name = project_dir.name
    src_dir = project_dir
    docs_dir = src_dir / "docs"
    spec_dir = src_dir / "spec"
    
    # ГЛАВНОЕ ИЗМЕНЕНИЕ: gen внутри docs
    gen_dir = docs_dir / "gen"  
    doc_images_dir = docs_dir / "images"
    
    out_dir = OUT / name
    out_images_dir = out_dir / "images"

    print(f"\n=== {name} ===")
    gen_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_images_dir.mkdir(parents=True, exist_ok=True)

    # 1) spec/*.yaml -> docs/gen/*.svg, docs/gen/*-table.md
    if spec_dir.exists():
        for yml in sorted(spec_dir.glob("*.yaml")):
            print(f"  spec: {yml.name}")
            data = load_yaml(yml)
            if not isinstance(data, dict) or "kind" not in data:
                continue
            kind = data["kind"]
            yname = data.get("name", yml.stem)
            
            if kind == "bitfield":
                render_bitfield_svg(data, yname, gen_dir)
                render_bitfield_md(data, yname, gen_dir)
            elif kind == "table":
                render_table_md(data, yname, gen_dir)
            elif kind == "timing":
                render_timing_svg(data, yname, gen_dir)

    # 2) src/<P>/docs/*.md -> out/<P>/*.md
    if docs_dir.exists():
        for md in sorted(docs_dir.rglob("*.md")):
            if "gen" in md.parts:  # Игнорируем сгенерированные .md таблицы при обходе
                continue
            rel = md.relative_to(docs_dir)
            print(f"  doc:  {rel}")
            text = process_file(md, gen_dir, src_dir)
            
            # Подменяем пути для финального сайта: gen/ -> images/
            text = text.replace("](gen/", "](images/")
            
            write_text(out_dir / rel, text)

    # 3) Ручные картинки из docs/images/ -> out/images/
    if doc_images_dir.exists():
        for f in doc_images_dir.rglob("*"):
            if f.is_file():
                rel = f.relative_to(doc_images_dir)
                smart_copy(f, out_images_dir / rel)

    # 4) Сгенерированные картинки из docs/gen/ -> out/images/
    for img_file in gen_dir.glob("*"):
        if img_file.suffix in (".svg", ".png", ".webp"):
            smart_copy(img_file, out_images_dir / img_file.name)

    # 5) check.py
    check = src_dir / "check.py"
    if check.exists():
        print(f"  running {check.name}...")
        subprocess.run([sys.executable, str(check)], cwd=src_dir, check=False)

# ---------- main ----------
def main():
    if not SRC.exists():
        print("No src/ directory")
        return
    for project_dir in sorted(SRC.iterdir()):
        if not project_dir.is_dir():
            continue
        build_project(project_dir)
    print("\nDone.")

if __name__ == "__main__":
    main()