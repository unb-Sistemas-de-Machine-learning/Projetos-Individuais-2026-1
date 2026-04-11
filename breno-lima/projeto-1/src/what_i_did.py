import subprocess
from models import ModelFactory


model = ModelFactory("gemini").create_model()


def __get_git_diff() -> str:
    result = subprocess.run(
        args=["git", "diff", "--staged"], capture_output=True, text=True
    )

    if result.returncode != 0:
        raise Exception(f"Error running git diff: {result.stderr}")

    return result.stdout


def limit_diff_lines(diff: str, max_lines: int = 100) -> str:
    lines = diff.splitlines()
    if len(lines) > max_lines:
        return "\n".join(lines[:max_lines]) + "\n... (truncated)"
    return diff


def limit_diff_size(diff: str, max_size: int = 8000) -> str:
    if len(diff) > max_size:
        return diff[:max_size] + "\n... (truncated)"
    return diff


def what_i_did():
    diff = __get_git_diff()

    diff = limit_diff_lines(diff)
    diff = limit_diff_size(diff)

    mensage = model.prompt_diff(diff)
    if mensage is None:
        print("No message generated.")
        return
    subprocess.run(
        [
            "git",
            "commit",
            "-e",
            "-m",
            mensage,
        ]
    )
