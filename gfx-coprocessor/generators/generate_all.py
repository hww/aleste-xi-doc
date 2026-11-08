import sys
import runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(script, *args):
    """Run a generator in-process with its own argv and module namespace."""
    sys.argv = [str(HERE / script), *args]
    runpy.run_path(str(HERE / script), run_name="__main__")


def main():
    run("register_map.py")
    run("bitfields.py", "microinstruction")
    run("bitfields.py", "mode")
    run("operand_map.py")
    run("architecture.py")  
    run("algorithms.py")  
    run("alu_map.py")
    print("\nAll diagrams generated in output/")


if __name__ == "__main__":
    main()