import argparse
from pathlib import Path
from parser import parse_script
from executor import execute

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("script_file")
    args = parser.parse_args()
    actions = parse_script(Path(args.script_file).read_text(encoding="utf-8"))
    execute(actions)

if __name__ == "__main__":
    main()