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


def what_i_did():
    diff = __get_git_diff()
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
