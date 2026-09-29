import ollama
import json
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
import sys

console = Console()
CONFIG_DIR = Path.home() / ".config" / "git-ai-checker"
CONFIG_FILE = CONFIG_DIR / "config.json"
MODEL_LIST = ["qwen2.5-coder:3b", "qwen3.5:9b", "gpt-oss:20b"]

def review_code(diff_text: str, model_name: str = "qwen2.5-coder:3b"):
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
        model=model_name,
        format="json",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Git Diff to review:\n{diff_text}"}
        ]
    )
    content = response['message']['content'].strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    return json.loads(content)

def model_install(model_selected: str):
    """
    Check if model is installed or not.
    If not, pull it with progress status
    :param model_selected:
    :return:
    """

    try:
        # Get the list of installed models
        model = ollama.list()
        installed_models = [
            m.model for m in model.models
        ]

        # Check if the model is already installed
        is_installed = any(
            m == model_selected or m.startswith(f"{model_selected}:")
            for m in installed_models
        )

        # If model is not installed. Start the installation procedure
        if not is_installed:
            console.print(f"\n[yellow]Model '{model_selected}' is not installed locally. Downloading now...[/yellow]")

            current_status = ""
            with console.status(f"[bold cyan]Pulling {model_selected}...[/bold cyan]") as status:
                # Pull the model and show progress bar
                for progress in ollama.pull(model_selected, stream=True):
                    status_text = progress.get("status", "")
                    if status_text != current_status:
                        current_status = status_text
                        status.update(f"[bold cyan]Pulling {model_selected}: {current_status}[/bold cyan]")

            console.print(f"[bold green]✓ Successfully pulled {model_selected}[/bold green]\n")
    except Exception as e:
        sys.exit(
            f"Error communicating with Ollama service: {e}\n"
            "Please ensure Ollama is installed and running (`ollama serve`)."
        )

def check_model():
    """
    Check if any llm model is installed or not.
    If not, Give options and pull it
    Create a CONFIG DIR for storing that details
    :return:
    """
    # Create CONFIG_DIR if it doesn't exist
    CONFIG_DIR.mkdir(parents=True, exist_ok=True) if not CONFIG_DIR.exists() else None

    # Check and create CONFIG_FILE and get model details
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                if "model" in config:
                    return config["model"]
        except (json.JSONDecodeError, KeyError):
            # @TODO: Add a Error message in here
            pass

    # If no config file and model mentioned.
    # Show the model option and install
    console.print("\n[bold cyan]First-time Setup: Choose a local AI model[/bold cyan]")
    for idx, model in enumerate(MODEL_LIST, 1):
        console.print(f"  [bold green]{idx}[/bold green]. {model}")

    choice = Prompt.ask(
        "\nSelect a model number",
        choices=[str(i) for i in range(1, len(MODEL_LIST) + 1)],
        default="1"
    )

    # Get the model selection and install it
    model_selected = MODEL_LIST[int(choice) - 1]
    model_install(model_selected)

    # Write the model details to CONFIG_FILE
    with open(CONFIG_FILE, "w") as f:
        json.dump({"model": model_selected}, f, indent=4)

    # Show finished and return model name and param
    console.print(f"[green]Saved '{model_selected}' to {CONFIG_FILE}[/green]\n")
    return model_selected