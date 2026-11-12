#!/usr/bin/env python3
import re
import shutil
import subprocess
import sys
import filecmp
from pathlib import Path
import html
import yaml

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "out"

def esc(value):
    return html.escape(str(value), quote=True)

def write_text(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def write_svg(path, content):
    svg_str = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{content['W']}" height="{content['H']}" viewBox="0 0 {content['W']} {content['H']}" style="background: #FFFFFF; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
<text x="32" y="45" style="font: 700 24px sans-serif; fill: #000000;">{esc(content['title'])}</text>
<text x="32" y="75" style="font: 16px sans-serif; fill: #555555;">{esc(content['subtitle'])}</text>
{"".join(content['parts'])}
</svg>'''
    write_text(path, svg_str)

def smart_copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and filecmp.cmp(src, dst, shallow=False):
        return
    shutil.copy2(src, dst)

# ---------- Цвета ----------
COLOR_GRID = "#000000"
COLOR_FILL_LIGHT = "#F2F2F2"
COLOR_FILL_MED = "#E0E0E0"
COLOR_FILL_WARN = "#FFF3CD"
COLOR_BORDER_WARN = "#FFC107"

# ---------- Рендерер SVG для timing ----------

def render_timing_svg(data, REGISTRY):
    W = data.get("width", 800)
    signals = data.get("signals", [])
    num_ticks = next((len(s["states"]) for s in signals if "states" in s), 0)
    if num_ticks == 0:
        return None

    left, top, row_h = 150, 120, 40
    col_w = (W - left - 32) / num_ticks
    H = top + len(signals) * row_h + 40

    parts = []
    for i in range(num_ticks + 1):
        x = left + i * col_w
        parts.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top+len(signals)*row_h}" stroke="#CCCCCC" stroke-width="1"/>')
        if i < num_ticks:
            parts.append(f'<text x="{x+col_w/2}" y="{top-15}" text-anchor="middle" style="font: 12px monospace; fill:#666;">T{i+1}</text>')

    for idx, sig in enumerate(signals):
        y_top = top + idx * row_h
        y_bot = y_top + row_h
        y_mid = y_top + row_h / 2
        parts.append(f'<text x="{left-10}" y="{y_mid+5}" text-anchor="end" style="font: 700 14px monospace;">{esc(sig.get("name", ""))}</text>')

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

    return {"W": W, "H": H, "title": data.get("title", "Timing"), "subtitle": data.get("subtitle", ""), "parts": parts}

# ---------- Рендерер SVG для bitfield ----------
def render_bitfield_svg(bf, REGISTRY):
    name = bf.get("name", "unknown")
    title = bf.get("title", name)
    width_bits = int(bf.get("width", 8))
    fields = bf.get("fields", [])
    
    if not fields and "ref" in bf:
        ref = REGISTRY.get(bf["ref"])
        if ref:
            fields = ref.get("fields", [])
            width_bits = int(ref.get("width", 8))
    
    if not fields:
        return None

    W, left, top, row_h = 1200, 32, 120, 50
    col_w = (W - left * 2) / width_bits
    H = top + row_h + 50
    tick_h = row_h * 0.15
    parts = []
    
    # 1. Номера битов и пунктирные линии
    for i in range(width_bits + 1):
        x = left + i * col_w
        if i < width_bits:
            bit_num = width_bits - 1 - i
            parts.append(f'<text x="{x+col_w/2}" y="{top-10}" text-anchor="middle" style="font: 12px monospace; fill:#666;">{bit_num}</text>')
        parts.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top+row_h}" stroke="{COLOR_GRID}" stroke-dasharray="2,2" stroke-width="1"/>')
    
    # 2. Поля
    ordered = sorted(fields, key=lambda f: int(f.get("msb", 0)), reverse=True)
    for idx, f in enumerate(ordered):
        msb, lsb = int(f.get("msb", 0)), int(f.get("lsb", 0))
        nbits = msb - lsb + 1
        x = left + (width_bits - 1 - msb) * col_w
        w = nbits * col_w
        fill = COLOR_FILL_LIGHT if idx % 2 == 0 else COLOR_FILL_MED
        parts.append(f'<rect x="{x}" y="{top}" width="{w}" height="{row_h}" fill="{fill}" stroke="{COLOR_GRID}" stroke-width="2"/>')
        parts.append(f'<text x="{x+w/2}" y="{top+row_h/2+6}" text-anchor="middle" style="font: 700 16px sans-serif;">{esc(f.get("name", ""))}</text>')
    
    # 3. Штрихи ТОЛЬКО СВЕРХУ на каждой границе бита
    for i in range(width_bits + 1):
        x = left + i * col_w
        parts.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top + tick_h}" stroke="{COLOR_GRID}" stroke-width="1"/>')
    
    return {"W": W, "H": H, "title": title, "subtitle": f"{width_bits}-bit bitfield", "parts": parts}
    
# ---------- Рендерер SVG для code_list с width ----------
def render_code_list_svg(cl, REGISTRY):
    name = cl.get("name", "unknown")
    title = cl.get("title", name)
    width_bits = int(cl.get("width", 8))
    entries = cl.get("entries", [])
    
    if not entries:
        return None

    W, left, top, row_h = 1200, 32, 120, 40
    max_index_len = max(len(str(e.get("addr", e.get("index", "")))) for e in entries)
    max_name_len = max(len(str(e.get("name", ""))) for e in entries)
    char_width = 8
    left_bits = left + (max_index_len + max_name_len) * char_width + 40

    col_w = (W - left_bits - 32) / width_bits
    H = top + len(entries) * row_h + 50
    tick_h = row_h * 0.15  # Длина штриха
    parts = []
    
    # 1. Номера битов и пунктирные линии (сетка)
    for i in range(width_bits + 1):
        x = left_bits + i * col_w
        if i < width_bits:
            bit_num = width_bits - 1 - i
            parts.append(f'<text x="{x+col_w/2}" y="{top-10}" text-anchor="middle" style="font: 12px monospace; fill:#666;">{bit_num}</text>')
        parts.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top+len(entries)*row_h}" stroke="{COLOR_GRID}" stroke-dasharray="2,2" stroke-width="1"/>')
    
    # 2. Рисуем строки
    y = top
    for e in entries:
        idx = e.get("addr", e.get("index", ""))
        name = e.get("name", "")
        
        fields = []
        if "ref" in e and e["ref"] in REGISTRY:
            fields = REGISTRY[e["ref"]].get("fields", [])
        elif "fields" in e:
            fields = e["fields"]
        
        # Текст слева
        parts.append(f'<text x="{left}" y="{y + row_h/2 + 5}" style="font: 700 14px monospace;">{idx}</text>')
        parts.append(f'<text x="{left + max_index_len * char_width + 10}" y="{y + row_h/2 + 5}" style="font: 700 14px sans-serif;">{name}</text>')
        
        if fields:
            ordered = sorted(fields, key=lambda f: int(f["msb"]), reverse=True)
            
            # 2.1. Рисуем прямоугольники полей
            for idx2, f in enumerate(ordered):
                msb, lsb = int(f["msb"]), int(f["lsb"])
                nbits = msb - lsb + 1
                x = left_bits + (width_bits - 1 - msb) * col_w
                w = nbits * col_w
                fill = COLOR_FILL_LIGHT if idx2 % 2 == 0 else COLOR_FILL_MED
                parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{row_h}" fill="{fill}" stroke="{COLOR_GRID}" stroke-width="2"/>')
                parts.append(f'<text x="{x+w/2}" y="{y+row_h/2+6}" text-anchor="middle" style="font: 700 14px sans-serif;">{esc(f.get("name", ""))}</text>')
            
            # 2.2. Рисуем штрихи ТОЛЬКО ВНУТРИ КАЖДОГО ПОЛЯ
            for f in ordered:
                msb, lsb = int(f["msb"]), int(f["lsb"])
                # Штрихи для каждой границы бита внутри поля
                for bit_idx in range(lsb, msb + 1):
                    # Позиция границы бита: bit_idx — это LSB. 
                    # В SVG координаты: биты идут справа налево.
                    # x = left_bits + (width_bits - 1 - bit_idx) * col_w
                    x = left_bits + (width_bits - 1 - bit_idx) * col_w
                    parts.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + tick_h}" stroke="{COLOR_GRID}" stroke-width="1"/>')
                    
                    # А также правую границу последнего бита (msb)
                    # (если bit_idx == msb, то нужно добавить x + col_w)
                
                # Добавляем правую границу поля (x + w), чтобы штрих был и там
                x_right = left_bits + (width_bits - lsb) * col_w
                parts.append(f'<line x1="{x_right}" y1="{y}" x2="{x_right}" y2="{y + tick_h}" stroke="{COLOR_GRID}" stroke-width="1"/>')
        else:
            # Если полей нет — рисуем пустую полосу
            parts.append(f'<rect x="{left_bits}" y="{y}" width="{W - left_bits - 32}" height="{row_h}" fill="{COLOR_FILL_LIGHT}" stroke="{COLOR_GRID}" stroke-width="2"/>')
            
            # Штрихи для всех битов (потому что это цельный регистр)
            for i in range(width_bits + 1):
                x = left_bits + i * col_w
                parts.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + tick_h}" stroke="{COLOR_GRID}" stroke-width="1"/>')        
        y += row_h
    
    return {"W": W, "H": H, "title": title, "subtitle": f"{width_bits}-bit register map", "parts": parts}

# ---------- Рендерер Markdown для bitfield ----------
def render_bitfield_md(bf, REGISTRY):
    name = bf.get("name", "unknown")
    title = bf.get("title", name)
    fields = bf.get("fields", [])
    
    if not fields and "ref" in bf:
        ref = REGISTRY.get(bf["ref"])
        if ref:
            fields = ref.get("fields", [])
    
    if not fields:
        return None
        
    md = f"**{title}**\n\n"
    md += "| Field | Bits | Width | Description |\n| --- | --- | --- | --- |\n"
    for f in sorted(fields, key=lambda x: -int(x.get("msb", 0))):
        n = int(f.get("msb", 0)) - int(f.get("lsb", 0)) + 1
        md += f'| **{f.get("name")}** | [{f.get("msb")}:{f.get("lsb")}] | {n} | {f.get("description", "")} |\n'
    return md

# ---------- Рендерер Markdown для code_list ----------
def render_code_list_md(cl, REGISTRY):
    name = cl["name"]
    title = cl.get("title", name)
    fields = cl.get("fields", ["code", "name", "description"])
    entries = cl.get("entries", [])
    
    md = f"**{title}**\n\n"
    md += "| " + " | ".join(f.capitalize() for f in fields) + " |\n"
    md += "| " + " | ".join("---" for _ in fields) + " |\n"
    
    for e in entries:
        cells = []
        for f in fields:
            v = e.get(f, "—")
            cells.append(str(v))
        md += "| " + " | ".join(cells) + " |\n"
    
    # Вывод notes (если есть)
    notes = cl.get("notes", [])
    if notes:
        md += "\n**Примечания:**\n\n"
        for n in notes:
            md += f"- {n}\n"
    
    return md

# ---------- Рендерер Markdown для memspace ----------
def render_memspace_md(ms, REGISTRY):
    name = ms["name"]
    title = ms.get("title", name)
    regions = ms.get("regions", [])
    md = f"**{title}**\n\n"
    md += "| Имя | Диапазон | Ширина | Назначение |\n| --- | --- | --- | --- |\n"
    for r in regions:
        md += f'| `{r.get("name")}` | {r.get("range")} | {r.get("width")} | {r.get("purpose")} |\n'
    return md

# ---------- Валидатор ----------

def verify_yaml_separators(filepath):
    """Проверяет, что перед каждым kind: (кроме первого) стоит ---"""
    lines = filepath.read_text(encoding="utf-8").splitlines()
    kind_count = 0
    sep_count = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("kind:"):
            kind_count += 1
        if stripped == "---":
            sep_count += 1
    
    # Если kind больше, чем (--- + 1), значит, где-то пропущен разделитель
    if kind_count > sep_count + 1:
        print(f"  ❌ ERROR: {filepath.name} has {kind_count} 'kind:' but only {sep_count} '---'.")
        print(f"     Add '---' between documents.")
        sys.exit(1)

# ---------- Препроцессор ----------
INCLUDE_RE = re.compile(r'\[(?:include|insert)\]\(([^)]+)\)')

def process_file(filepath, gen_dir, src_dir, seen=None):
    if seen is None: seen = set()
    filepath = Path(filepath).resolve()
    if filepath in seen: return f"*[Cycle: {filepath.name}]*"
    seen.add(filepath)

    text = filepath.read_text(encoding="utf-8")
    
    def replacer(match):
        rel = match.group(1)
        if rel.startswith("./"): rel = rel[2:]
        if rel.startswith("gen/"): rel = rel[4:]
            
        p = gen_dir / rel
        if not p.exists(): p = src_dir / rel
        if not p.exists():
            print(f"    ⚠️  not found: {rel} (in {filepath.name})")
            return f"*[Missing: {rel}]*"
        
        if rel.endswith("-table.md"):
            content = process_file(p, gen_dir, src_dir, seen)
            return content
            
        return process_file(p, gen_dir, src_dir, seen)

    return INCLUDE_RE.sub(replacer, text)

# ---------- Сборка проекта ----------
def build_project(project_dir):
    name = project_dir.name
    src_dir = project_dir
    docs_dir = src_dir / "docs"
    spec_dir = src_dir / "spec"
    gen_dir = docs_dir / "gen"  
    doc_images_dir = docs_dir / "images"
    
    out_dir = OUT / name
    out_docs_dir = out_dir / "docs"

    print(f"\n=== {name} ===")
    gen_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_docs_dir.mkdir(parents=True, exist_ok=True)

    # ФАЗА 1: Сбор всех YAML
    REGISTRY = {}
    if spec_dir.exists():
        for yml in sorted(spec_dir.glob("*.yaml")):
            verify_yaml_separators(yml)
            try:
                docs = list(yaml.safe_load_all(yml.read_text(encoding="utf-8")))
                for data in docs:
                    if not isinstance(data, dict) or "name" not in data:
                        continue
                    id_name = data["name"]
                    if id_name in REGISTRY:
                        print(f"  ❌ ERROR: Duplicate name '{id_name}' in {yml.name}")
                        sys.exit(1)
                    data["_source_file"] = yml.name 
                    REGISTRY[id_name] = data
            except Exception as e:
                print(f"  ❌ YAML error in {yml.name}: {e}")
                sys.exit(1)

    # ФАЗА 2: Валидация
    for id_name, data in REGISTRY.items():
        if "entries" in data:
            for e in data["entries"]:
                if "ref" in e and e["ref"] not in REGISTRY:
                    print(f"  ❌ ERROR: {id_name} references missing bitfield '{e['ref']}'")
                    sys.exit(1)

    # ФАЗА 3: Генерация
    for id_name, data in sorted(REGISTRY.items()):
        kind = data.get("kind")
        if not kind: continue
        
        src_file = data.get("_source_file", "unknown")
        print(f"  render: {id_name} ({kind}) [from {src_file}]")
        
        outputs = data.get("output")
        if not outputs:
            if kind == "bitfield": outputs = ["svg", "md"]
            elif kind == "code_list":
                outputs = ["svg", "md"] if "width" in data else ["md"]
            elif kind == "timing": outputs = ["svg"]                   
            elif kind == "memspace": outputs = ["md"]
            else: outputs = ["md"]

        # 1. Генерация SVG
        if "svg" in outputs:
            svg_content = None
            try:
                if kind == "bitfield":
                    svg_content = render_bitfield_svg(data, REGISTRY)
                elif kind == "code_list" and "width" in data:
                    svg_content = render_code_list_svg(data, REGISTRY)
                elif kind == "timing":
                    svg_content = render_timing_svg(data, REGISTRY)                      
                else:
                    print(f"    ⚠️  SVG generation not implemented for kind={kind} in {src_file}")
            except Exception as e:
                print(f"    ❌ ERROR in {src_file}: {e}")

            if svg_content:
                write_svg(gen_dir / f"{id_name}.svg", svg_content)
            else:
                print(f"    ❌ ERROR: SVG requested for '{id_name}' in {src_file}, but generation failed.")
                sys.exit(1)

        # 2. Генерация Markdown
        if "md" in outputs:
            md_content = ""
            try:
                if kind == "bitfield": md_content = render_bitfield_md(data, REGISTRY)
                elif kind == "code_list": md_content = render_code_list_md(data, REGISTRY)
                elif kind == "memspace": md_content = render_memspace_md(data, REGISTRY)
                else:
                    print(f"    ⚠️  MD generation not implemented for kind={kind} in {src_file}")
            except Exception as e:
                print(f"    ❌ ERROR in {src_file}: {e}")
            
            if md_content:
                write_text(gen_dir / f"{id_name}-table.md", md_content)

    # ФАЗА 4: Копирование
    if docs_dir.exists():
        for md in sorted(docs_dir.rglob("*.md")):
            if "gen" in md.parts or "images" in md.parts: continue
            rel = md.relative_to(docs_dir)
            text = process_file(md, gen_dir, src_dir)
            write_text(out_docs_dir / rel, text)

    if gen_dir.exists():
        for f in gen_dir.rglob("*"):
            if f.is_file():
                rel = f.relative_to(gen_dir)
                smart_copy(f, out_docs_dir / "gen" / rel)

    if doc_images_dir.exists():
        for f in doc_images_dir.rglob("*"):
            if f.is_file():
                rel = f.relative_to(doc_images_dir)
                smart_copy(f, out_docs_dir / "images" / rel)

    # 5) check.py
    check = src_dir / "check.py"
    if check.exists():
        subprocess.run([sys.executable, str(check)], cwd=src_dir, check=False)


def deploy():
    """Заморозить текущее состояние out/ в deploy/"""
    if not OUT.exists():
        print("❌ No out/ directory. Run build.py first.")
        return
    
    DEPLOY = ROOT / "docs"
    
    # Очищаем deploy/ (если есть)
    if DEPLOY.exists():
        print(f"🧹 Cleaning {DEPLOY}...")
        shutil.rmtree(DEPLOY)
    
    # Копируем out/ в deploy/
    print(f"📦 Copying {OUT} -> {DEPLOY}...")
    shutil.copytree(OUT, DEPLOY)
    
    print(f"✅ Deployed to {DEPLOY}")


# ---------- Main ----------
def main():
    if not SRC.exists():
        print("No src/ directory")
        return
    for project_dir in sorted(SRC.iterdir()):
        if project_dir.is_dir():
            build_project(project_dir)
    print("\nDone.")
    
    # Если передан флаг --deploy, замораживаем
    if "--deploy" in sys.argv:
        deploy()

if __name__ == "__main__":
    main()