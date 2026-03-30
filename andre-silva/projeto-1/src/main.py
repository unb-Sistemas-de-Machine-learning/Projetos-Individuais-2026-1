import sys
from pathlib import Path
import argparse
from discovery import load_project, load_full_source, get_project_structure
from ai_client import llm_analyze

parser = argparse.ArgumentParser(description="Analyze and split a Python project into modules using an LLM.")
parser.add_argument("-r", "--root", type=str, default=".", help="Root directory of the Python project")
parser.add_argument("-o", "--output", type=str, default="modules_plan.sh", help="Output bash script filename")
parser.add_argument("-f", "--force", action="store_true", help="Force overwrite of output file if it already exists")

if __name__ == "__main__":
    try:
        print("Analyzing project structure...")
        args = parser.parse_args()
        if not Path(args.root).is_dir():
            raise ValueError(f"Provided root path '{args.root}' is not a valid directory.")
        if Path(args.output).exists() and not args.force:
            raise ValueError(f"Output file '{args.output}' already exists. Please choose a different name or remove the existing file.")

        project_data = {
            "file_structure": get_project_structure(args.root),
            "full_source": load_full_source(load_project(args.root)),
        }

        modules_script = llm_analyze(project_data)
        if modules_script is None:
            raise RuntimeError("LLM did not return a valid response")

        print("Writing module split plan to output file...")
        with open(args.output, "w") as f:
            f.write(modules_script)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        exit(1)
