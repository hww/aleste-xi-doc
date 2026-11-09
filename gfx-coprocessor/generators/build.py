import sys
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import yaml
from common import (
    OUT, SPEC, SRC, DOC, write_svg, write_md, svg_start, esc,
    COLOR_GRID, COLOR_TEXT, COLOR_FILL_LIGHT, COLOR_FILL_MED,
)


# ---------- bitfield ----------
def render_bitfield_svg(data, filename):
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
    write_svg(filename, "".join(parts))


def render_bitfield_md(data, filename):
    md = f"**{data.get('title', data['name'])}**\n\n"
    md += "| Поле | Биты | Ширина | Описание |\n| --- | --- | --- | --- |\n"
    for f in sorted(data["fields"], key=lambda x: -int(x["msb"])):
        n = int(f["msb"]) - int(f["lsb"]) + 1
        md += f'| **{f["name"]}** | [{f["msb"]}:{f["lsb"]}] | {n} | {f["description"]} |\n'
    write_md(filename, md)


# ---------- table ----------
def render_table_md(data, filename):
    md = f"### {data.get('title', data['name'])}\n\n"
    cols = list(data["columns"])

    autoindex = data.get("autoindex")
    if autoindex is not None:
        # autoindex — это форматная строка, например "R{}" или "0x{:02X}"
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

    write_md(filename, md)


# ---------- timing ----------
def render_timing_svg(data, filename):
    W = data.get("width", 800)
    signals = data["signals"]
    num_ticks = next((len(s["states"]) for s in signals if "states" in s), 0)
    if num_ticks == 0:
        raise ValueError("No 'states' in any signal")

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

    write_svg(filename, "".join(parts))


# ---------- preprocessor ----------
def process_file(filepath):
    text = filepath.read_text(encoding="utf-8")
    pattern = r'\[(?:include|insert)\]\(([^)]+)\)'

    def replacer(match):
        include_filename = match.group(1)
        # Сначала ищем в output/, потом в src/
        path = OUT / include_filename
        if not path.exists():
            path = SRC / include_filename
        if not path.exists():
            print(f"  ⚠️  Not found: {include_filename}")
            return f"*[Missing: {include_filename}]*"
        return process_file(path)

    return re.sub(pattern, replacer, text)


def assemble_documents():
    DOC.mkdir(exist_ok=True)
    for src_file in sorted(SRC.glob("*.md")):
        if src_file.name.endswith("-table.md"):
            continue
        print(f"Assembling {src_file.name}...")
        result = process_file(src_file)
        (DOC / src_file.name).write_text(result, encoding="utf-8")
        print(f"  -> {DOC / src_file.name}")


# ---------- главный обход ----------
def main():
    for yml in sorted(SPEC.glob("*.yaml")):
        try:
            data = yaml.safe_load(yml.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Skip {yml.name}: YAML error: {e}")
            continue

        if not isinstance(data, dict) or "kind" not in data:
            print(f"Skip {yml.name}: no 'kind' field")
            continue

        kind = data["kind"]
        name = data.get("name", yml.stem)

        if kind == "bitfield":
            render_bitfield_svg(data, f"{name}.svg")
            render_bitfield_md(data, f"{name}-table.md")
        elif kind == "table":
            render_table_md(data, f"{name}-table.md")
        elif kind == "timing":
            render_timing_svg(data, f"{name}.svg")
        else:
            print(f"Skip {yml.name}: unknown kind={kind}")

    print("\n--- Assembling documents ---")
    assemble_documents()


if __name__ == "__main__":
    main()