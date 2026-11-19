#!/usr/bin/env python3
"""
buildex.py — генератор документации по архитектуре (стиль даташитов 90-х).

Идея: в YAML описывается только СУТЬ (регистры, биты, коды, автоматы, карты памяти,
временные диаграммы). Картинки и таблицы выводятся из сути сами.

Раскладка проекта:
    src/<project>/spec/*.yaml     спецификации (много документов через '---')
    src/<project>/docs/**/*.md    текст документации с директивами {{...}}
    src/<project>/buildex.yaml    (необязательно) lang: en | ru
    out/<project>/docs/...        результат (+ gen/ с картинками и таблицами)

Директивы в Markdown:
    {{auto:NAME}}      рисунок (если есть) + таблица
    {{figure:NAME}}    рисунок с подписью и автонумерацией
    {{table:NAME}}     таблица с подписью и автонумерацией
    {{ref:NAME}}       ссылка на сущность;  {{ref:NAME.FIELD}} — на поле/код/регистр
    {{const:NAME}}     значение константы
    {{include:path}}   вставка другого .md

Команды:
    buildex.py [build] [project ...] [--deploy] [--watch]
    buildex.py kinds                 список сущностей
    buildex.py explain <kind>        схема и пример
    buildex.py new <kind> <name>     заготовка YAML (в stdout)
"""
import argparse
import copy
import difflib
import filecmp
import hashlib
import html
import math
import os
import posixpath
import re
import shutil
import sys
import time
import urllib.parse
from pathlib import Path
from types import SimpleNamespace as NS

import yaml

VERSION = "1.5"
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "out"

# =============================================================================
#  Утилиты
# =============================================================================
INK = "#000000"
GRAY_TXT = "#555555"
FILL_A, FILL_B = "#F2F2F2", "#E0E0E0"
FILL_FIXED = "#DCE8F6"
GROUP_FILLS = ["#F2F2F2", "#DCE8F6", "#E6F2DC", "#F6E8DC", "#EBDCF6", "#F6F3DC"]

CAPTIONS = {
    "en": {"figure": "Figure", "table": "Table", "fields": "Fields"},
    "ru": {"figure": "Рис.", "table": "Таблица", "fields": "Поля"},
}


def esc(v):
    return html.escape(str(v), quote=True)


def n(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def as_int(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, str):
        try:
            return int(v.replace("_", "").strip(), 0)
        except ValueError:
            return None
    return None


def as_list(v):
    if v is None:
        return []
    return list(v) if isinstance(v, (list, tuple)) else [v]


def anchor_id(name):
    return re.sub(r"[^A-Za-z0-9_.\-]", "_", str(name))


def hexw(v, bits):
    return f"0x{v:0{max(1, (bits + 3) // 4)}X}"


def fmt_size(sz):
    for unit, k in (("GiB", 1 << 30), ("MiB", 1 << 20), ("KiB", 1 << 10)):
        if sz >= k and sz % k == 0:
            return f"{sz // k} {unit}"
    return f"{sz} B"


def md_cell(v):
    if v is None or v == "":
        return "—"
    return str(v).replace("|", "\\|").replace("\n", "<br>")


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for r in rows:
        out.append("| " + " | ".join(md_cell(c) for c in r) + " |")
    return "\n".join(out) + "\n"


def write_if_changed(path, content, produced):
    path = Path(path)
    produced.add(path.resolve())
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.write_text(content, encoding="utf-8")


def smart_copy(src, dst, produced):
    produced.add(Path(dst).resolve())
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and filecmp.cmp(src, dst, shallow=False):
        return
    shutil.copy2(src, dst)


def _hash(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def sync_tree(src_dir, dst_dir, produced):
    """Зеркалит src_dir -> dst_dir, копируя только новые/изменённые файлы (по md5)."""
    src_dir, dst_dir = Path(src_dir), Path(dst_dir)
    if not src_dir.exists():
        return
    for f in sorted(src_dir.rglob("*")):
        if not f.is_file():
            continue
        dst = dst_dir / f.relative_to(src_dir)
        produced.add(dst.resolve())
        if dst.exists() and _hash(dst) == _hash(f):
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dst)


# ---------- метрики текста (оценка ширины без шрифтов) ----------
_NARROW = set("iljtfIr.,:;'|!()[]/\\ 1")
_WIDE = set("mwMW@%")


def tw(s, size, mono=False, bold=False):
    s = str(s)
    if mono:
        return len(s) * size * 0.6
    w = 0.0
    for ch in s:
        if ch in _NARROW:
            w += 0.32
        elif ch in _WIDE:
            w += 0.88
        elif ch.isupper() or ch.isdigit():
            w += 0.66
        else:
            w += 0.56
    return w * size * (1.07 if bold else 1.0)


# =============================================================================
#  Диагностика
# =============================================================================
class Diag:
    def __init__(self):
        self.errors, self.warnings = [], []

    def err(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")

    def report(self):
        for w in self.warnings:
            print(f"  ⚠️  {w}")
        for e in self.errors:
            print(f"  ❌ {e}")


def W_(spec):
    return f"{spec.get('_file', '?')}:{spec.get('_line', '?')} {spec.get('kind', '?')} '{spec.get('name', '?')}'"


BASE_KEYS = ["kind", "name", "title", "subtitle", "description", "view", "notes"]


def check_keys(d, allowed, where, P, what="key"):
    allowed = list(allowed)
    for k in d:
        if str(k).startswith("_") or k in allowed:
            continue
        m = difflib.get_close_matches(str(k), allowed, n=1)
        hint = f" — did you mean '{m[0]}'?" if m else f" (allowed: {', '.join(sorted(allowed))})"
        P.diag.err(where, f"unknown {what} '{k}'{hint}")


class UniqueLoader(yaml.SafeLoader):
    """SafeLoader, который ловит дубли ключей (типично: забыли '---') и помнит строку документа."""
    last_line = 0

    def construct_document(self, node):
        self.last_line = node.start_mark.line + 1
        return super().construct_document(node)

    def construct_mapping(self, node, deep=False):
        seen = set()
        for k, _ in node.value:
            if isinstance(k, yaml.ScalarNode):
                if k.value in seen:
                    raise yaml.constructor.ConstructorError(
                        None, None,
                        f"duplicate key '{k.value}' at line {k.start_mark.line + 1} "
                        f"(forgot '---' between documents?)", k.start_mark)
                seen.add(k.value)
        return super().construct_mapping(node, deep)


# =============================================================================
#  SVG-примитивы
# =============================================================================
SVG_DEFS = """<defs>
<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
<rect width="6" height="6" fill="#FFFFFF"/><line x1="0" y1="0" x2="0" y2="6" stroke="#B0B0B0" stroke-width="2"/></pattern>
<pattern id="xpat" width="8" height="8" patternUnits="userSpaceOnUse">
<rect width="8" height="8" fill="#FFFFFF"/><path d="M0 0L8 8M8 0L0 8" stroke="#C07070" stroke-width="1"/></pattern>
<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto">
<path d="M0 0L10 5L0 10z" fill="#000000"/></marker>
</defs>"""


class Svg:
    def __init__(self):
        self.p = []

    def add(self, s):
        self.p.append(s)

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.p.append(f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def rect(self, x, y, w, h, fill="none", stroke=INK, sw=1.5, rx=0, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        r = f' rx="{rx}"' if rx else ""
        self.p.append(f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{r}{d}/>')

    def poly(self, pts, fill="none", stroke=INK, sw=1.5):
        s = " ".join(f"{n(x)},{n(y)}" for x, y in pts)
        self.p.append(f'<polygon points="{s}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def path(self, d, stroke=INK, sw=1.5, fill="none", marker=False, dash=None):
        m = ' marker-end="url(#arr)"' if marker else ""
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.p.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{m}{da}/>')

    def circle(self, cx, cy, r, fill="none", stroke=INK, sw=1.5):
        self.p.append(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def text(self, x, y, t, size=12, anchor="middle", bold=False, mono=False, fill=INK, rot=None, halo=False, over=False):
        cls = ' class="m"' if mono else ""
        w = ' font-weight="700"' if bold else ""
        tr = f' transform="rotate({rot} {n(x)} {n(y)})"' if rot else ""
        st = []
        if halo:
            st.append("paint-order:stroke;stroke:#fff;stroke-width:3px;stroke-linejoin:round")
        if over:
            st.append("text-decoration:overline")
        sty = f' style="{";".join(st)}"' if st else ""
        self.p.append(f'<text x="{n(x)}" y="{n(y)}" font-size="{n(size)}" text-anchor="{anchor}" fill="{fill}"{w}{cls}{tr}{sty}>{esc(t)}</text>')

    def fit_label(self, cx, cy, t, avail_w, avail_h, bold=True, max_size=14, min_size=9, fill=INK, halo=False):
        """Подпись внутри ячейки: уменьшаем шрифт, затем поворачиваем, затем обрезаем."""
        t = str(t)
        size = max_size
        while size >= min_size and tw(t, size, bold=bold) > avail_w - 6:
            size -= 1
        if size >= min_size:
            self.text(cx, cy + size * 0.35, t, size, bold=bold, fill=fill, halo=halo)
            return
        rsize = min(12, max_size)
        while rsize >= min_size and tw(t, rsize, bold=bold) > avail_h - 8:
            rsize -= 1
        if rsize >= min_size and avail_w >= rsize + 4:
            self.text(cx, cy + rsize * 0.35, t, rsize, bold=bold, fill=fill, rot=-90, halo=halo)
            return
        s = t
        while len(s) > 1 and tw(s + "…", min_size, bold=bold) > avail_w - 4:
            s = s[:-1]
        self.text(cx, cy + min_size * 0.35, s + "…", min_size, bold=bold, fill=fill, halo=halo)

    def inner(self):
        return "\n".join(self.p)


def svg_doc(W, H, title, subtitle, inner):
    W = max(W, tw(title, 22, bold=True) + 64, tw(subtitle or "", 14) + 64)
    head = (f'<text x="32" y="38" font-size="22" font-weight="700" fill="{INK}">{esc(title)}</text>\n'
            f'<text x="32" y="62" font-size="14" fill="{GRAY_TXT}">{esc(subtitle or "")}</text>\n')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{n(W)}" height="{n(H)}" viewBox="0 0 {n(W)} {n(H)}">\n'
            f'{SVG_DEFS}\n<style>text{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}'
            f'.m{{font-family:ui-monospace,Menlo,Consolas,"DejaVu Sans Mono",monospace}}</style>\n'
            f'<rect width="{n(W)}" height="{n(H)}" fill="#FFFFFF"/>\n{head}{inner}\n</svg>\n')


# =============================================================================
#  Поля (bitfield) — общая основа для bitfield / encoding / regmap
# =============================================================================
FIELD_KEYS = ["name", "bits", "bit", "msb", "lsb", "description", "access", "reset", "enum", "reserved", "value", "group", "overlay"]


def fmt_const(v, nbits):
    if nbits == 1:
        return str(v)
    if nbits <= 4:
        return format(v, f"0{nbits}b") + "b"
    return hexw(v, nbits)


def fmt_reset(v, nbits):
    if isinstance(v, int) and not isinstance(v, bool):
        return str(v) if nbits == 1 else hexw(v, nbits)
    return None if v is None else str(v)


def norm_field(raw, W, where, P):
    if not isinstance(raw, dict):
        P.diag.err(where, f"field must be a mapping, got {raw!r}")
        return None
    nm = raw.get("name")
    check_keys(raw, FIELD_KEYS, f"{where} field '{nm}'", P, "field key")
    reserved = bool(raw.get("reserved", False))
    if nm is None and reserved:
        nm = "RSV"
    if not nm:
        P.diag.err(where, f"field without 'name': {raw!r}")
        return None
    nm = str(nm)
    msb = lsb = None
    if "bits" in raw:
        b = raw["bits"]
        if isinstance(b, (list, tuple)) and len(b) == 2:
            msb, lsb = as_int(b[0]), as_int(b[1])
        elif as_int(b) is not None and not isinstance(b, str):
            msb = lsb = as_int(b)
        elif isinstance(b, str) and ":" in b:
            p = b.strip("[] ").split(":")
            msb, lsb = as_int(p[0]), as_int(p[1])
    elif "bit" in raw:
        msb = lsb = as_int(raw["bit"])
    elif "msb" in raw and "lsb" in raw:
        msb, lsb = as_int(raw["msb"]), as_int(raw["lsb"])
    if msb is None or lsb is None:
        P.diag.err(where, f"field '{nm}': need 'bits: [msb, lsb]' or 'bit: N'")
        return None
    if not (0 <= lsb <= msb < W):
        P.diag.err(where, f"field '{nm}': bits [{msb}:{lsb}] outside 0..{W - 1}")
        return None
    nb = msb - lsb + 1
    fixed = None
    if "value" in raw:
        fixed = as_int(raw["value"])
        if fixed is None or not (0 <= fixed < (1 << nb)):
            P.diag.err(where, f"field '{nm}': value {raw['value']!r} does not fit {nb} bit(s)")
            fixed = None
    return NS(name=nm, msb=msb, lsb=lsb, nb=nb, desc=raw.get("description"), access=raw.get("access"),
              reset=fmt_reset(raw.get("reset"), nb), enum=raw.get("enum"), reserved=reserved,
              fixed=fixed, group=raw.get("group"), overlay=bool(raw.get("overlay")))


def apply_fixed(fields, fixed, where, P):
    for k, v in (fixed or {}).items():
        f = next((x for x in fields if x.name == k), None)
        if f is None:
            m = difflib.get_close_matches(str(k), [x.name for x in fields], n=1)
            P.diag.err(where, f"'fixed/when' refers to unknown field '{k}'" + (f" — did you mean '{m[0]}'?" if m else ""))
            continue
        iv = as_int(v)
        if iv is None or not (0 <= iv < (1 << f.nb)):
            P.diag.err(where, f"field '{k}': value {v!r} does not fit {f.nb} bit(s)")
            continue
        f.fixed = iv


def check_layout(fields, W, where, P, warn_gaps=True, tag=""):
    used, cover = {}, set()
    for f in fields:
        cover.update(range(f.lsb, f.msb + 1))
        if f.overlay:
            continue
        for b in range(f.lsb, f.msb + 1):
            if b in used:
                P.diag.err(where, f"{tag}fields '{used[b]}' and '{f.name}' overlap at bit {b} (use 'overlay: true' for an alternate meaning of the same bits)")
                break
            used[b] = f.name
    if warn_gaps:
        gaps, start = [], None
        for b in range(W + 1):
            if b < W and b not in cover:
                start = b if start is None else start
            elif start is not None:
                gaps.append((b - 1, start))
                start = None
        if gaps:
            P.diag.warn(where, f"{tag}bits not covered: " + ", ".join(f"[{h}:{l}]" if h != l else f"[{h}]" for h, l in reversed(gaps)))


def check_field_enums(fields, where, P):
    for f in fields:
        if not f.enum:
            continue
        e = P.REG.get(f.enum)
        if e is None or e.get("kind") != "enum":
            m = difflib.get_close_matches(str(f.enum), [k for k, v in P.REG.items() if v.get("kind") == "enum"], n=1)
            P.diag.err(where, f"field '{f.name}': enum '{f.enum}' not found" + (f" — did you mean '{m[0]}'?" if m else ""))
            continue
        for lo, hi, _ in e.get("_ranges", []):
            if hi >= (1 << f.nb):
                P.diag.warn(where, f"field '{f.name}' is {f.nb} bit(s) but enum '{f.enum}' has value {hi}")
                break


def merge_fields(base, extra):
    out = list(base)
    for f in extra:
        for i, g in enumerate(out):
            if g.name == f.name:
                out[i] = f
                break
        else:
            out.append(f)
    return out


def resolve_bitfield(spec, P, stack=()):
    if "_res" in spec:
        return spec["_res"]
    where = W_(spec)
    if spec["name"] in stack:
        P.diag.err(where, "cyclic 'extends'")
        spec["_res"] = None
        return None
    W, base = None, []
    if spec.get("extends"):
        b = P.REG.get(spec["extends"])
        if b is None or b.get("kind") != "bitfield":
            P.diag.err(where, f"'extends: {spec['extends']}' — bitfield not found")
        else:
            r = resolve_bitfield(b, P, tuple(stack) + (spec["name"],))
            if r:
                W, base = r[0], [copy.copy(f) for f in r[1]]
    if spec.get("width") is not None:
        w = as_int(spec["width"])
        if w is None or not 1 <= w <= 256:
            P.diag.err(where, f"bad 'width': {spec['width']!r}")
        else:
            W = w
    if W is None:
        P.diag.err(where, "missing 'width' (or 'extends')")
        spec["_res"] = None
        return None
    extra = [f for f in (norm_field(r, W, where, P) for r in as_list(spec.get("fields"))) if f]
    fields = merge_fields(base, extra)
    apply_fixed(fields, spec.get("fixed"), where, P)
    fields.sort(key=lambda f: -f.msb)
    check_layout(fields, W, where, P, warn_gaps=not spec.get("partial"))
    spec["_res"] = (W, fields)
    return spec["_res"]


def fields_table_md(fields, W):
    ha = any(f.access for f in fields)
    hr = any(f.reset is not None for f in fields)
    hf = any(f.fixed is not None for f in fields)
    hd = ["Field", "Bits", "Width"] + (["Access"] if ha else []) + (["Reset"] if hr else []) + (["Fixed"] if hf else []) + ["Description"]
    rows = []
    for f in sorted(fields, key=lambda x: -x.msb):
        bits = f"[{f.msb}:{f.lsb}]" if f.msb != f.lsb else f"[{f.msb}]"
        d = f.desc or ("Reserved" if f.reserved else "")
        if f.enum:
            d = (d + " " if d else "") + "{{" + "ref:" + str(f.enum) + "}}"
        row = [f'<a id="{anchor_id(f.name)}"></a>**{f.name}**', bits, f.nb]
        if ha:
            row.append(f.access)
        if hr:
            row.append(f.reset)
        if hf:
            row.append(None if f.fixed is None else fmt_const(f.fixed, f.nb))
        row.append(d)
        rows.append(row)
    return md_table(hd, rows)


def notes_md(spec):
    notes = as_list(spec.get("notes"))
    if not notes:
        return ""
    return "\n**Notes:**\n\n" + "".join(f"- {x}\n" for x in notes)


# ---------- рисование одной «полосы» битов ----------
def draw_lane(svg, fields, hi, lo, x0, y, col_w, row_h, idx_base=0):
    nb = hi - lo + 1
    svg.rect(x0, y, nb * col_w, row_h, fill="#FFFFFF", stroke=INK, sw=1.5)
    for i, f in enumerate(fields):
        sh, sl = min(f.msb, hi), max(f.lsb, lo)
        if sh < sl or f.overlay:
            continue
        x = x0 + (hi - sh) * col_w
        w = (sh - sl + 1) * col_w
        if f.reserved:
            fill = "url(#hatch)"
        elif f.fixed is not None:
            fill = FILL_FIXED
        else:
            fill = FILL_A if (i + idx_base) % 2 == 0 else FILL_B
        svg.rect(x, y, w, row_h, fill=fill, stroke=INK, sw=1.5)
        cx, cy = x + w / 2, y + row_h / 2
        halo = f.reserved
        if f.fixed is not None and w >= 18 and f.name:
            top = f.name
            val = fmt_const(f.fixed, f.nb)
            if tw(top, 12, bold=True) <= w - 6 and tw(val, 11, mono=True) <= w - 4:
                svg.text(cx, cy - 3, top, 12, bold=True)
                svg.text(cx, cy + 12, val, 11, mono=True, fill="#1A3A6A")
            else:
                svg.fit_label(cx, cy, f"{top}={val}", w, row_h, bold=True, max_size=12, halo=halo)
        elif f.name:
            svg.fit_label(cx, cy, f.name, w, row_h, bold=True, max_size=14, halo=halo)
        # засечки по границам битов внутри поля (сверху)
        for b in range(sh, sl, -1):
            xx = x0 + (hi - b + 1) * col_w
            svg.line(xx, y, xx, y + row_h * 0.14, INK, 1)


def draw_overlays(svg, fields, hi, lo, x0, y, col_w):
    """Поля с overlay: true — альтернативная трактовка тех же битов, тонкая полоса под строкой."""
    used = 0
    for f in fields:
        sh, sl = min(f.msb, hi), max(f.lsb, lo)
        if not f.overlay or sh < sl:
            continue
        x = x0 + (hi - sh) * col_w
        w = (sh - sl + 1) * col_w
        yy = y + 4 + used * 24
        svg.rect(x, yy, w, 20, fill="#FFF8E1", stroke="#8A6D00", sw=1.2, dash="4,2")
        svg.fit_label(x + w / 2, yy + 10, f.name, w, 20, bold=True, max_size=11, min_size=8)
        used += 1
    return used * 24


def draw_bit_numbers(svg, bits, hi, x0, col_w, y):
    for b in sorted(set(bits), reverse=True):
        if 0 <= b <= hi:
            svg.text(x0 + (hi - b + 0.5) * col_w, y, str(b), 11, mono=True, fill="#444444")


def draw_info_line(svg, fields, hi, lo, x0, col_w, y):
    drawn = False
    for f in fields:
        sh, sl = min(f.msb, hi), max(f.lsb, lo)
        if sh < sl or not (f.access or f.reset is not None):
            continue
        t = " · ".join(str(x) for x in (f.access, f.reset) if x not in (None, ""))
        w = (sh - sl + 1) * col_w
        if tw(t, 10, mono=True) <= w - 2:
            svg.text(x0 + (hi - sh) * col_w + w / 2, y, t, 10, mono=True, fill=GRAY_TXT)
            drawn = True
    return drawn


def edge_bits(fields):
    s = set()
    for f in fields:
        s.add(f.msb)
        s.add(f.lsb)
    return s


# =============================================================================
#  KIND: bitfield
# =============================================================================
def v_bitfield(spec, P):
    where = W_(spec)
    check_keys(spec, BASE_KEYS + ["width", "fields", "extends", "fixed", "split", "partial"], where, P)
    r = resolve_bitfield(spec, P)
    if r:
        check_field_enums(r[1], where, P)
        sp = spec.get("split")
        if sp is not None and (as_int(sp) is None or as_int(sp) < 1):
            P.diag.err(where, f"bad 'split': {sp!r}")


def d_bitfield(spec, P):
    r = spec.get("_res")
    if not r:
        return None
    W, fields = r
    lane = as_int(spec.get("split")) or min(W, 32)
    lanes = [(min(W - 1, h + lane - 1), h) for h in range(0, W, lane)]
    lanes = [(hi, lo) for hi, lo in sorted(lanes, reverse=True)]
    multi = len(lanes) > 1
    gutter = 78 if multi else 0
    x0 = 32 + gutter
    col_w = min(36.0, 1080.0 / lane)
    row_h = 50
    info = any(f.access or f.reset is not None for f in fields)
    svg = Svg()
    y = 104
    for hi, lo in lanes:
        draw_bit_numbers(svg, [b for f in fields for b in (f.msb, f.lsb) if lo <= b <= hi] + [hi, lo], hi, x0, col_w, y - 8)
        if multi:
            svg.text(32, y + row_h / 2 + 4, f"[{hi}:{lo}]", 13, "start", mono=True, fill=GRAY_TXT)
        draw_lane(svg, fields, hi, lo, x0, y, col_w, row_h)
        y += draw_overlays(svg, fields, hi, lo, x0, y + row_h, col_w)
        if info:
            draw_info_line(svg, fields, hi, lo, x0, col_w, y + row_h + 14)
            y += 20
        y += row_h + 34
    Wpx = x0 + lane * col_w + 32
    return svg_doc(Wpx, y - 4, spec.get("title", spec["name"]), spec.get("subtitle", f"{W}-bit register"), svg.inner())


def t_bitfield(spec, P):
    r = spec.get("_res")
    return (fields_table_md(r[1], r[0]) + notes_md(spec)) if r else None


def a_bitfield(spec):
    r = spec.get("_res")
    return {f.name for f in r[1]} if r else set()


# =============================================================================
#  KIND: enum  (таблица кодов)
# =============================================================================
_RANGE_RE = re.compile(r"^\s*(\S+?)\s*\.\.\s*(\S+?)\s*$")


def parse_value(v):
    iv = as_int(v)
    if iv is not None:
        return iv, iv
    if isinstance(v, str):
        m = _RANGE_RE.match(v)
        if m and as_int(m.group(1)) is not None and as_int(m.group(2)) is not None:
            return as_int(m.group(1)), as_int(m.group(2))
    return None


def fmt_value(v, spec):
    radix = spec.get("radix", "dec")
    bits = as_int(spec.get("width")) or 1

    def one(x):
        if radix == "hex":
            return hexw(x, bits)
        if radix == "bin":
            return f"0b{x:0{bits}b}"
        return str(x)
    pv = parse_value(v)
    if pv is None:
        return str(v)
    if pv[0] == pv[1] and not isinstance(v, str):
        return one(pv[0])
    return f"{one(pv[0])}..{one(pv[1])}"


def v_enum(spec, P):
    where = W_(spec)
    check_keys(spec, BASE_KEYS + ["entries", "columns", "width", "radix"], where, P)
    entries = spec.get("entries")
    if not isinstance(entries, list) or not entries:
        P.diag.err(where, "'entries' must be a non-empty list")
        return
    if spec.get("radix", "dec") not in ("dec", "hex", "bin"):
        P.diag.err(where, "'radix' must be dec | hex | bin")
    ranges, order = [], []
    for i, e in enumerate(entries):
        if not isinstance(e, dict) or "value" not in e or "name" not in e:
            P.diag.err(where, f"entry #{i + 1} needs 'value' and 'name': {e!r}")
            continue
        for k in e:
            if k not in order:
                order.append(k)
        pv = parse_value(e["value"])
        if pv:
            for lo, hi, nm in ranges:
                if pv[0] <= hi and lo <= pv[1]:
                    P.diag.err(where, f"value {e['value']} ('{e['name']}') overlaps '{nm}'")
                    break
            ranges.append((pv[0], pv[1], e["name"]))
    spec["_ranges"] = ranges
    w = as_int(spec.get("width"))
    if w:
        for lo, hi, nm in ranges:
            if hi >= (1 << w):
                P.diag.warn(where, f"value {hi} ('{nm}') does not fit width {w}")
    cols = []
    if spec.get("columns"):
        for c in spec["columns"]:
            if isinstance(c, dict):
                cols.append((c["key"], c.get("title", str(c["key"]).replace("_", " ").capitalize())))
            else:
                cols.append((c, str(c).replace("_", " ").capitalize()))
    else:
        keys = ["value", "name"] + [k for k in order if k not in ("value", "name")]
        cols = [(k, k.replace("_", " ").capitalize()) for k in keys]
    spec["_cols"] = cols


def t_enum(spec, P):
    if "_cols" not in spec:
        return None
    rows = []
    for e in spec["entries"]:
        row = []
        for k, _ in spec["_cols"]:
            v = e.get(k)
            if k == "value":
                v = fmt_value(v, spec)
            elif k == "name":
                v = f'<a id="{anchor_id(e.get("name"))}"></a>**{e.get("name")}**'
            row.append(v)
        rows.append(row)
    return md_table([t for _, t in spec["_cols"]], rows) + notes_md(spec)


def a_enum(spec):
    return {str(e.get("name")) for e in spec.get("entries", []) if isinstance(e, dict)}


# =============================================================================
#  KIND: encoding  (семейство форматов слова)
# =============================================================================
def v_encoding(spec, P):
    where = W_(spec)
    check_keys(spec, BASE_KEYS + ["width", "common", "variants"], where, P)
    W = as_int(spec.get("width"))
    if W is None or not 1 <= W <= 128:
        P.diag.err(where, "missing or bad 'width'")
        return
    common = [f for f in (norm_field(r, W, where, P) for r in as_list(spec.get("common"))) if f]
    variants = spec.get("variants")
    if not isinstance(variants, list) or not variants:
        P.diag.err(where, "'variants' must be a non-empty list")
        return
    res, seen_when = [], {}
    for i, v in enumerate(variants):
        vw = f"{where} variant #{i + 1}"
        if not isinstance(v, dict) or "name" not in v:
            P.diag.err(vw, "variant needs 'name'")
            continue
        vw = f"{where} variant '{v['name']}'"
        check_keys(v, ["name", "title", "when", "fields", "ref", "description"], vw, P, "variant key")
        if v.get("ref"):
            b = P.REG.get(v["ref"])
            if b is None or b.get("kind") != "bitfield":
                P.diag.err(vw, f"ref '{v['ref']}' is not a bitfield")
                continue
            r = resolve_bitfield(b, P)
            if not r:
                continue
            if r[0] != W:
                P.diag.err(vw, f"ref '{v['ref']}' is {r[0]} bits, expected {W}")
            fields = [copy.copy(f) for f in r[1]]
        else:
            extra = [f for f in (norm_field(r_, W, vw, P) for r_ in as_list(v.get("fields"))) if f]
            fields = merge_fields([copy.copy(f) for f in common], extra)
        when = v.get("when") or {}
        apply_fixed(fields, when, vw, P)
        fields.sort(key=lambda f: -f.msb)
        check_layout(fields, W, vw, P, tag="")
        check_field_enums(fields, vw, P)
        key = tuple(sorted((str(k), as_int(x)) for k, x in when.items()))
        if key in seen_when:
            P.diag.err(vw, f"same 'when' as variant '{seen_when[key]}' — ambiguous decoding")
        seen_when[key] = v["name"]
        res.append(NS(name=str(v["name"]), title=v.get("title"), when=when, desc=v.get("description"), fields=fields))
    spec["_W"], spec["_vars"] = W, res


def when_str(when):
    return " ".join(f"{k}={v}" for k, v in when.items())


def stack_diagram(title, subtitle, rows, W, header_bits):
    """rows: [(label, sublabel, fields)] — общая сетка битов, подписи слева."""
    svg = Svg()
    lab_w = max([tw(r[0], 13, bold=True) for r in rows] + [tw(r[1], 11, mono=True) for r in rows if r[1]] + [30]) + 20
    x0 = 32 + lab_w
    col_w = min(36.0, 1000.0 / W)
    row_h, gap, y = 46, 14, 112
    draw_bit_numbers(svg, header_bits | {W - 1, 0}, W - 1, x0, col_w, y - 10)
    for i, (lab, sub, fields) in enumerate(rows):
        svg.text(32, y + row_h / 2 - (3 if sub else -4), lab, 13, "start", bold=True)
        if sub:
            svg.text(32, y + row_h / 2 + 13, sub, 11, "start", mono=True, fill=GRAY_TXT)
        draw_lane(svg, fields, W - 1, 0, x0, y, col_w, row_h)
        y += draw_overlays(svg, fields, W - 1, 0, x0, y + row_h, col_w)
        y += row_h + gap
    return svg_doc(x0 + W * col_w + 32, y + 8, title, subtitle, svg.inner())


def d_encoding(spec, P):
    if "_vars" not in spec:
        return None
    W = spec["_W"]
    rows = [(v.title or v.name, when_str(v.when), v.fields) for v in spec["_vars"]]
    bits = set()
    for v in spec["_vars"]:
        bits |= edge_bits(v.fields)
    return stack_diagram(spec.get("title", spec["name"]), spec.get("subtitle", f"{W}-bit word · {len(rows)} formats"), rows, W, bits)


def t_encoding(spec, P):
    if "_vars" not in spec:
        return None
    md = md_table(["Format", "Selector", "Description"],
                  [[f'<a id="{anchor_id(v.name)}"></a>**{v.title or v.name}**', f"`{when_str(v.when)}`" if v.when else "—", v.desc] for v in spec["_vars"]])
    for v in spec["_vars"]:
        md += f"\n**{v.title or v.name}**" + (f" (`{when_str(v.when)}`)" if v.when else "") + "\n\n"
        md += fields_table_md(v.fields, spec["_W"])
    return md + notes_md(spec)


def a_encoding(spec):
    s = set()
    for v in spec.get("_vars", []):
        s.add(v.name)
        s |= {f.name for f in v.fields}
    return s


# =============================================================================
#  KIND: regmap  (регистры по смещениям)
# =============================================================================
def v_regmap(spec, P):
    where = W_(spec)
    check_keys(spec, BASE_KEYS + ["width", "registers", "base"], where, P)
    W = as_int(spec.get("width", 32))
    if W is None or not 1 <= W <= 128:
        P.diag.err(where, "bad 'width'")
        return
    regs, seen = [], {}
    for i, r in enumerate(as_list(spec.get("registers"))):
        rw = f"{where} register #{i + 1}"
        if not isinstance(r, dict) or "name" not in r or "offset" not in r:
            P.diag.err(rw, "register needs 'offset' and 'name'")
            continue
        rw = f"{where} register '{r['name']}'"
        check_keys(r, ["offset", "name", "ref", "fields", "access", "reset", "description", "width"], rw, P, "register key")
        off = as_int(r["offset"])
        if off is None:
            P.diag.err(rw, f"bad offset {r['offset']!r}")
            continue
        if off in seen:
            P.diag.err(rw, f"offset {hexw(off, 8)} already used by '{seen[off]}'")
        seen[off] = r["name"]
        rwid, fields = as_int(r.get("width")) or W, []
        if r.get("ref"):
            b = P.REG.get(r["ref"])
            if b is None or b.get("kind") != "bitfield":
                P.diag.err(rw, f"ref '{r['ref']}' is not a bitfield")
            else:
                rr = resolve_bitfield(b, P)
                if rr:
                    rwid, fields = rr[0], rr[1]
        elif r.get("fields"):
            fields = [f for f in (norm_field(x, rwid, rw, P) for x in r["fields"]) if f]
            fields.sort(key=lambda f: -f.msb)
            check_layout(fields, rwid, rw, P)
            check_field_enums(fields, rw, P)
        regs.append(NS(offset=off, name=str(r["name"]), fields=fields, width=rwid, access=r.get("access"),
                       reset=fmt_reset(r.get("reset"), rwid), desc=r.get("description")))
    regs.sort(key=lambda r: r.offset)
    spec["_W"], spec["_regs"] = W, regs


def _offw(regs):
    return max([2] + [(r.offset.bit_length() + 3) // 4 for r in regs])


def t_regmap(spec, P):
    if "_regs" not in spec:
        return None
    regs = spec["_regs"]
    ow = _offw(regs)
    ha = any(r.access for r in regs)
    hr = any(r.reset is not None for r in regs)
    hd = ["Offset", "Name"] + (["Access"] if ha else []) + (["Reset"] if hr else []) + ["Description"]
    rows = []
    for r in regs:
        row = [f"`0x{r.offset:0{ow}X}`", f'<a id="{anchor_id(r.name)}"></a>**{r.name}**']
        if ha:
            row.append(r.access)
        if hr:
            row.append(r.reset)
        row.append(r.desc)
        rows.append(row)
    md = md_table(hd, rows)
    for r in regs:
        if r.fields:
            md += f"\n**{r.name}** (`0x{r.offset:0{ow}X}`)\n\n" + fields_table_md(r.fields, r.width)
    return md + notes_md(spec)


def d_regmap(spec, P):
    if "_regs" not in spec:
        return None
    W, regs = spec["_W"], spec["_regs"]
    ow = _offw(regs)
    rows, bits = [], set()
    for r in regs:
        fl = r.fields or [NS(name=r.name, msb=r.width - 1, lsb=0, nb=r.width, fixed=None, reserved=False, access=None, reset=None, desc=None, enum=None, overlay=False, group=None)]
        bits |= edge_bits(fl)
        rows.append((r.name, f"0x{r.offset:0{ow}X}", fl))
    return stack_diagram(spec.get("title", spec["name"]), spec.get("subtitle", f"{W}-bit registers"), rows, W, bits)


def a_regmap(spec):
    s = set()
    for r in spec.get("_regs", []):
        s.add(r.name)
        s |= {f.name for f in r.fields}
    return s


# =============================================================================
#  KIND: memmap
# =============================================================================
def v_memmap(spec, P):
    where = W_(spec)
    check_keys(spec, BASE_KEYS + ["width", "regions", "order"], where, P)
    aw = as_int(spec.get("width", 32)) or 32
    regs = []
    for i, r in enumerate(as_list(spec.get("regions"))):
        rw = f"{where} region #{i + 1}"
        if not isinstance(r, dict) or "name" not in r:
            P.diag.err(rw, "region needs 'name'")
            continue
        rw = f"{where} region '{r['name']}'"
        check_keys(r, ["name", "start", "end", "size", "access", "purpose", "description", "group", "width"], rw, P, "region key")
        st = as_int(r.get("start"))
        en = as_int(r.get("end"))
        sz = as_int(r.get("size"))
        if st is None or (en is None and sz is None):
            P.diag.err(rw, "need 'start' and ('end' or 'size')")
            continue
        if en is None:
            en = st + sz - 1
        if en < st:
            P.diag.err(rw, "end < start")
            continue
        if en >= (1 << aw):
            P.diag.err(rw, f"end {hex(en)} outside {aw}-bit address space")
        regs.append(NS(name=str(r["name"]), start=st, end=en, access=r.get("access"),
                       purpose=r.get("purpose") or r.get("description"), group=r.get("group"), width=r.get("width")))
    regs.sort(key=lambda r: r.start)
    for a, b in zip(regs, regs[1:]):
        if b.start <= a.end:
            P.diag.err(where, f"regions '{a.name}' and '{b.name}' overlap")
    spec["_aw"], spec["_regions"] = aw, regs


def d_memmap(spec, P):
    if "_regions" not in spec:
        return None
    aw, regs = spec["_aw"], spec["_regions"]
    dig = (aw + 3) // 4
    items = []
    for i, r in enumerate(regs):
        if i and r.start > regs[i - 1].end + 1:
            items.append(NS(gap=True, start=regs[i - 1].end + 1, end=r.start - 1))
        items.append(r)
    if spec.get("order", "desc") == "desc":
        items.reverse()
    groups = []
    for r in regs:
        if r.group and r.group not in groups:
            groups.append(r.group)
    svg = Svg()
    addr_w = tw("0x" + "F" * dig, 12, mono=True) + 14
    x0 = 32 + addr_w
    bw = 340
    y = 96
    for it in items:
        h = 34 if getattr(it, "gap", False) else (58 if it.purpose else 44)
        top_a, bot_a = (it.end, it.start) if spec.get("order", "desc") == "desc" else (it.start, it.end)
        if getattr(it, "gap", False):
            svg.rect(x0, y, bw, h, fill="#FFFFFF", stroke="#888888", sw=1, dash="4,3")
            svg.text(x0 + bw / 2, y + h / 2 + 4, "unmapped", 11, fill="#888888")
        else:
            if it.group:
                fill = GROUP_FILLS[(groups.index(it.group) + 1) % len(GROUP_FILLS)]
            else:
                fill = FILL_A
            svg.rect(x0, y, bw, h, fill=fill, stroke=INK, sw=1.5)
            if it.purpose:
                svg.fit_label(x0 + bw / 2, y + h / 2 - 8, it.name, bw, h, bold=True, max_size=14)
                svg.text(x0 + bw / 2, y + h / 2 + 12, str(it.purpose), 11, fill=GRAY_TXT)
            else:
                svg.fit_label(x0 + bw / 2, y + h / 2, it.name, bw, h, bold=True, max_size=14)
            right = " · ".join(x for x in (str(it.access) if it.access else "", fmt_size(it.end - it.start + 1)) if x)
            svg.text(x0 + bw + 12, y + h / 2 + 4, right, 11, "start", fill=GRAY_TXT)
        svg.text(x0 - 8, y + 11, f"0x{top_a:0{dig}X}", 12, "end", mono=True)
        if top_a != bot_a:
            svg.text(x0 - 8, y + h - 3, f"0x{bot_a:0{dig}X}", 12, "end", mono=True)
        y += h
    return svg_doc(x0 + bw + 130, y + 24, spec.get("title", spec["name"]), spec.get("subtitle", f"{aw}-bit address space"), svg.inner())


def t_memmap(spec, P):
    if "_regions" not in spec:
        return None
    dig = (spec["_aw"] + 3) // 4
    ha = any(r.access for r in spec["_regions"])
    hw = any(r.width is not None for r in spec["_regions"])
    hd = ["Range", "Name", "Size"] + (["Width"] if hw else []) + (["Access"] if ha else []) + ["Purpose"]
    rows = []
    for r in spec["_regions"]:
        row = [f"`0x{r.start:0{dig}X}`–`0x{r.end:0{dig}X}`", f'<a id="{anchor_id(r.name)}"></a>**{r.name}**', fmt_size(r.end - r.start + 1)]
        if hw:
            row.append(r.width)
        if ha:
            row.append(r.access)
        row.append(r.purpose)
        rows.append(row)
    return md_table(hd, rows) + notes_md(spec)


def a_memmap(spec):
    return {r.name for r in spec.get("_regions", [])}


# =============================================================================
#  KIND: timing  (WaveDrom-подобные волны)
# =============================================================================
def v_timing(spec, P):
    where = W_(spec)
    check_keys(spec, BASE_KEYS + ["signals", "arrows", "ticks", "tick_width", "width"], where, P)
    sigs_raw = as_list(spec.get("signals"))
    if not sigs_raw:
        P.diag.err(where, "'signals' must be a non-empty list")
        return
    # legacy: states → wave
    waves = []
    for s in sigs_raw:
        if not isinstance(s, dict) or "name" not in s:
            P.diag.err(where, f"signal needs 'name': {s!r}")
            continue
        check_keys(s, ["name", "wave", "data", "type", "states", "description"], f"{where} signal '{s['name']}'", P, "signal key")
        wave, data = s.get("wave"), list(s.get("data") or [])
        if wave is None and "states" in s:
            wave = ""
            for st in s["states"]:
                st = str(st)
                if st in ("0", "1", "x", "z"):
                    wave += st
                else:
                    wave += "="
                    data.append(st)
        waves.append([s, wave, data])
    nt = max([len(str(w)) for _, w, _ in waves if w is not None] + [0])
    if nt == 0:
        P.diag.err(where, "no signal has a 'wave'")
        return
    sigs = []
    for s, wave, data in waves:
        sw = f"{where} signal '{s['name']}'"
        if wave is None:
            if s.get("type") == "clock":
                wave = "p" + "." * (nt - 1)
            else:
                P.diag.err(sw, "needs 'wave'")
                continue
        wave = str(wave)
        runs, di = [], 0
        for i, ch in enumerate(wave):
            if ch == ".":
                if not runs:
                    P.diag.err(sw, "wave cannot start with '.'")
                    continue
                runs[-1].len += 1
                continue
            ch = {"P": "p", "N": "n", "h": "1", "l": "0"}.get(ch, ch)
            if ch not in "pn01xz=":
                P.diag.err(sw, f"unknown wave symbol '{ch}' (allowed: p n 0 1 h l x z = .)")
                continue
            label = None
            if ch == "=":
                if di < len(data):
                    label = str(data[di])
                else:
                    P.diag.warn(sw, "more '=' segments than entries in 'data'")
                    label = ""
                di += 1
            runs.append(NS(ch=ch, start=i, len=1, label=label))
        sigs.append(NS(name=str(s["name"]), runs=runs, ntk=len(wave)))
    names = {s.name: i for i, s in enumerate(sigs)}
    arrows = []
    for a in as_list(spec.get("arrows")):
        try:
            (s1, t1), (s2, t2) = a["from"], a["to"]
            if s1 not in names or s2 not in names:
                raise KeyError(s1 if s1 not in names else s2)
            arrows.append(NS(s1=names[s1], t1=float(t1), s2=names[s2], t2=float(t2), text=a.get("text", "")))
        except KeyError as e:
            P.diag.err(where, f"arrow refers to unknown signal {e}")
        except (TypeError, ValueError):
            P.diag.err(where, f"arrow needs from: [signal, tick] and to: [signal, tick]: {a!r}")
    spec["_sigs"], spec["_nt"], spec["_arrows"] = sigs, nt, arrows


def d_timing(spec, P):
    if "_sigs" not in spec:
        return None
    sigs, nt = spec["_sigs"], spec["_nt"]
    left = max([90] + [tw(s.name, 13, mono=True, bold=True) + 40 for s in sigs])
    if spec.get("tick_width"):
        col_w = spec["tick_width"]
    elif as_int(spec.get("width")):
        col_w = max(20, (as_int(spec["width"]) - left - 32) / nt)
    else:
        col_w = max(36, min(72, (960 - left) / nt))
    row_h, top = 46, 112
    svg = Svg()
    H = top + len(sigs) * row_h
    labels = spec.get("ticks")
    for i in range(nt + 1):
        x = left + i * col_w
        svg.line(x, top - 4, x, H, "#CCCCCC", 1)
        if i < nt and labels is not False:
            lab = str(labels[i]) if isinstance(labels, list) and i < len(labels) else f"T{i + 1}"
            svg.text(x + col_w / 2, top - 12, lab, 11, mono=True, fill="#666666")
    for idx, s in enumerate(sigs):
        yt = top + idx * row_h
        yb = yt + row_h
        ym = yt + row_h / 2
        hi, lo = yt + 9, yb - 9
        svg.text(left - 12, ym + 5, s.name, 13, "end", bold=True, mono=True)
        prev = None
        for r in s.runs:
            x, w = left + r.start * col_w, r.len * col_w
            if r.ch in "pn":
                a, b = (lo, hi) if r.ch == "p" else (hi, lo)
                d = ""
                for k in range(r.len):
                    xx = x + k * col_w
                    d += f"M{n(xx)} {n(a)} L{n(xx)} {n(b)} L{n(xx + col_w / 2)} {n(b)} L{n(xx + col_w / 2)} {n(a)} L{n(xx + col_w)} {n(a)} "
                svg.path(d.strip(), sw=2)
            elif r.ch in "01":
                y = hi if r.ch == "1" else lo
                svg.line(x, y, x + w, y, INK, 2)
                if prev and prev.ch in "01" and prev.ch != r.ch:
                    svg.line(x, hi, x, lo, INK, 2)
            elif r.ch == "=":
                sl = min(6, col_w / 4)
                svg.poly([(x + sl, hi), (x + w - sl, hi), (x + w, ym), (x + w - sl, lo), (x + sl, lo), (x, ym)], fill=FILL_A, sw=1.5)
                if r.label:
                    svg.fit_label(x + w / 2, ym, r.label, w - 2 * sl, row_h - 10, bold=False, max_size=12, min_size=8)
            elif r.ch == "x":
                svg.rect(x, hi, w, lo - hi, fill="url(#xpat)", stroke="#A05050", sw=1)
            elif r.ch == "z":
                svg.line(x, ym, x + w, ym, "#666666", 2, dash="5,3")
            prev = r
    for a in spec["_arrows"]:
        # концы стрелки — у краёв строк, обращённых друг к другу, чтобы не лезть на сами волны
        d = 1 if a.s2 > a.s1 else (-1 if a.s2 < a.s1 else 0)
        x1, x2 = left + a.t1 * col_w, left + a.t2 * col_w
        y1 = top + a.s1 * row_h + row_h / 2 + d * row_h * 0.32
        y2 = top + a.s2 * row_h + row_h / 2 - d * row_h * 0.32
        if d == 0:
            y1 = y2 = top + a.s1 * row_h + row_h / 2
        svg.path(f"M{n(x1)} {n(y1)} L{n(x2)} {n(y2)}", stroke="#B00020", sw=1.4, marker=True)
        svg.circle(x1, y1, 2.5, fill="#B00020", stroke="#B00020", sw=0.5)
        if a.text:
            lx, ly = (x1 + x2) / 2, (y1 + y2) / 2
            svg.text(lx + 7, ly + 4, a.text, 11, "start", fill="#B00020", halo=True)
    return svg_doc(left + nt * col_w + 40, H + 28, spec.get("title", spec["name"]), spec.get("subtitle", f"{nt} ticks"), svg.inner())


def a_timing(spec):
    return {s.name for s in spec.get("_sigs", [])}


# =============================================================================
#  KIND: fsm
# =============================================================================
def v_fsm(spec, P):
    where = W_(spec)
    check_keys(spec, BASE_KEYS + ["states", "transitions", "initial"], where, P)
    states = []
    for s in as_list(spec.get("states")):
        if isinstance(s, str):
            s = {"name": s}
        if not isinstance(s, dict) or "name" not in s:
            P.diag.err(where, f"state needs 'name': {s!r}")
            continue
        check_keys(s, ["name", "description", "output"], f"{where} state '{s['name']}'", P, "state key")
        if any(x.name == str(s["name"]) for x in states):
            P.diag.err(where, f"duplicate state '{s['name']}'")
            continue
        states.append(NS(name=str(s["name"]), desc=s.get("description"), out=s.get("output")))
    if not states:
        P.diag.err(where, "'states' must be non-empty")
        return
    names = [s.name for s in states]
    trans = []
    for t in as_list(spec.get("transitions")):
        if not isinstance(t, dict) or "from" not in t or "to" not in t:
            P.diag.err(where, f"transition needs 'from' and 'to': {t!r}")
            continue
        check_keys(t, ["from", "to", "when", "do", "description"], where, P, "transition key")
        bad = [x for x in (t["from"], t["to"]) if str(x) not in names]
        if bad:
            m = difflib.get_close_matches(str(bad[0]), names, n=1)
            P.diag.err(where, f"transition refers to unknown state '{bad[0]}'" + (f" — did you mean '{m[0]}'?" if m else ""))
            continue
        trans.append(NS(a=str(t["from"]), b=str(t["to"]), when=t.get("when"), do=t.get("do"), desc=t.get("description")))
    init = spec.get("initial")
    if init is not None and str(init) not in names:
        P.diag.err(where, f"initial state '{init}' not found")
        init = None
    if init is None:
        init = names[0]
        P.diag.warn(where, f"no 'initial' — using '{init}'")
    seen, todo = {str(init)}, [str(init)]
    while todo:
        c = todo.pop()
        for t in trans:
            if t.a == c and t.b not in seen:
                seen.add(t.b)
                todo.append(t.b)
    for s in names:
        if s not in seen:
            P.diag.warn(where, f"state '{s}' is unreachable from '{init}'")
    spec["_states"], spec["_trans"], spec["_init"] = states, trans, str(init)


def _clip(cx, cy, hw, hh, tx, ty):
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    sx = hw / abs(dx) if dx else 1e9
    sy = hh / abs(dy) if dy else 1e9
    t = min(sx, sy)
    return cx + dx * t, cy + dy * t


def d_fsm(spec, P):
    if "_states" not in spec:
        return None
    states, trans, init = spec["_states"], spec["_trans"], spec["_init"]
    N = len(states)
    size = {}
    for s in states:
        hw = max(50, (max(tw(s.name, 14, bold=True), tw(str(s.out or ""), 10.5, mono=True)) + 34) / 2)
        hh = 28 if s.out else 22
        size[s.name] = (hw, hh)
    maxw = max(v[0] for v in size.values()) * 2

    def label_of(t):
        return " ".join(x for x in (str(t.when) if t.when else "", f"/ {t.do}" if t.do else "") if x)

    maxlab = max([tw(label_of(t), 11) for t in trans] + [0])
    pos = {}
    if N == 1:
        pos[states[0].name] = (0, 0)
    elif N == 2:
        gap = maxw + maxlab + 90
        pos[states[0].name], pos[states[1].name] = (-gap / 2, 0), (gap / 2, 0)
    else:
        R = max(190, N * (maxw + 0.55 * maxlab + 70) / (2 * math.pi))
        init_i = [s.name for s in states].index(init)
        for i in range(N):
            a = math.pi + 2 * math.pi * ((i - init_i) % N) / N
            pos[states[i].name] = (R * math.cos(a), 0.85 * R * math.sin(a))
    svg = Svg()
    bb = [1e9, 1e9, -1e9, -1e9]

    def grow(x, y, w=0, h=0):
        bb[0], bb[1] = min(bb[0], x - w), min(bb[1], y - h)
        bb[2], bb[3] = max(bb[2], x + w), max(bb[3], y + h)

    def outward(name):
        x, y = pos[name]
        if abs(x) < 1e-6 and abs(y) < 1e-6:
            return -math.pi / 2
        return math.atan2(y, x)

    for s in states:
        cx, cy = pos[s.name]
        hw, hh = size[s.name]
        svg.rect(cx - hw, cy - hh, 2 * hw, 2 * hh, fill=FILL_FIXED if s.name == init else FILL_A, stroke=INK, sw=1.8, rx=12)
        if s.out:
            svg.text(cx, cy - 2, s.name, 14, bold=True)
            svg.text(cx, cy + 15, str(s.out), 10.5, mono=True, fill=GRAY_TXT)
        else:
            svg.text(cx, cy + 5, s.name, 14, bold=True)
        grow(cx, cy, hw, hh)

    def put_lines(x, y, lines, anchor="middle", up=True):
        for i, l in enumerate(lines):
            yy = y - (len(lines) - 1 - i) * 14 if up else y + i * 14
            svg.text(x, yy, l, 11, anchor, halo=True)
            tw_ = tw(l, 11)
            grow(x + (tw_ / 2 if anchor == "start" else -tw_ / 2 if anchor == "end" else 0), yy, tw_ / 2, 8)

    groups = {}
    for t in trans:
        groups.setdefault((t.a, t.b), []).append(t)
    loops = {a for (a, b) in groups if a == b}
    for (a, b), ts in groups.items():
        lines = [label_of(t) for t in ts if label_of(t)]
        ax, ay = pos[a]
        bx, by = pos[b]
        if a == b:
            hw, hh = size[a]
            th = outward(a)
            ca, sa = math.cos(th), math.sin(th)
            p1 = _clip(ax, ay, hw + 1, hh + 1, ax + math.cos(th - 0.42) * 100, ay + math.sin(th - 0.42) * 100)
            p2 = _clip(ax, ay, hw + 3, hh + 3, ax + math.cos(th + 0.42) * 100, ay + math.sin(th + 0.42) * 100)
            k = 62
            svg.path(f"M{n(p1[0])} {n(p1[1])} C{n(p1[0] + ca * k)} {n(p1[1] + sa * k)} {n(p2[0] + ca * k)} {n(p2[1] + sa * k)} {n(p2[0])} {n(p2[1])}", marker=True, sw=1.6)
            bxy = _clip(ax, ay, hw, hh, ax + ca * 100, ay + sa * 100)
            lx, ly = bxy[0] + ca * 58, bxy[1] + sa * 58
            if ca > 0.4:
                put_lines(lx + 4, ly + 4, lines, "start", up=sa < 0.4)
            elif ca < -0.4:
                put_lines(lx - 4, ly + 4, lines, "end", up=sa < 0.4)
            else:
                put_lines(lx, ly if sa < 0 else ly + 10, lines, "middle", up=sa < 0)
            grow(lx, ly, 10, 10)
            continue
        mx, my = (ax + bx) / 2, (ay + by) / 2
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1
        px, py = -dy / L, dx / L
        curved = (b, a) in groups
        cv = 42 if curved else 0
        cx_, cy_ = mx + px * cv, my + py * cv
        s0 = _clip(ax, ay, size[a][0] + 2, size[a][1] + 2, cx_, cy_)
        e0 = _clip(bx, by, size[b][0] + 3, size[b][1] + 3, cx_, cy_)
        svg.path(f"M{n(s0[0])} {n(s0[1])} Q{n(cx_)} {n(cy_)} {n(e0[0])} {n(e0[1])}", marker=True, sw=1.6)
        lx, ly = 0.25 * s0[0] + 0.5 * cx_ + 0.25 * e0[0], 0.25 * s0[1] + 0.5 * cy_ + 0.25 * e0[1]
        ox, oy = px * 13, py * 13
        if not curved and oy > 0:
            ox, oy = -ox, -oy
        put_lines(lx + ox, ly + oy, lines)
        grow(cx_, cy_)
    # начальный маркер: наружу от центра; если у состояния есть петля — со смещением
    ix, iy = pos[init]
    th = outward(init) if N > 1 else math.pi
    if init in loops:
        th += 1.15
    ux, uy = math.cos(th), math.sin(th)
    hw, hh = size[init]
    ex, ey = _clip(ix, iy, hw + 3, hh + 3, ix + ux * 100, iy + uy * 100)
    dx_, dy_ = ex + ux * 40, ey + uy * 40
    svg.circle(dx_, dy_, 5, fill=INK)
    svg.path(f"M{n(dx_)} {n(dy_)} L{n(ex)} {n(ey)}", marker=True, sw=1.6)
    grow(dx_, dy_, 8, 8)
    pad = 36
    dx0, dy0 = -bb[0] + pad, -bb[1] + pad + 78
    inner = f'<g transform="translate({n(dx0)},{n(dy0)})">\n{svg.inner()}\n</g>'
    return svg_doc(bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad + 78, spec.get("title", spec["name"]),
                   spec.get("subtitle", f"{N} states · {len(trans)} transitions"), inner)


def t_fsm(spec, P):
    if "_states" not in spec:
        return None
    md = md_table(["State", "Output", "Description"],
                  [[f'<a id="{anchor_id(s.name)}"></a>**{s.name}**' + (" (initial)" if s.name == spec["_init"] else ""), s.out, s.desc] for s in spec["_states"]])
    md += "\n" + md_table(["From", "To", "Condition", "Action"], [[t.a, t.b, t.when, t.do] for t in spec["_trans"]])
    return md + notes_md(spec)


def a_fsm(spec):
    return {s.name for s in spec.get("_states", [])}


# =============================================================================
#  KIND: pins
# =============================================================================
def v_pins(spec, P):
    where = W_(spec)
    check_keys(spec, BASE_KEYS + ["pins", "symbol"], where, P)
    pins, seen = [], set()
    for p in as_list(spec.get("pins")):
        if not isinstance(p, dict) or "name" not in p:
            P.diag.err(where, f"pin needs 'name': {p!r}")
            continue
        check_keys(p, ["name", "dir", "width", "description", "group", "active_low", "pin"], f"{where} pin '{p['name']}'", P, "pin key")
        d = str(p.get("dir", "in")).lower()
        if d not in ("in", "out", "inout", "pwr", "gnd", "nc"):
            P.diag.err(where, f"pin '{p['name']}': dir must be in | out | inout | pwr | gnd | nc")
            d = "in"
        if str(p["name"]) in seen:
            P.diag.err(where, f"duplicate pin '{p['name']}'")
        seen.add(str(p["name"]))
        pins.append(NS(name=str(p["name"]), dir=d, width=as_int(p.get("width")) or 1, desc=p.get("description"),
                       group=p.get("group"), low=bool(p.get("active_low")), pin=p.get("pin")))
    if not pins:
        P.diag.err(where, "'pins' must be non-empty")
        return
    spec["_pins"] = pins


def _pname(p):
    return p.name + (f"[{p.width - 1}:0]" if p.width > 1 else "")


def d_pins(spec, P):
    if "_pins" not in spec:
        return None
    pins = spec["_pins"]
    left = [p for p in pins if p.dir == "in"]
    right = [p for p in pins if p.dir != "in"]
    pitch = 38
    rows = max(len(left), len(right))
    bh = rows * pitch + 36
    lw = max([0] + [tw(_pname(p), 13, mono=True) for p in left])
    rw = max([0] + [tw(_pname(p), 13, mono=True) for p in right])
    ctr = spec.get("symbol", spec["name"])
    bw = max(220, lw + rw + 60, tw(ctr, 15, bold=True) + 40)
    stub = 54
    x0 = 32 + stub + 60
    y0 = 96
    svg = Svg()
    svg.rect(x0, y0, bw, bh, fill=FILL_A, stroke=INK, sw=2)
    svg.text(x0 + bw / 2, y0 + bh / 2 + 5, ctr, 15, bold=True, fill="#888888")

    def draw(p, i, side):
        y = y0 + 28 + i * pitch
        xs, xe = (x0 - stub, x0) if side == "L" else (x0 + bw, x0 + bw + stub)
        svg.line(xs, y, xe, y, INK, 1.8)
        # стрелки направления
        mid = (xs + xe) / 2
        sgn = 1 if (side == "L") == (p.dir != "out") else -1
        if p.dir == "inout":
            svg.path(f"M{n(mid - 6)} {n(y)} L{n(mid - 1)} {n(y - 4)} M{n(mid - 6)} {n(y)} L{n(mid - 1)} {n(y + 4)} M{n(mid + 6)} {n(y)} L{n(mid + 1)} {n(y - 4)} M{n(mid + 6)} {n(y)} L{n(mid + 1)} {n(y + 4)}", sw=1.3)
        else:
            tip = mid + 6 * sgn
            svg.path(f"M{n(tip)} {n(y)} L{n(tip - 7 * sgn)} {n(y - 4.5)} L{n(tip - 7 * sgn)} {n(y + 4.5)} Z", fill=INK, sw=1)
        if p.width > 1:
            sx = xs + (xe - xs) * 0.25
            svg.line(sx - 3, y + 5, sx + 3, y - 5, INK, 1.3)
            svg.text(sx, y - 8, str(p.width), 10, mono=True, fill=GRAY_TXT)
        if p.pin is not None:
            svg.text(xs + (4 if side == "L" else -4), y + 15, str(p.pin), 9.5, "start" if side == "L" else "end", mono=True, fill=GRAY_TXT)
        tx = x0 + 10 if side == "L" else x0 + bw - 10
        svg.text(tx, y + 4, _pname(p), 13, "start" if side == "L" else "end", mono=True, bold=True, over=p.low)

    for i, p in enumerate(left):
        draw(p, i, "L")
    for i, p in enumerate(right):
        draw(p, i, "R")
    return svg_doc(x0 + bw + stub + 40, y0 + bh + 30, spec.get("title", spec["name"]), spec.get("subtitle", f"{len(pins)} signals"), svg.inner())


def t_pins(spec, P):
    if "_pins" not in spec:
        return None
    pins = spec["_pins"]
    hg = any(p.group for p in pins)
    hp = any(p.pin is not None for p in pins)
    hd = ["Name"] + (["Pin"] if hp else []) + ["Dir", "Width"] + (["Group"] if hg else []) + ["Description"]
    rows = []
    for p in pins:
        nm = ("~" if p.low else "") + p.name
        row = [f'<a id="{anchor_id(p.name)}"></a>**{nm}**'] + ([p.pin] if hp else []) + [p.dir, p.width] + ([p.group] if hg else []) + [p.desc]
        rows.append(row)
    return md_table(hd, rows) + notes_md(spec)


def a_pins(spec):
    return {p.name for p in spec.get("_pins", [])}


# =============================================================================
#  KIND: const
# =============================================================================
def v_const(spec, P):
    where = W_(spec)
    check_keys(spec, BASE_KEYS + ["values", "radix", "width"], where, P)
    vals = spec.get("values")
    items = []
    if isinstance(vals, dict):
        items = [(str(k), v, None) for k, v in vals.items()]
    else:
        for e in as_list(vals):
            if isinstance(e, dict) and "name" in e and "value" in e:
                items.append((str(e["name"]), e["value"], e.get("description")))
            else:
                P.diag.err(where, f"bad const entry {e!r} (need name/value)")
    if not items:
        P.diag.err(where, "'values' must be a mapping or a list of {name, value}")
        return
    for k, v, d in items:
        if k in P.consts:
            P.diag.err(where, f"const '{k}' already defined")
        P.consts[k] = (v, d, spec["name"])
    spec["_items"] = items


def t_const(spec, P):
    if "_items" not in spec:
        return None
    return md_table(["Name", "Value", "Description"],
                    [[f'<a id="{anchor_id(k)}"></a>**{k}**', fmt_value(v, spec), d] for k, v, d in spec["_items"]]) + notes_md(spec)


def a_const(spec):
    return {k for k, _, _ in spec.get("_items", [])}


# =============================================================================
#  Реестр видов сущностей
# =============================================================================
KINDS = {
    "bitfield": dict(v=v_bitfield, diagram=d_bitfield, table=t_bitfield, anchors=a_bitfield, views=["diagram", "table"]),
    "enum":     dict(v=v_enum, diagram=None, table=t_enum, anchors=a_enum, views=["table"]),
    "encoding": dict(v=v_encoding, diagram=d_encoding, table=t_encoding, anchors=a_encoding, views=["diagram", "table"]),
    "regmap":   dict(v=v_regmap, diagram=d_regmap, table=t_regmap, anchors=a_regmap, views=["table"]),
    "memmap":   dict(v=v_memmap, diagram=d_memmap, table=t_memmap, anchors=a_memmap, views=["diagram", "table"]),
    "timing":   dict(v=v_timing, diagram=d_timing, table=None, anchors=a_timing, views=["diagram"]),
    "fsm":      dict(v=v_fsm, diagram=d_fsm, table=t_fsm, anchors=a_fsm, views=["diagram", "table"]),
    "pins":     dict(v=v_pins, diagram=d_pins, table=t_pins, anchors=a_pins, views=["diagram", "table"]),
    "const":    dict(v=v_const, diagram=None, table=t_const, anchors=a_const, views=["table"]),
}


# =============================================================================
#  Совместимость со старым форматом (code_list, output: [svg, md])
# =============================================================================
_RANGE_SPLIT = re.compile(r"\s*(?:\.\.\.?|\u2013|\u2014|-)\s*")


def legacy(spec, P):
    """Старый формат → новый. Предупреждения — в P.diag."""
    if "output" in spec and "view" not in spec:
        m = {"svg": "diagram", "md": "table"}
        spec["view"] = [m.get(x, x) for x in as_list(spec.pop("output"))]
    kind = spec.get("kind")
    if kind == "memspace":
        spec["kind"] = "memmap"
        regions = spec.get("regions") or []
        mx = 0
        for r in regions:
            if isinstance(r, dict) and "range" in r and "start" not in r:
                parts = _RANGE_SPLIT.split(str(r["range"]), maxsplit=1)
                lo, hi = (as_int(parts[0]), as_int(parts[1])) if len(parts) == 2 else (None, None)
                if lo is not None and hi is not None:
                    r.pop("range")
                    r["start"], r["end"] = lo, hi
            if isinstance(r, dict) and as_int(r.get("end")) is not None:
                mx = max(mx, as_int(r["end"]))
        if "width" not in spec:
            spec["width"] = max(1, mx.bit_length())
        return
    if kind != "code_list":
        return
    entries = [e for e in (spec.get("entries") or []) if isinstance(e, dict)]
    fields = spec.get("fields") or []
    if "width" in spec and any(("ref" in e or "fields" in e) for e in entries):
        spec["kind"] = "regmap"
        keys = ([fields[0]] if fields else []) + ["addr", "index", "code", "offset"]
        regs = []
        for i, e in enumerate(entries):
            off = next((e[k] for k in keys if k in e), i)
            r = {"offset": off, "name": e.get("name", "?")}
            for k in ("ref", "fields", "access", "reset", "description"):
                if k in e:
                    r[k] = e[k]
            regs.append(r)
        spec["registers"] = regs
        spec.pop("entries", None)
        spec.pop("fields", None)
        return
    spec["kind"] = "enum"
    cols = fields or ["code", "name", "description"]
    vk = cols[0]
    ne = []
    for e in entries:
        e = dict(e)
        if vk in e and vk != "value":
            e["value"] = e.pop(vk)
        e.setdefault("name", str(e.get("value")))
        ne.append(e)
    spec["entries"] = ne
    spec["columns"] = [{"key": "value", "title": str(vk).capitalize()}] + [f for f in cols[1:]]
    spec.pop("fields", None)
    if "diagram" in as_list(spec.get("view")):
        spec["view"] = [v for v in as_list(spec["view"]) if v != "diagram"] or ["table"]
        P.diag.warn(W_(spec), "svg for a plain code list is not supported any more — table only "
                    "(for a picture use kind: regmap with registers, or bitfield)")


# =============================================================================
#  Проект
# =============================================================================
class Project:
    def __init__(self, pdir):
        self.dir = pdir
        self.name = pdir.name
        self.diag = Diag()
        self.REG = {}
        self.consts = {}
        self.anchors = {}
        self.files = {}
        self.lang = "en"
        cfg = pdir / "buildex.yaml"
        if cfg.exists():
            try:
                self.lang = (yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}).get("lang", "en")
            except yaml.YAMLError as e:
                self.diag.err("buildex.yaml", str(e))
        if self.lang not in CAPTIONS:
            self.lang = "en"


def load_specs(P, spec_dir):
    items = []
    files = sorted(list(spec_dir.rglob("*.yaml")) + list(spec_dir.rglob("*.yml")))
    for yml in files:
        loader = UniqueLoader(yml.read_text(encoding="utf-8"))
        try:
            while loader.check_data():
                data = loader.get_data()
                line = loader.last_line
                if data is None:
                    continue
                if not isinstance(data, dict):
                    P.diag.err(f"{yml.name}:{line}", "document is not a mapping")
                    continue
                data["_file"], data["_line"] = yml.name, line
                items.append(data)
        except yaml.YAMLError as e:
            P.diag.err(yml.name, f"YAML: {str(e).replace(chr(10), ' ')}")
        finally:
            loader.dispose()
    return items


def views_of(spec):
    kd = KINDS[spec["kind"]]
    v = spec.get("view")
    if v is None:
        return list(kd["views"])
    return as_list(v)


# =============================================================================
#  Директивы в Markdown
# =============================================================================
DIRECTIVE = re.compile(r"\{\{\s*(?P<d>[a-z]+)\s*:\s*(?P<arg>[^{}]+?)\s*\}\}")
LEGACY_INC = re.compile(r"\[(?:include|insert)\]\((?P<lpath>[^)]+)\)")
IMG_GEN = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<path>(?:\./|(?:\.\./)+)?gen/(?P<img>[^)/\s]+)\.svg)\)")
COMBINED = re.compile(DIRECTIVE.pattern + "|" + IMG_GEN.pattern + "|" + LEGACY_INC.pattern)


MD_IMG = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
_CODE_SPANS = re.compile(r"```.*?```|`[^`\n]*`", re.S)


def check_images(text, where, md_dir, docs_in, docs_out, P):
    """Все ![](путь) должны указывать на существующие файлы (путь — от папки самого .md)."""
    for m in MD_IMG.finditer(_CODE_SPANS.sub("", text)):
        raw = m.group(1).strip()
        path = raw.split()[0].strip("<>") if raw else ""
        if not path or path.startswith(("http://", "https://", "#", "data:", "mailto:")):
            continue
        path = urllib.parse.unquote(path.split("#")[0].split("?")[0])
        if path and not ((docs_in / md_dir / path).exists() or (docs_out / md_dir / path).exists()):
            P.diag.err(where, f"image '{path}': file not found (looked in {docs_in / md_dir})")


class Ctx:
    def __init__(self, P, where, docdir, numbered=True):
        self.P, self.where, self.docdir, self.numbered = P, where, docdir, numbered
        self.count = {"figure": 0, "table": 0}

    def rel(self, target):
        return posixpath.relpath(target, self.docdir or ".")


def expand(text, ctx, stack=()):
    P = ctx.P
    # экранирование: \{{...}} и \[include](...) выводятся буквально (без обратной косой)
    text = text.replace("\\{{", "\x00L\x00").replace("\\[include]", "\x00I\x00").replace("\\[insert]", "\x00S\x00")

    def link(arg):
        name, _, fld = arg.partition(".")
        if name not in P.REG:
            m = difflib.get_close_matches(name, list(P.REG), n=1)
            P.diag.err(ctx.where, f"{{{{ref:{arg}}}}}: '{name}' not found" + (f" — did you mean '{m[0]}'?" if m else ""))
            return f"`{arg}`"
        if fld and fld not in P.anchors.get(name, set()):
            P.diag.err(ctx.where, f"{{{{ref:{arg}}}}}: '{name}' has no '{fld}'")
            return f"`{arg}`"
        url = ctx.rel(f"gen/{name}.md") + (f"#{anchor_id(fld)}" if fld else "")
        return f"[`{fld or name}`]({url})"

    def why(name, view):
        spec = P.REG.get(name)
        if spec is None:
            m = difflib.get_close_matches(name, list(P.REG), n=1)
            return (f"'{name}' is not defined in any spec file of this project" + (f" — did you mean '{m[0]}'?" if m else "")
                    + f" (loaded specs: {', '.join(sorted(P.files)) or 'none'})")
        return f"'{name}' ({spec['kind']}) has no {view}; its views: {', '.join(views_of(spec))}"

    def figure(name):
        spec = P.REG.get(name)
        if not spec or not spec.get("_has_svg"):
            P.diag.err(ctx.where, f"{{{{figure:{name}}}}}: " + why(name, "diagram"))
            return ""
        title = spec.get("title", name)
        cap = CAPTIONS[P.lang]["figure"]
        if ctx.numbered:
            ctx.count["figure"] += 1
            c = f"*{cap} {ctx.count['figure']} — {title}*"
        else:
            c = f"*{title}*"
        return f"![{title}]({ctx.rel(f'gen/{name}.svg')})\n\n{c}\n"

    def table(name):
        spec = P.REG.get(name)
        if not spec or "_table_md" not in spec:
            P.diag.err(ctx.where, f"{{{{table:{name}}}}}: " + why(name, "table"))
            return ""
        title = spec.get("title", name)
        cap = CAPTIONS[P.lang]["table"]
        if ctx.numbered:
            ctx.count["table"] += 1
            c = f"**{cap} {ctx.count['table']} — {title}**"
        else:
            c = f"**{title}**"
        return f"{c}\n\n{spec['_table_md']}"

    def repl(m):
        if m.group("lpath"):
            return legacy_repl(m)
        if m.group("img"):                       # обычная картинка ![..](gen/NAME.svg)
            name = m.group("img")
            spec = P.REG.get(name)
            if not spec or not spec.get("_has_svg"):
                P.diag.err(ctx.where, f"image {m.group('path')}: " + why(name, "diagram"))
                return m.group(0)
            if re.match(r"\n+\*", m.string[m.end():m.end() + 8]):   # подпись уже есть
                return m.group(0)
            title = spec.get("title", name)
            ctx.count["figure"] += 1 if ctx.numbered else 0
            cap = CAPTIONS[P.lang]["figure"]
            c = f"*{cap} {ctx.count['figure']} — {title}*" if ctx.numbered else f"*{title}*"
            return f"{m.group(0)}\n\n{c}"
        d, arg = m.group("d"), m.group("arg").strip()
        if d == "ref":
            return link(arg)
        if d == "figure":
            return figure(arg)
        if d == "table":
            return expand(table(arg), ctx, stack)
        if d == "auto":
            spec = P.REG.get(arg)
            if not spec:
                P.diag.err(ctx.where, f"{{{{auto:{arg}}}}}: " + why(arg, "view"))
                return ""
            parts = []
            if spec.get("_has_svg"):
                parts.append(figure(arg))
            if "_table_md" in spec:
                parts.append(expand(table(arg), ctx, stack))
            return "\n".join(parts)
        if d == "const":
            if arg not in P.consts:
                P.diag.err(ctx.where, f"const '{arg}' not found")
                return arg
            return str(P.consts[arg][0])
        if d == "include":
            p = (P.dir / "docs" / arg)
            if not p.exists():
                P.diag.err(ctx.where, f"include '{arg}': file not found (looked for {p})")
                return ""
            rp = p.resolve()
            if rp in stack:
                P.diag.err(ctx.where, f"include cycle at '{arg}'")
                return ""
            return expand(p.read_text(encoding="utf-8"), ctx, stack + (rp,))
        P.diag.err(ctx.where, f"unknown directive '{{{{{d}:...}}}}'")
        return m.group(0)

    def legacy_repl(m):
        rel = m.group("lpath")
        rel = rel[2:] if rel.startswith("./") else rel
        if rel.startswith("gen/"):
            rel = rel[4:]
        if rel.endswith("-table.md"):
            return expand("{{" + "table:" + rel[:-9] + "}}", ctx, stack)
        if rel.endswith(".md") and "_table_md" in P.REG.get(rel[:-3], {}):
            return expand("{{" + "table:" + rel[:-3] + "}}", ctx, stack)
        if rel.endswith(".svg"):
            return expand("{{" + "figure:" + rel[:-4] + "}}", ctx, stack)
        return expand("{{" + "include:" + rel + "}}", ctx, stack)

    out = COMBINED.sub(repl, text)
    if not stack:
        out = out.replace("\x00L\x00", "{{").replace("\x00I\x00", "[include]").replace("\x00S\x00", "[insert]")
    return out


# =============================================================================
#  Сборка проекта
# =============================================================================
def build_project(pdir):
    P = Project(pdir)
    print(f"\n=== {P.name} ===  (buildex {VERSION}, {Path(__file__).resolve()})")
    spec_dir, docs_dir = pdir / "spec", pdir / "docs"
    out_docs = OUT / P.name / "docs"
    gen_src = docs_dir / "gen"          # сгенерированное лежит рядом с исходником
    gen_out = out_docs / "gen"
    imgs_in, imgs_out = docs_dir / "images", out_docs / "images"
    produced = set()                    # все файлы, которые должны остаться (и в src/gen, и в out/)

    def emit_pair(rel_name, content):
        write_if_changed(gen_src / rel_name, content, produced)
        write_if_changed(gen_out / rel_name, content, produced)

    # 1. загрузка
    items = load_specs(P, spec_dir) if spec_dir.exists() else []
    for it in items:
        P.files[it["_file"]] = P.files.get(it["_file"], 0) + 1
    print(f"  specs: " + (", ".join(f"{f} ({c})" for f, c in sorted(P.files.items())) or f"none found in {spec_dir}"))
    print(f"  output: {out_docs}  (gen/ inside)")
    for s in items:
        legacy(s, P)
        nm, kd = s.get("name"), s.get("kind")
        if not nm:
            P.diag.err(f"{s['_file']}:{s['_line']}", "document without 'name'")
            continue
        if kd not in KINDS:
            m = difflib.get_close_matches(str(kd), list(KINDS), n=1)
            P.diag.err(W_(s), f"unknown kind '{kd}'" + (f" — did you mean '{m[0]}'?" if m else f" (known: {', '.join(KINDS)})"))
            continue
        nm = s["name"] = str(nm)
        if nm in P.REG:
            P.diag.err(W_(s), f"duplicate name (already in {P.REG[nm]['_file']}:{P.REG[nm]['_line']})")
            continue
        P.REG[nm] = s

    # 2. валидация
    for s in P.REG.values():
        KINDS[s["kind"]]["v"](s, P)
        for v in views_of(s):
            if v not in ("diagram", "table"):
                P.diag.err(W_(s), f"unknown view '{v}' (diagram | table)")
            elif KINDS[s["kind"]][v] is None:
                P.diag.err(W_(s), f"kind '{s['kind']}' has no '{v}' view")
        P.anchors[s["name"]] = KINDS[s["kind"]]["anchors"](s)

    # 3. генерация сущностей
    if not P.diag.errors:
        for nm, s in sorted(P.REG.items()):
            kd = KINDS[s["kind"]]
            vs = views_of(s)
            print(f"  render: {nm} ({s['kind']}) [{', '.join(vs)}]")
            svg = kd["diagram"](s, P) if "diagram" in vs else None
            tbl = kd["table"](s, P) if "table" in vs else None
            if "diagram" in vs and svg is None:
                P.diag.err(W_(s), "diagram could not be generated")
            if svg:
                s["_has_svg"] = True
                emit_pair(f"{nm}.svg", svg)
            if tbl is not None:
                s["_table_md"] = tbl
    if P.diag.errors:
        P.diag.report()
        return False

    # NAME.md — таблица (или рисунок, если таблицы нет); index.md — список всего
    gctx = Ctx(P, "gen", "gen", numbered=False)
    for nm, s_ in sorted(P.REG.items()):
        gctx.where = f"gen/{nm}.md"
        title = s_.get("title", nm)
        body = s_["_table_md"] if "_table_md" in s_ else f"![{title}]({nm}.svg)\n"
        emit_pair(f"{nm}.md", expand(f"**{title}**\n\n{body}", gctx))
    idx = "# Specification index\n\n"
    for kd in KINDS:
        group = [(nm, s_) for nm, s_ in sorted(P.REG.items()) if s_["kind"] == kd]
        if group:
            idx += f"## {kd}\n\n" + "".join(f"- [{s_.get('title', nm)}]({nm}.md) — `{nm}`\n" for nm, s_ in group) + "\n"
    emit_pair("index.md", idx)
    # зеркалим images -> out/docs/images (по md5)
    sync_tree(imgs_in, imgs_out, produced)

    # 4. документы
    if docs_dir.exists():
        for f in sorted(docs_dir.rglob("*")):
            if not f.is_file():
                continue
            rel = f.relative_to(docs_dir)
            if rel.parts[0] in ("gen", "images"):
                continue
            if f.suffix.lower() == ".md":
                ctx = Ctx(P, f"docs/{rel.as_posix()}", rel.parent.as_posix() if str(rel.parent) != "." else "")
                expanded = expand(f.read_text(encoding="utf-8"), ctx)
                check_images(expanded, ctx.where, rel.parent, docs_dir, out_docs, P)
                write_if_changed(out_docs / rel, expanded, produced)
            else:
                smart_copy(f, out_docs / rel, produced)

    # 5. вычистить устаревшее: в src/.../gen и во всём out/.../docs
    for root, label in ((gen_src, "src gen/"), (out_docs, "")):
        if not root.exists():
            continue
        for f in list(root.rglob("*")):
            if f.is_file() and f.resolve() not in produced:
                f.unlink()
                print(f"  🧹 removed stale {label}{f.relative_to(root).as_posix()}")
        for d in sorted([x for x in root.rglob("*") if x.is_dir()], reverse=True):
            if not any(d.iterdir()):
                d.rmdir()

    P.diag.report()
    ok = not P.diag.errors
    print(f"  {'✅' if ok else '❌'} {len(P.REG)} entities, {len(P.diag.warnings)} warning(s), {len(P.diag.errors)} error(s)")
    return ok


def deploy():
    if not OUT.exists():
        print("❌ No out/ directory. Run build first.")
        return
    dst = ROOT / "docs"
    dst.mkdir(parents=True, exist_ok=True)
    print(f"📦 Syncing {OUT} -> {dst}...")
    sync_tree(OUT, dst, set())
    for f in list(dst.rglob("*")):          # убрать то, чего нет в out/
        if f.is_file() and not (OUT / f.relative_to(dst)).exists():
            f.unlink()
    for d in sorted([x for x in dst.rglob("*") if x.is_dir()], reverse=True):
        if not any(d.iterdir()):
            d.rmdir()
    print(f"✅ Deployed to {dst}")


def ensure_gitignore():
    want = ["out/", "src/*/docs/gen/"]
    gi = ROOT / ".gitignore"
    if not gi.exists():
        gi.write_text("\n".join(want) + "\n", encoding="utf-8")
        print("  created .gitignore (out/, src/*/docs/gen/)")
        return
    have = {ln.strip() for ln in gi.read_text(encoding="utf-8").splitlines()}
    miss = [w for w in want if w not in have]
    if miss:
        print(f"  💡 add to .gitignore: {', '.join(miss)}")


def build_all(projects):
    if not SRC.exists():
        print("No src/ directory")
        return False
    ensure_gitignore()
    ok = True
    for pdir in sorted(SRC.iterdir()):
        if pdir.is_dir() and (not projects or pdir.name in projects):
            ok &= build_project(pdir)
    print("\nDone." if ok else "\nDone with errors.")
    return ok


def snapshot():
    mt = 0.0
    for p in list(SRC.rglob("*")) + [Path(__file__)]:
        try:
            mt = max(mt, p.stat().st_mtime)
        except OSError:
            pass
    return mt


# =============================================================================
#  explain / new
# =============================================================================
HELP = {
    "bitfield": ("Регистр или слово: набор полей. Поддерживает extends (наследование), fixed (константы), split (разбивка на строки).",
"""kind: bitfield
name: NAME
title: "Control register"
width: 32
fields:
  - {name: EN,   bit: 0,      access: rw, reset: 0, description: "Enable"}
  - {name: MODE, bits: [3,1], access: rw, reset: 0, enum: NAME_modes, description: "Mode"}
  - {name: RSV,  bits: [31,4], reserved: true}"""),
    "enum": ("Таблица кодов. value+name обязательны, остальные ключи становятся колонками. Диапазоны: '14..31'.",
"""kind: enum
name: NAME
title: "Operation codes"
width: 3        # необязательно: проверка, что значения влезают; нужна для radix: bin/hex
radix: dec      # dec | hex | bin
entries:
  - {value: 0, name: NOP, description: "Nothing"}
  - {value: 1, name: ADD, description: "d = d + s"}
  - {value: "2..7", name: reserved}"""),
    "encoding": ("Семейство форматов слова: общие поля (common) + варианты (variants) с селекторами (when).",
"""kind: encoding
name: NAME
title: "Instruction formats"
width: 16
common:
  - {name: OPC, bits: [15,14], description: "Format selector"}
variants:
  - name: alu
    when: {OPC: 0}
    fields:
      - {name: RD, bits: [13,10]}
      - {name: IMM, bits: [9,0], description: "Immediate"}
  - name: jmp
    when: {OPC: 1}
    fields:
      - {name: ADDR, bits: [13,0]}"""),
    "regmap": ("Регистры по смещениям. Поля — inline (fields) или ссылкой (ref) на bitfield. view: [diagram, table] включает диаграмму.",
"""kind: regmap
name: NAME
title: "Registers"
width: 32
registers:
  - {offset: 0x00, name: CTRL, access: rw, reset: 0, description: "Control", fields: [{name: EN, bit: 0}, {name: RSV, bits: [31,1], reserved: true}]}
  - {offset: 0x04, name: STATUS, access: ro, description: "Status", fields: [{name: BUSY, bit: 0}, {name: RSV, bits: [31,1], reserved: true}]}"""),
    "memmap": ("Адресное пространство. Регион: start + (end | size). Пересечения — ошибка, дыры рисуются как 'unmapped'.",
"""kind: memmap
name: NAME
title: "Memory map"
width: 16
regions:
  - {name: ROM,  start: 0x0000, size: 0x4000, access: ro, purpose: "Boot code", group: mem}
  - {name: RAM,  start: 0x8000, size: 0x2000, access: rw, group: mem}
  - {name: IO,   start: 0xF000, end: 0xF0FF, access: rw, purpose: "Peripherals"}"""),
    "timing": ("Временная диаграмма. wave: p n (такт) 0 1 (уровни) = (шина, подпись из data) x z . (продолжение). arrows — стрелки зависимостей.",
"""kind: timing
name: NAME
title: "Write cycle"
signals:
  - {name: CLK,  wave: "p......."}
  - {name: CS,   wave: "10....1."}
  - {name: ADDR, wave: "x=.....x", data: ["A0"]}
  - {name: DATA, wave: "x.==..x.", data: ["D0", "D1"]}
arrows:
  - {from: [CS, 1], to: [DATA, 2], text: "t_su"}"""),
    "fsm": ("Конечный автомат. Переходы: from, to, when, do. Недостижимые состояния и неизвестные имена ловятся валидатором.",
"""kind: fsm
name: NAME
title: "Controller FSM"
initial: IDLE
states:
  - {name: IDLE, output: "busy=0"}
  - {name: RUN,  output: "busy=1"}
  - {name: DONE}
transitions:
  - {from: IDLE, to: RUN,  when: "start", do: "load"}
  - {from: RUN,  to: RUN,  when: "!last"}
  - {from: RUN,  to: DONE, when: "last"}
  - {from: DONE, to: IDLE}"""),
    "pins": ("Сигналы и выводы: символ-блок + таблица. dir: in | out | inout; width; active_low; pin; group.",
"""kind: pins
name: NAME
title: "Pinout"
symbol: CHIP
pins:
  - {name: CLK,  dir: in}
  - {name: RST,  dir: in, active_low: true}
  - {name: A,    dir: in,  width: 16, description: "Address"}
  - {name: D,    dir: inout, width: 8, description: "Data"}
  - {name: IRQ,  dir: out, description: "Interrupt"}"""),
    "const": ("Именованные константы; в тексте — {{const:NAME}}.",
"""kind: const
name: NAME
title: "Constants"
values:
  PAGE_SIZE: 256
  BOOT_ADDR: 0x0000"""),
}


def cmd_kinds():
    for k, (d, _) in HELP.items():
        print(f"  {k:<9} {d}")


def cmd_explain(kind):
    if kind not in HELP:
        print(f"unknown kind '{kind}'. Known: {', '.join(HELP)}")
        return 1
    d, ex = HELP[kind]
    print(f"{kind}: {d}\n\nПример:\n\n{ex}\n\nВиды по умолчанию: {', '.join(KINDS[kind]['views'])} (переопределить: view: [diagram, table])")
    return 0


def cmd_new(kind, name):
    if kind not in HELP:
        print(f"unknown kind '{kind}'. Known: {', '.join(HELP)}", file=sys.stderr)
        return 1
    print(HELP[kind][1].replace("NAME", name))
    return 0


# =============================================================================
def main(argv=None):
    ap = argparse.ArgumentParser(prog="buildex.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    b = sub.add_parser("build", help="собрать проекты")
    b.add_argument("projects", nargs="*")
    b.add_argument("--deploy", action="store_true", help="после сборки скопировать out/ в docs/")
    b.add_argument("--watch", action="store_true", help="пересобирать при изменении файлов")
    sub.add_parser("kinds", help="список сущностей")
    e = sub.add_parser("explain", help="схема и пример для сущности")
    e.add_argument("kind")
    nw = sub.add_parser("new", help="заготовка YAML")
    nw.add_argument("kind")
    nw.add_argument("name")
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in ("build", "kinds", "explain", "new", "-h", "--help"):
        argv = ["build"] + argv
    a = ap.parse_args(argv)
    if a.cmd == "kinds":
        cmd_kinds()
        return 0
    if a.cmd == "explain":
        return cmd_explain(a.kind)
    if a.cmd == "new":
        return cmd_new(a.kind, a.name)
    ok = build_all(a.projects)
    if a.watch:
        print("👀 watching (Ctrl+C to stop)...")
        last = snapshot()
        try:
            while True:
                time.sleep(0.7)
                cur = snapshot()
                if cur != last:
                    last = cur
                    ok = build_all(a.projects)
        except KeyboardInterrupt:
            pass
    if a.deploy and ok:
        deploy()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())