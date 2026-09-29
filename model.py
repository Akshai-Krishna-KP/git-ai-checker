import ollama
import json

def review_code(diff_text: str):
    system_prompt = """
    You are a senior code reviewer and security expert. Analyze the provided git diff.
    Return ONLY a JSON object with this exact structure:
    {
        "has_critical_issues": true/false,
        "summary": "Short 1-line summary of changes",
        "findings": [
            {
                "severity": "CRITICAL" | "WARNING" | "INFO",
                "file": "filename",
                "message": "Description of issue or fix recommendation"
            }
        ]
    }
    Rules:
    1. Set has_critical_issues to true ONLY if there are exposed secrets, security risks, syntax errors, or major bugs.
    2. Keep findings concise and actionable.
    """

    response = ollama.chat(
        model="qwen2.5-coder:3b",
        format="json",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Git Diff to review:\n{diff_text}"}
        ]
    )
    return json.loads(response['message']['content'])