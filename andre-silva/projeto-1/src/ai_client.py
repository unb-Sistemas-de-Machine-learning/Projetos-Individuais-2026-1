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
