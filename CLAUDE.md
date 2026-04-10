# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Coursework for the AI Engineering Bootcamp (Maven course). Python/FastAPI services deployed on Render, integrating with Claude via the Anthropic SDK.

## Security Posture — THIS REPO IS PUBLIC

This is a public GitHub repository. Treat every commit as visible to the world.

- **NEVER hardcode secrets, API keys, tokens, or credentials anywhere** — not in code, comments, commit messages, or CLAUDE.md files
- **All secrets go in `.env`** (gitignored) and are loaded via Pydantic Settings. Provide placeholder patterns in `.env.example` only
- **Anthropic API key**: instantiate `anthropic.Anthropic()` with no arguments — the SDK reads `ANTHROPIC_API_KEY` from the environment. Never pass the key as a string
- **Pre-commit hooks are mandatory**: gitleaks blocks secret commits, ruff enforces lint/format. Run `pre-commit install` after cloning
- **GitHub Secret Scanning + Push Protection** are enabled on this repo
- **Never put secrets in system prompts** — assume model context can be extracted
- Before committing, mentally audit: "would I be comfortable if this diff appeared on Hacker News?"

## Stack

| Layer | Tool |
|-------|------|
| Language | Python 3.12+ |
| Package manager | **uv** (not pip) |
| Framework | FastAPI |
| Config | pydantic-settings (reads `.env`) |
| LLM | Anthropic SDK (`anthropic` package) |
| Linting/formatting | Ruff |
| Rate limiting | slowapi |
| Deployment | Render |

## Repo Layout

Each week of coursework lives in its own subfolder (e.g. `week1/`). Each week folder that has a deployable service contains its own `pyproject.toml`, `uv.lock`, `app/`, `tests/`, and `prompts/`. Render's `rootDir` in `render.yaml` points to the active week.

## Commands

All `uv` commands run from inside the relevant week folder (e.g. `cd week1`).

```bash
# Setup (from week folder, e.g. cd week1)
uv sync                          # install all dependencies
uv sync --extra dev              # include dev dependencies
pre-commit install               # activate pre-commit hooks (from repo root)

# Run (from week folder)
uv run uvicorn app.main:app --reload # dev server
uv run pytest                    # run all tests
uv run pytest tests/test_foo.py::test_bar  # run a single test
uv run ruff check .              # lint
uv run ruff format .             # format

# Security (from week folder)
uv run pip-audit                 # scan dependencies for vulnerabilities
pre-commit run --all-files       # run all hooks on entire repo (from repo root)
```

## Conventions

### FastAPI Patterns

- **DRY**: Use `app/dependencies.py` for shared singletons (`get_settings()`, `get_anthropic_service()`). Inject via `Depends()` — never instantiate Settings or services directly in routes
- Use **Pydantic models** for all request/response bodies with explicit field constraints (`constr`, `Field(max_length=...)`)
- Use **dependency injection** (`Depends()`) for auth, settings, and shared clients
- Every service must expose `GET /health` returning `{"status": "healthy"}` — Render uses this for zero-downtime deploys
- CORS: explicit origin allowlist from `settings.allowed_origins`. Never use `["*"]` in production
- Rate limit public endpoints with `@limiter.limit()` from slowapi

### Anthropic SDK Usage

- Default model: `claude-haiku-4-5-20251001` (latest Haiku) — fast and cheap for bootcamp work
- Always set `max_tokens` on every `messages.create()` call to cap cost
- Use the `system` parameter for system prompts — never concatenate user input into system strings
- Log `response.usage.input_tokens` and `response.usage.output_tokens` for cost monitoring
- The dedicated API key for this project has spend limits set in the Anthropic Console

### Project Structure

- Use `uv add <package>` to add dependencies (updates `pyproject.toml` and `uv.lock`)
- Tests go in `tests/` using pytest + pytest-asyncio. Use `httpx.AsyncClient` for endpoint tests
- Ruff is configured in `pyproject.toml` with security rules enabled (`S` ruleset from bandit)

### Logging

Logging must be configured in the **FastAPI lifespan event** — not at module level, not via `logging.basicConfig()`. This is critical because Render runs `uvicorn main:app` via CLI, and Uvicorn calls `dictConfig()` at startup which stomps any earlier config.

The correct pattern:
- Configure logging inside `@asynccontextmanager async def lifespan(app):`
- Strip Uvicorn's handlers: `logging.getLogger("uvicorn").handlers = []`
- Set `propagate=True` on uvicorn, uvicorn.error, uvicorn.access so they flow to root
- Use exactly ONE handler on the root logger — no duplicates
- Switch formatter based on `ENVIRONMENT`: human-readable for dev, JSON for production
- **Never call `logging.basicConfig()` at module level** — it gets stomped or causes duplicate output
- **Always set `disable_existing_loggers: False`** in any `dictConfig` call

### Render Deployment

- `render.yaml` uses `sync: false` for all secret environment variables — values are set in the Render Dashboard, never in the YAML file
- Use Environment Groups to share secrets across services
- Build command: `uv sync --frozen && uv cache prune --ci` (uv is pre-installed on Render's native Python runtime)
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
