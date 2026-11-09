from pathlib import Path
import html
import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "spec"
OUT = ROOT / "output"
DOC = ROOT / "doc"
SRC = ROOT / "src"

COLOR_BG = "#FFFFFF"
COLOR_TEXT = "#000000"
COLOR_GRID = "#000000"
COLOR_FILL_LIGHT = "#F2F2F2"
COLOR_FILL_MED = "#E0E0E0"

def load_yaml(name):
    with (SPEC / name).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def esc(value):
    return html.escape(str(value), quote=True)

def svg_start(width, height, title, subtitle=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="background: {COLOR_BG}; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
<text x="32" y="45" style="font: 700 24px sans-serif; fill: {COLOR_TEXT};">{esc(title)}</text>
<text x="32" y="75" style="font: 16px sans-serif; fill: #555555;">{esc(subtitle)}</text>
'''

def svg_end():
    return "</svg>"

def write_svg(filename, content):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / filename
    path.write_text(content + svg_end(), encoding="utf-8")
    print(f"Wrote {path}")

def write_md(filename, content, in_src=False):
    dir_path = SRC if in_src else OUT
    dir_path.mkdir(parents=True, exist_ok=True)
    path = dir_path / filename
    path.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")