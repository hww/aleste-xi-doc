import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
OUT = ROOT / "output"
DOC = ROOT / "doc"

def process_file(filepath):
    text = filepath.read_text(encoding="utf-8")
    
    # Ищем паттерн [include](filename.md) или [insert](filename.md)
    pattern = r'\[(?:include|insert)\]\(([^)]+)\)'
    
    def replacer(match):
        include_filename = match.group(1)
        
        # Сначала ищем в output/ (сгенерированные таблицы и картинки)
        include_path = OUT / include_filename
        if not include_path.exists():
            # Если нет, ищем в src/
            include_path = SRC / include_filename
            
        if not include_path.exists():
            print(f"  ⚠️  Warning: File not found {include_filename}")
            return f"*[Missing file: {include_filename}]*"
            
        # Рекурсивно обрабатываем включенный файл
        return process_file(include_path)

    return re.sub(pattern, replacer, text)

def main():
    DOC.mkdir(exist_ok=True)
    
    for src_file in SRC.glob("*.md"):
        # Пропускаем сгенерированные таблицы (они не для прямого чтения)
        if src_file.name.endswith("-table.md"):
            continue
            
        print(f"Processing {src_file.name}...")
        result = process_file(src_file)
        out_path = DOC / src_file.name
        out_path.write_text(result, encoding="utf-8")
        print(f"  -> Saved to {out_path}")

if __name__ == "__main__":
    main()