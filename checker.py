from email import message
import subprocess
import sys
import json
import ollama
from rich.console import Console
from rich.panel import Panel

console = Console()

def get_git_diff():
    """
    Retrive staged changes using subprocess
    """
    result = subprocess.run(
        ["git", "diff", "--cached"], capture_output=True, text=True, check=False 
    )
    return result.stdout.strip()

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

if __name__ == "__main__":
    # Get the Git diff 
    diff = get_git_diff()
    if not diff:
        console.print("[yellow]No Staged changed to review.[/yellow]")
        sys.exit(0)

    # Initiate the process 
    console.print("[cyan]Local AI reviewing staged changes....[/cyan]")

    try:
        review = review_code(diff)
    except Exception as e:
        console.print(f"[bold red]Failed to get AI review:[/bold red] {e}")
        sys.exit(1)

    # Show the review report
    console.print(Panel(f"[bold]{review.get('summary', 'Code Review')}[/bold]", title="AI Summary"))

    for item in review.get("findings", []):
        severity = item.get("severity", "INFO")
        file_name = item.get("file", "Unknown File")
        message = item.get("message", "No message provided")

        color = "red" if severity == "CRITICAL" else "yellow" if severity == "WARNING" else "blue"
        console.print(f"[{color}]-[{severity}] {file_name}: {message}[/{color}]")

    # Abort the commit if a critical issue is found
    if review.get("has_critical_issues"):
        console.print("\n[bold red]Commit aborted due to CRITICAL issues[/bold red]")
        sys.exit(1)

    # Approve the commit if everything is okay
    console.print("\n[bold green] AI Review passed. Proceeding with commit.[/bold green]")
    sys.exit(0)
