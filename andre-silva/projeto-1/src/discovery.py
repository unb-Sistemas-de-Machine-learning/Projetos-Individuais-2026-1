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
