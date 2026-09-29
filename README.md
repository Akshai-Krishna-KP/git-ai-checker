<div align="center">

# Git AI Checker

### Local AI code reviews for your staged Git changes

Review staged diffs with Ollama before they become commits.

![Python](https://img.shields.io/badge/python-3.14%2B-blue?logo=python&logoColor=white)
![AI](https://img.shields.io/badge/AI-Ollama-black?logo=ollama&logoColor=white)

</div>

---

## About

`git-ai-check` is a lightweight command-line code reviewer that checks **staged Git changes** using a locally running [Ollama](https://ollama.com/) model. It prints a concise summary and findings, then returns a failing exit status when critical issues are found.

```text
Stage changes  →  Review with Ollama  →  See findings  →  Commit or fix
```

The model runs locally, and the staged diff is sent to your local Ollama service. The project currently provides a checker script; it does not install a Git hook automatically.
> This is just a side project and Not made for professional use, at the moment.

## Installation and usage

> **Platform note:** Tested on Linux. Windows compatibility has not been verified.

### Requirements

- Python 3.14 or later
- Git
- [Ollama](https://ollama.com/) installed and running

### 1. Start Ollama

If the Ollama service is not already running, start it in a terminal:

```bash
ollama serve
```

### 2. Get the project

```bash
git clone <repository-url>
cd git-ai-check
```

### 3. Install dependencies

Using [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

Or using pip:

```bash
python -m pip install .
```

### 4. Review staged changes

Stage the files you want reviewed, then run the checker from the project directory:

```bash
git add <files>
python checker.py
```

On first run, select an Ollama model from the interactive list. The checker downloads the selected model if needed and saves your choice to `~/.config/git-ai-checker/config.json`. The available models are:

| Model | Notes |
| --- | --- |
| `qwen2.5-coder:3b` | Default selection |
| `qwen3.5:9b` | Larger model |
| `gpt-oss:20b` | Larger model |

Only staged changes are reviewed. If nothing is staged, the checker exits without reviewing. A critical finding produces a nonzero exit code, which can stop a commit when the checker is used as a Git hook.

### Optional: use as a pre-commit hook

The repository does not install a hook automatically. To configure one manually, create `.git/hooks/pre-commit` in your target repository with:

```sh
#!/bin/sh
python /path/to/git-ai-check/checker.py
```

Replace the path with the location of this project, then make the hook executable:

```bash
chmod +x .git/hooks/pre-commit
```

## Roadmap

- [ ] Add a setup command to install and manage the pre-commit hook.
- [ ] Align Python and dependency requirements between package metadata and runtime checks.
- [ ] Improve configuration validation and Ollama error reporting.
- [ ] Support choosing or changing the model from the command line.
- [ ] Add tests for diff collection, model responses, and commit-blocking behavior.
- [ ] Verify and document Windows and other platform support.
- [ ] Add more features

---
<div align="center">
Made by Akshai Krishna KP
</div>