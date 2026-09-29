import sys
import importlib.metadata
from packaging.requirements import Requirement
from packaging.version import Version

from rich.console import Console
from rich.panel import Panel

# User modules
# import gitdiff as gd
# import model

DEPENDENCIES = ["ollama>=0.1.0", "rich>=13.0.0"]
console = Console()

def pre_runner():
    """
    Pre-runner function
    This will check whether the necessary resources are present in the system.
    :return:
    """
    # Check python version
    if sys.version_info < (3, 14):
        sys.exit(
            "This script requires Python 3.14 or later."
            f"Current version is {sys.version_info}."
        )

    # Check dependencies
    errors = []
    for dep_str in DEPENDENCIES:
        req = Requirement(dep_str)
        try:
            installed_version = Version(importlib.metadata.version(req.name))
            if req.specifier and installed_version not in req.specifier:
                errors.append(
                    f"{req.name} (installed: {installed_version}, required: {dep_str})"
                )
        except importlib.metadata.PackageNotFoundError:
            errors.append(f"{dep_str} is not installed")

    # If any library not available show error message
    if errors:
        issues = "\n - ".join(errors)
        console.print(
            f"[bold red][Error]: Dependency requirements not met:\n - {issues}\n[/bold red]"
            f"Please update/install dependencies with: pip install " + " ".join(DEPENDENCIES)
        )
        sys.exit(1)

if __name__ == "__main__":
    pre_runner()    # Function to check if python module and version is correct

    # lazy import local module after checking
    import gitdiff as gd
    import model
    selected_model = model.check_model()   # Function to check model is available or not

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
