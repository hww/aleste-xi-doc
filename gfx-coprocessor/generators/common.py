from pathlib import Path
import html
import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "spec"
OUT = ROOT / "output"

PALETTE = {
    "destination": "#2F7564",
    "source":      "#347C91",
    "memory":      "#A56B35",
    "pixel":       "#8061A1",
    "clipping":    "#426F9D",
    "affine":      "#8A5C86",
    "temporary":   "#68717D",
    "default":     "#536779",
}

FIELD_COLORS = [
    "#365E91", "#287A65", "#368D83", "#A36B32",
    "#76569A", "#64717D", "#A04F55",
]


def load_yaml(name):
    with (SPEC / name).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def esc(value):
    return html.escape(str(value), quote=True)


def svg_start(width, height, title, subtitle=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="#F4F6F8"/>
<text x="32" y="42" style="font: 700 25px 'Inter', 'Arial', sans-serif; fill: #172B3A;">{esc(title)}</text>
<text x="32" y="65" style="font: 13px 'Inter', 'Arial', sans-serif; fill: #607080;">{esc(subtitle)}</text>
'''


def svg_end():
    return "</svg>"


def write_svg(filename, content):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / filename
    path.write_text(content + svg_end(), encoding="utf-8")
    print(f"Wrote {path}")