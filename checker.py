import sys
from rich.console import Console
from rich.panel import Panel

# User modules
import gitdiff as gd
import model

console = Console()

if __name__ == "__main__":
    # Get the Git diff 
    diff = gd.get_git_diff()
    if not diff:
        console.print("[yellow]No Staged changed to review.[/yellow]")
        sys.exit(0)

    # Initiate the process 
    console.print("[cyan]Local AI reviewing staged changes....[/cyan]")

    try:
        review = model.review_code(diff)
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
