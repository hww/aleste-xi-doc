import yaml
from pathlib import Path

data = yaml.safe_load(Path("spec/microinstruction.yaml").read_text(encoding="utf-8"))
print("Top-level keys:", list(data.keys()))
print("Fields count:", len(data.get("fields", [])))
if data.get("fields"):
    print("First field:", data["fields"][0])
    print("Keys of first field:", list(data["fields"][0].keys()))
