import sys
import runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent

def run(script, *args):
    sys.argv = [str(HERE / script), *args]
    runpy.run_path(str(HERE / script), run_name="__main__")

def main():
    print("1. Generating SVG bitfields...")
    run("bitfields.py", "microinstruction")
    run("bitfields.py", "mode")
    
    print("\n2. Generating Markdown tables...")
    run("md_tables.py")
    
    print("\n3. Generating Timing diagrams...")
    run("timing.py")
    
    print("\n4. Generating Algorithms (Graphviz)...")
    run("algorithms.py")
    
    print("\n5. Assembling documents...")
    run("preprocessor.py")
    
    print("\n✅ Build complete! Check doc/ folder.")

if __name__ == "__main__":
    main()