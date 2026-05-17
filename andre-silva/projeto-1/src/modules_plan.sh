cat << 'EOF' > discovery.py
import subprocess
from pathlib import Path

def load_project(root):
    print("Searching for Python files in the project...")
    project_files = []
    for path in Path(root).rglob("*.py"):
        project_files.append(path)
    return project_files


def load_full_source(project_files):
    print("Loading source code:")
    data = {}
    for file in project_files:
        print("- " + str(file))
        with open(file, "r") as f:
            data[str(file)] = f.read()
    return data


def get_project_structure(root):
    print("Analyzing project structure with 'tree' command...")
    res = subprocess.run(
        ["tree", "-J", root],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return res.stdout
EOF

cat << 'EOF' > ai_client.py
import json
from google import genai

client = genai.Client()

def llm_analyze(project_data):
    print("Generating module split plan using LLM...")
    prompt = f"""
You are a senior Python software architect.

Given these Python files:

{json.dumps(project_data, indent=2)}

Split them into multiple modules.

Rules:
- Each module must have a single responsibility
- Keep behavior unchanged
- DO NOT invent new logic
- Only reorganize existing code
- Include necessary imports
- Output COMPLETE, runnable Python files

Return ONLY a bash script (NO markdown, must be directly runnable) that will apply the required modifications
"""

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
    )

    return response.text
EOF

cat << 'EOF' > main.py
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
EOF