import subprocess
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()


def get_git_diff() -> str:
    result = subprocess.run(
        args=["git", "diff", "--staged"], capture_output=True, text=True
    )

    if result.returncode != 0:
        raise Exception(f"Error running git diff: {result.stderr}")

    return result.stdout


api_key = os.environ["API_KEY"]
if (not api_key) or api_key == "":
    raise Exception("API_KEY environment variable is not set.")


def gen_message(diff: str) -> str | None:
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        config=genai.types.GenerateContentConfig(
            system_instruction="You are a helpful assistant that summarizes git diffs into concise commit messages."
        ),
        contents=diff,
    )

    return response.text


def whatIDid():
    message = gen_message(get_git_diff())
    if message is None:
        print("No message generated.")
        return

    subprocess.run(
        [
            "git",
            "commit",
            "-e",
            "-m",
            message,
        ]
    )


whatIDid()
