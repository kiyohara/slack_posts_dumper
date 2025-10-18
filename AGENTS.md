# Repository Guidelines

## Project Structure & Module Organization
Core logic lives in `src/`, with `slack_checker.py` coordinating API access, `message_renderer.py` shaping HTML output, and helpers split between `utils/` and `config/settings.py`. CLI-like utilities, including fetchers and regression tests, are in `scripts/`. HTML and README templates reside under `templates/`. Generated exports should remain in `output/`, while `docs/` captures background notes and references.

## Build, Test, and Development Commands
- `poetry install` — set up the virtualenv and lockfile dependencies.
- `poetry run python scripts/get_channels.py --token "$SLACK_BOT_TOKEN"` — list accessible channels to confirm credentials.
- `poetry run python scripts/get_latest_message.py --channel general --format local` — dump the most recent message to `output/`.
- `poetry run pytest` — execute the regression suite that exercises the download/render helpers.
- `poetry run black src scripts` and `poetry run flake8 src scripts` — format and lint before opening a PR.

## Coding Style & Naming Conventions
Use 4-space indentation and UTF-8 safe strings. Modules follow lowercase with underscores, classes use PascalCase, and functions/variables use snake_case. Keep renderer templates cohesive by mirroring Jinja block names defined in `templates/message.html`. Favor dataclass-style DTOs where practical and guard Slack API responses with explicit error handling.

## Testing Guidelines
Pytest discovers tests in `scripts/test_*.py`; name new files and functions with a `test_` prefix for auto-discovery. Aim to cover credential edge cases (missing tokens, rate limits) and rendering regressions (emoji fallback, link sanitization). When tests require API fixtures, prefer VCR-style cassettes or stubbed responses rather than live calls. Run `poetry run pytest -k your_feature` for targeted checks before full runs.

## Commit & Pull Request Guidelines
Follow the existing Conventional Commit style (`feat:`, `fix:`, `refactor:`, `docs:`) with concise, descriptive summaries; include Japanese context when it clarifies changes. Each PR should link to any relevant specs (see `PROJECT_SPEC.md`), describe configuration updates, and attach sanitized screenshots or HTML snippets if the renderer changes. Update `README.md` or templates when behavior shifts, and ensure CI-friendly commands (`pytest`, `black`, `flake8`) pass locally.

## Configuration & Security Notes
Copy `env.example` to `.env` and supply Slack tokens plus workspace IDs before running scripts. Treat tokens as secrets—avoid committing them and prefer environment exports when running commands (`export SLACK_BOT_TOKEN=...`). Clean sensitive content from `output/` before sharing artifacts outside the team.
