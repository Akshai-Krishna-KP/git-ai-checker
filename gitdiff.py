import subprocess

def get_git_diff():
    """
    Retrive staged changes using subprocess
    """
    result = subprocess.run(
        ["git", "diff", "--cached"], capture_output=True, text=True, check=False
    )
    return result.stdout.strip()