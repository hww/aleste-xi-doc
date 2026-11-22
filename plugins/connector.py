"""
Плагин buildex: kind: connector — физическая раскладка разъёма (header, dip, sil).

Логика выводов (имя, направление, ширина, номера) берётся из kind: pins — единый источник правды.
Здесь описывается только геометрия: сколько рядов, как пронумерованы позиции, где ключ, как повернут рисунок.

Система координат: рисунок строится «как при rotate: 0» (ряды горизонтальны), затем целиком поворачивается
по часовой стрелке на rotate / orientation. Положение ключа (key.side) и угол pin1 задаются в этой же системе
(до поворота), поэтому при повороте ключ и первый вывод остаются на своих местах относительно корпуса.
"""
import re

HELP_TEXT = ("Физическая раскладка разъёма: header (1–2 ряда), dip, sil, edge (карточный, напр. PCIe). Номера и сигналы берутся из kind: pins.")

HELP_EXAMPLE = """kind: connector
name: NAME
title: "J1 — разъём (вид сверху)"
pins: some_pins            # имя сущности kind: pins; у выводов нужен pin: N (или список [3,4,5,6] для шины)
type: header               # header | dip | sil | edge
rows: 2                    # header: 1 или 2 (dip всегда 2, sil всегда 1)
per_row: 5                 # позиций в ряду (или count: общее число позиций)
numbering: zigzag          # zigzag | rowwise | ccw   (по умолчанию: header zigzag, dip ccw, sil rowwise)
pin1: top-left             # top-left | top-right | bottom-left | bottom-right
key: {side: bottom, kind: notch}   # side: top|bottom|left|right;  kind: notch | tab | semicircle | none
pitch: 2.54                # мм, только подпись
orientation: horizontal    # horizontal | vertical   (или rotate: 0 | 90 | 180 | 270)
labels: top                # для одного ряда: на какой стороне подписи (top | bottom)
# edge (карточный разъём): sides: [B, A], per_row: 18, gap_after: 11 (прорезь-ключ), номера в pins: «pin: B14»
# assign: {1: VCC, 2: {name: GND, dir: gnd}}   # дополнительно / вместо pins: позиция -> сигнал"""

TYPES = ("header", "dip", "sil", "edge")
SIDES = ("top", "bottom", "left", "right")
KEY_KINDS = ("notch", "tab", "semicircle", "none")
NUMBERINGS = ("zigzag", "rowwise", "ccw")
CORNERS = ("top-left", "top-right", "bottom-left", "bottom-right")

DIR_FILL = {"in": "#DCE8F6", "out": "#F6E8DC", "inout": "#EBDCF6", "power": "#F6D0D0", "gnd": "#C8C8C8", "nc": "#FFFFFF"}
DIR_TITLE = {"in": "in", "out": "out", "inout": "inout", "power": "power", "gnd": "gnd", "nc": "NC"}


def register(api):
    NS, Svg, tw, n = api.NS, api.Svg, api.tw, api.n
    math = api.math

    # ------------------------------------------------------------------ валидация
    def v_connector(spec, P):
        where = api.W_(spec)
        api.check_keys(spec, api.BASE_KEYS + ["type", "pins", "assign", "rows", "per_row", "count", "numbering",
                                              "pin1", "key", "pitch", "orientation", "rotate", "labels", "sides", "gap_after"], where, P)
        err = lambda m: P.diag.err(where, m)

        typ = spec.get("type", "header")
        if typ not in TYPES:
            err(f"type must be one of {', '.join(TYPES)}, got {typ!r}")
            return
        rows = api.as_int(spec.get("rows"))
        if typ == "dip":
            if rows not in (None, 2):
                err("dip always has 2 rows")
            rows = 2
        elif typ == "sil":
            if rows not in (None, 1):
                err("sil always has 1 row")
            rows = 1
        elif typ == "edge":
            if rows not in (None, 2):
                err("edge always has 2 sides (rows)")
            rows = 2
        else:
            rows = rows or 2
            if rows not in (1, 2):
                err("header: only rows: 1 or 2 are supported")
                return

        sides = spec.get("sides", ["B", "A"])
        if typ == "edge" and not (isinstance(sides, list) and len(sides) == 2 and len({str(x).upper() for x in sides}) == 2):
            err("sides must be a list of two different letters, e.g. [B, A] (top row first)")
            return
        sides = [str(x).upper() for x in sides] if typ == "edge" else None

        def parse_pos(raw):
            if typ == "edge":
                m = re.match(r"^([A-Za-z]+)\s*(\d+)$", str(raw).strip())
                return (m.group(1).upper(), int(m.group(2))) if m else None
            return api.as_int(raw)

        # --- сигналы: из pins и/или assign
        contacts, labels_src = {}, {}

        def pid(k):
            return k if isinstance(k, int) else f"{k[0]}{k[1]}"

        def put(pos, c, who):
            if pos in contacts:
                err(f"position {pid(pos)} is used by both '{contacts[pos].name}' and '{c.name}'")
            else:
                contacts[pos] = c

        ref = spec.get("pins")
        if ref:
            t = P.REG.get(ref)
            if t is None or t.get("kind") != "pins":
                m = api.difflib.get_close_matches(str(ref), [k for k, v in P.REG.items() if v.get("kind") == "pins"], n=1)
                err(f"pins: '{ref}' is not a 'pins' entity" + (f" — did you mean '{m[0]}'?" if m else ""))
            else:
                for p in t.get("_pins", []):
                    if p.pin is None:
                        err(f"pin '{p.name}' of '{ref}' has no 'pin:' number (add pin: N there, or use assign:)")
                        continue
                    nums = [parse_pos(x) for x in api.as_list(p.pin)]
                    if None in nums:
                        err(f"pin '{p.name}': bad pin number {p.pin!r} " + ("(expected like B14 or A3)" if typ == "edge" else "(numbers only)"))
                        continue
                    if p.width > 1 and len(nums) != p.width:
                        ex = ", ".join(str(i + 1) for i in range(p.width))
                        err(f"pin '{p.name}' is {p.width} bits wide: give {p.width} numbers, e.g. pin: [{ex}] (got {len(nums)}); "
                            f"'{p.name}' is defined in {t.get('_file')}:{t.get('_line')} (entity '{ref}')")
                        continue
                    for i, pos in enumerate(nums):
                        nm = f"{p.name}[{i}]" if p.width > 1 else p.name
                        put(pos, NS(name=nm, base=p.name, dir=p.dir, desc=p.desc, group=p.group, low=p.low), p.name)
        for pos, v in (spec.get("assign") or {}).items():
            pos = parse_pos(pos)
            if pos is None:
                err("assign: keys must be position numbers" + (" like B14" if typ == "edge" else ""))
                continue
            d = v if isinstance(v, dict) else {"name": v}
            put(pos, NS(name=str(d.get("name", "?")), base=str(d.get("name", "?")), dir=str(d.get("dir", "in")),
                        desc=d.get("description"), group=d.get("group"), low=bool(d.get("active_low"))), d.get("name"))
        if not contacts:
            err("no signals: give 'pins: <pins entity>' and/or 'assign:'")
            return

        # --- размеры
        count = api.as_int(spec.get("count"))
        per_row = api.as_int(spec.get("per_row"))
        if per_row is None:
            if typ == "edge":
                per_row = max(k[1] for k in contacts if isinstance(k, tuple))
            else:
                total = count or max(contacts)
                if total % rows:
                    total += rows - total % rows
                per_row = total // rows
        elif count is not None and count != per_row * rows:
            err(f"count {count} != rows {rows} × per_row {per_row}")
        N = rows * per_row
        if typ == "edge":
            ids = [(sd, i) for sd in sides for i in range(1, per_row + 1)]
            bad = [pid(p) for p in contacts if p not in ids]
            if bad:
                err(f"positions {sorted(bad)} outside sides {sides} × 1..{per_row}")
                return
        else:
            ids = list(range(1, N + 1))
            bad = [p for p in contacts if not 1 <= p <= N]
            if bad:
                err(f"positions {sorted(bad)} outside 1..{N} ({rows} row(s) × {per_row})")
                return
        missing = [k for k in ids if k not in contacts]
        for k in missing:
            contacts[k] = NS(name="NC", base="NC", dir="nc", desc="Not connected", group=None, low=False)
        if missing:
            P.diag.warn(where, f"positions not assigned (drawn as NC): {', '.join(str(pid(k)) for k in missing)}")
        gaps = [api.as_int(x) for x in api.as_list(spec.get("gap_after"))]
        if gaps and (typ != "edge" or None in gaps or any(not 1 <= g < per_row for g in gaps)):
            err("gap_after: only for type: edge, positions 1..per_row-1 (a key slot after that position)")
            return

        # --- нумерация, угол pin1, ключ, поворот
        numbering = spec.get("numbering", {"header": "zigzag" if rows == 2 else "rowwise", "dip": "ccw", "sil": "rowwise", "edge": "rowwise"}[typ])
        if numbering not in NUMBERINGS:
            err(f"numbering must be one of {', '.join(NUMBERINGS)}")
            return
        if numbering == "ccw" and rows != 2:
            err("numbering: ccw needs 2 rows")
            return
        pin1 = spec.get("pin1", "bottom-left" if numbering == "ccw" else "top-left")
        if pin1 not in CORNERS:
            err(f"pin1 must be one of {', '.join(CORNERS)}")
            return
        key = spec.get("key", {"side": "left", "kind": "semicircle"} if typ == "dip" else None)
        if isinstance(key, str):
            key = {"side": key, "kind": "notch"}
        if key:
            api.check_keys(key, ["side", "kind"], f"{where} key", P, "key field")
            key = NS(side=key.get("side", "left"), kind=key.get("kind", "notch"))
            if key.side not in SIDES or key.kind not in KEY_KINDS:
                err(f"key: side in {{{', '.join(SIDES)}}}, kind in {{{', '.join(KEY_KINDS)}}}")
                return
            if key.kind == "none":
                key = None
        orient, rot = spec.get("orientation"), spec.get("rotate")
        if orient is not None and rot is not None:
            err("use either 'orientation' or 'rotate', not both")
            return
        if orient is not None:
            if orient not in ("horizontal", "vertical"):
                err("orientation must be horizontal | vertical")
                return
            rot = 0 if orient == "horizontal" else 90
        elif rot is None:
            rot = 90 if typ == "dip" else 0          # DIP по умолчанию рисуется вертикально, как в даташитах
        rot = api.as_int(rot)
        if rot not in (0, 90, 180, 270):
            err("rotate must be 0, 90, 180 or 270")
            return
        lab = spec.get("labels", "top")
        if lab not in ("top", "bottom"):
            err("labels must be top | bottom")
            return

        # --- позиция -> (ряд, колонка) в системе rotate: 0
        grid = {}
        for k in ids:
            if typ == "edge":
                r, c = sides.index(k[0]), k[1] - 1
            elif numbering == "zigzag":
                r, c = (k - 1) % rows, (k - 1) // rows
            elif numbering == "rowwise":
                r, c = (k - 1) // per_row, (k - 1) % per_row
            else:
                r, c = (rows - 1, k - 1) if k <= per_row else (0, per_row - 1 - (k - per_row - 1))
            grid[k] = (r, c)
        bv, bh = ("bottom", "left") if numbering == "ccw" else ("top", "left")
        wv, wh = pin1.split("-")
        for k, (r, c) in list(grid.items()):
            grid[k] = (rows - 1 - r if wv != bv else r, per_row - 1 - c if wh != bh else c)

        spec["_c"] = NS(ids=ids, pid=pid, gaps=gaps, sides=sides, typ=typ, rows=rows, per_row=per_row, N=N, numbering=numbering, pin1=pin1, key=key, rot=rot,
                        pitch=spec.get("pitch", 2.54), labels=lab, grid=grid, contacts=contacts)

    # ------------------------------------------------------------------ геометрия
    def rot_pt(x, y, deg):
        return {0: (x, y), 90: (-y, x), 180: (-x, -y), 270: (y, -x)}[deg]       # по часовой на экране (y вниз)

    def body_poly(bw, bh, key, pitch):
        """Контур корпуса по часовой, со вставленным ключом (выемка / выступ / полукруг)."""
        edges = [("top", (-bw, -bh), (bw, -bh)), ("right", (bw, -bh), (bw, bh)),
                 ("bottom", (bw, bh), (-bw, bh)), ("left", (-bw, bh), (-bw, -bh))]
        pts = []
        for side, a, b in edges:
            pts.append(a)
            if key and key.side == side:
                ux, uy = b[0] - a[0], b[1] - a[1]
                L = math.hypot(ux, uy)
                ux, uy = ux / L, uy / L
                nx, ny = -uy, ux                                                # внутрь корпуса
                mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
                if key.kind == "semicircle":
                    r = 0.42 * pitch
                    for i in range(0, 13):
                        t = math.pi - math.pi * i / 12
                        pts.append((mx + ux * r * math.cos(t) + nx * r * math.sin(t),
                                    my + uy * r * math.cos(t) + ny * r * math.sin(t)))
                else:
                    w, d = 0.95 * pitch, 0.32 * pitch
                    sgn = 1 if key.kind == "notch" else -1
                    pts += [(mx - ux * w / 2, my - uy * w / 2),
                            (mx - ux * w / 2 + nx * d * sgn, my - uy * w / 2 + ny * d * sgn),
                            (mx + ux * w / 2 + nx * d * sgn, my + uy * w / 2 + ny * d * sgn),
                            (mx + ux * w / 2, my + uy * w / 2)]
        return pts

    def d_connector(spec, P):
        C = spec.get("_c")
        if not C:
            return None
        PT = 40.0
        rows, ncol, deg = C.rows, C.per_row, C.rot
        svg = Svg()
        bb = [1e9, 1e9, -1e9, -1e9]

        def grow(x, y, w=0.0, h=0.0):
            bb[0], bb[1] = min(bb[0], x - w), min(bb[1], y - h)
            bb[2], bb[3] = max(bb[2], x + w), max(bb[3], y + h)

        T = lambda x, y: rot_pt(x, y, deg)

        def poly(pts, fill, sw=1.6, dash=None):
            tp = [T(x, y) for x, y in pts]
            svg.poly(tp, fill=fill, sw=sw)
            for x, y in tp:
                grow(x, y)

        def rect_pts(cx, cy, w, h):
            return [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]

        xs = [c * PT + sum(1.2 * PT for g in C.gaps if c >= g) for c in range(ncol)]
        mid = (xs[0] + xs[-1]) / 2
        xs = [x - mid for x in xs]
        if C.typ == "edge":
            ys = [-0.6 * PT, 0.6 * PT]
            bw, bh = (xs[-1] - xs[0]) / 2 + 0.75 * PT, 0.6 * PT + 0.7 * PT
        elif C.typ == "dip":
            rowgap = 3.0 * PT
            ys = [-rowgap / 2 + r * rowgap for r in range(2)]
            bw, bh = ncol * PT / 2, rowgap / 2
        else:
            ys = [(r - (rows - 1) / 2) * PT for r in range(rows)]
            bw, bh = (ncol - 1) * PT / 2 + 0.75 * PT, (rows - 1) * PT / 2 + 0.75 * PT
        poly(body_poly(bw, bh, C.key, PT), "#FAFAFA", sw=2)

        def out_vec(r):
            if rows == 1:
                return (0, -1) if C.labels == "top" else (0, 1)
            return (0, -1) if r == 0 else (0, 1)

        dirs_present = []
        for g in C.gaps:                                                   # прорезь-ключ карточного разъёма
            kx = (xs[g - 1] + xs[g]) / 2
            poly(rect_pts(kx, 0, 0.5 * PT, 2 * bh), "url(#hatch)", sw=1.4)
        for k in C.ids:
            r, c = C.grid[k]
            ct = C.contacts[k]
            x, y = xs[c], ys[r]
            fill = DIR_FILL.get(ct.dir, "#FFFFFF")
            if ct.dir not in dirs_present:
                dirs_present.append(ct.dir)
            first = (k == C.ids[0]) and C.typ != "edge"
            if C.typ == "edge":
                poly(rect_pts(x, y, 0.64 * PT, 0.8 * PT), fill, sw=1.4)
                cx, cy = T(x, y)
                svg.text(cx, cy + 3.4, str(C.pid(k)), 9)
                grow(cx, cy, 13, 16)
                ox, oy = out_vec(r)
                anchor_pt = (x, (-bh if oy < 0 else bh) + oy * 7)
            elif C.typ == "dip":
                ox, oy = out_vec(r)
                ye = (-bh if oy < 0 else bh)
                poly(rect_pts(x, ye + oy * 0.2 * PT, 0.42 * PT, 0.62 * PT), fill, sw=1.4)
                tx, ty = T(x, ye - oy * 0.36 * PT)
                svg.text(tx, ty + 4, str(C.pid(k)), 10, bold=first)
                grow(tx, ty, 8, 8)
                anchor_pt = (x, ye + oy * (0.5 * PT + 6))
            else:
                cx, cy = T(x, y)
                if first:
                    poly(rect_pts(x, y, 0.72 * PT, 0.72 * PT), fill, sw=2)
                else:
                    svg.circle(cx, cy, 0.36 * PT, fill=fill, stroke="#000000", sw=1.4)
                    grow(cx, cy, 0.36 * PT, 0.36 * PT)
                svg.text(cx, cy + 3.6, str(C.pid(k)), 10, bold=first)
                ox, oy = out_vec(r)
                anchor_pt = (x, (-bh if oy < 0 else bh) + oy * 7)        # подпись — за границей корпуса
            # подпись сигнала снаружи
            ax, ay = T(*anchor_pt)
            vx, vy = rot_pt(ox, oy, deg)
            name = ct.name
            w = tw(name, 11, mono=True)
            colour = "#888888" if ct.dir == "nc" else "#000000"
            if abs(vy) > abs(vx):                                            # подпись над/под выводом
                if w <= PT - 6:
                    ty = ay - 3 if vy < 0 else ay + 11
                    svg.text(ax, ty, name, 11, mono=True, fill=colour, over=ct.low)
                    grow(ax, ty, w / 2, 8)
                else:  # длинное имя — повёрнутый текст
                    tx = ax + 4
                    ty = ay if vy < 0 else ay + w

                    svg.text(tx, ty, name, 11, "start", mono=True,
                            fill=colour, rot=-90, over=ct.low)

                    grow(tx, ty - w, 8, 0)
                    grow(tx, ty, 8, 0)
            else:                                                             # подпись слева/справа
                if vx > 0:
                    svg.text(ax, ay + 4, name, 11, "start", mono=True, fill=colour, over=ct.low)
                    grow(ax + w, ay, 0, 8)
                else:
                    svg.text(ax, ay + 4, name, 11, "end", mono=True, fill=colour, over=ct.low)
                    grow(ax - w, ay, 0, 8)
                grow(ax, ay)
        # отметка pin 1 у DIP — точка на корпусе
        if C.typ == "dip":
            r, c = C.grid[C.ids[0]]
            ox, oy = out_vec(r)
            dx, dy = T(xs[c] - 0.0 * PT, (-bh if oy < 0 else bh) - oy * 0.95 * PT)
            svg.circle(dx, dy, 4.2, fill="#000000")

        pad = 34
        top = 82
        # легенда
        legend = Svg()
        lx = 0
        for d in [x for x in ("in", "out", "inout", "power", "gnd", "nc") if x in dirs_present]:
            legend.rect(lx, 0, 14, 14, fill=DIR_FILL[d], stroke="#000000", sw=1.2, dash="3,2" if d == "nc" else None)
            legend.text(lx + 20, 12, DIR_TITLE[d], 11, "start")
            lx += 20 + tw(DIR_TITLE[d], 11) + 22
        bw_, bh_ = bb[2] - bb[0], bb[3] - bb[1]
        W = bw_ + 2 * pad
        H = bh_ + 2 * pad + top + 34
        dx0, dy0 = -bb[0] + pad, -bb[1] + pad + top
        inner = (f'<g transform="translate({n(dx0)},{n(dy0)})">\n{svg.inner()}\n</g>\n'
                 f'<g transform="translate(32,{n(H - 30)})">\n{legend.inner()}\n</g>')
        meta = f"{C.typ} · {rows}×{ncol} · pitch {C.pitch} mm" + (f" · key slot after {', '.join(map(str, C.gaps))}" if C.gaps else "") + (f" · key: {C.key.kind} ({C.key.side})" if C.key else "") + f" · rotate {deg}°"
        return api.svg_doc(max(W, 32 + lx + 32), H, spec.get("title", spec["name"]), spec.get("subtitle", meta), inner)

    # ------------------------------------------------------------------ таблица
    def t_connector(spec, P):
        C = spec.get("_c")
        if not C:
            return None
        hg = any(c.group for c in C.contacts.values())
        hd = ["Pin", "Signal", "Dir"] + (["Group"] if hg else []) + ["Description"]
        seen, rows = set(), []
        for k in C.ids:
            c = C.contacts[k]
            anchor = "" if (c.name in seen or c.dir == "nc") else f'<a id="{api.anchor_id(c.name)}"></a>'
            seen.add(c.name)
            rows.append([C.pid(k), f"{anchor}**{c.name}**", DIR_TITLE.get(c.dir, c.dir)] + ([c.group] if hg else []) + [c.desc])
        key = (f"key: {C.key.kind} on the {C.key.side} side" if C.key else ("key slot after position " + ", ".join(map(str, C.gaps)) if C.gaps else "no key"))
        head = (f"*{C.typ}, {C.rows} row(s) × {C.per_row}, pitch {C.pitch} mm, numbering {C.numbering}, "
                f"pin 1 at {C.pin1}, {key}, drawn rotated {C.rot}°*\n\n")
        return head + api.md_table(hd, rows) + api.notes_md(spec)

    def a_connector(spec):
        C = spec.get("_c")
        return {c.name for c in C.contacts.values()} if C else set()

    api.register_kind("connector", validate=v_connector, diagram=d_connector, table=t_connector, anchors=a_connector,
                      views=["diagram", "table"], order=1, help=(HELP_TEXT, HELP_EXAMPLE))
