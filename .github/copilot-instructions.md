<!-- Copilot instructions for AI coding agents working on this repo -->
# Ibex Backend — Copilot Instructions

Summary
- Small Python backend workspace. Current tree shows a checked-in virtualenv (`.venv/`), an empty `requirements/` folder, and a file `ibex_backend/API.bash` that contains a repository tree dump (not an executable script).

Quick goals for an AI agent
- Identify the real application entrypoint (search for `app.py`, `main.py`, `server.py`, or framework keywords: `flask`, `fastapi`, `django`).
- Prefer minimal, reversible edits — this repo appears incomplete; open a PR with clear intent and a short description.

What I looked at (examples)
- `ibex_backend/API.bash` — contains a tree listing rather than runnable code. Treat it as documentation/placeholder.
- `.venv/` — a full virtualenv appears present; do not modify or commit changes inside `.venv/`.
- `requirements/` — empty directory; look for `requirements.txt` elsewhere before creating one.
- `Untitled-1.txt` — unknown notes file at repo root; inspect before deleting.

Repository conventions and patterns
- Local virtualenv usage: the project keeps a `.venv/` folder. On Windows, developers likely use `.venv\\Scripts\\activate` to activate the environment. Avoid altering `.venv`; prefer creating reproducible `requirements.txt` or `pyproject.toml` instead.
- No tests or explicit framework files detected. Assume standard Python web frameworks when exploring, but confirm by searching for imports (e.g., `from fastapi`, `flask`, `django`).

Developer workflows (commands to try)
- Activate venv (Windows PowerShell):

```powershell
.\\.venv\\Scripts\\Activate.ps1
```

- Activate venv (cmd):

```cmd
.venv\\Scripts\\activate.bat
```

- Install dependencies (if a `requirements.txt` is created or found):

```bash
pip install -r requirements.txt
```

Discovery checklist for agents before edits
1. Search the repo for framework clues: `grep -R "from fastapi\\|import flask\\|django"`.
2. Search for common entrypoints: `app.py`, `main.py`, `wsgi.py`, `manage.py`, `server.py`.
3. Inspect `Untitled-1.txt` and `ibex_backend/API.bash` to understand any human notes or intended scripts.
4. Do not modify `.venv/` contents or commit changes inside it — prefer regenerating environment artifacts instead.

When creating or updating files
- If adding a `requirements.txt` or `pyproject.toml`, include a short comment explaining how it was generated (e.g., `pip freeze > requirements.txt`), and prefer pinning only direct dependencies.
- If scaffolding an entrypoint, add a minimal README or PR description that explains how to run the new code.

What not to assume
- There is currently no running server configuration or test harness discoverable. Do not assume Flask/FastAPI until imports confirm it.
- The `.venv/` directory is considered a workspace artifact — avoid deleting it without asking the repo owner.

Next steps for you (human)
- Confirm whether `API.bash` is intended as documentation or should be replaced by an actual script.
- Add a `README.md` with the project's intended framework and run instructions.

If anything above is unclear or you want this file expanded with PR templates, test run commands, or CI notes, say which area to expand and I will update this file.
