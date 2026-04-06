# Agent Instructions for WeatherApp

These instructions define how an AI agent should modify, extend, and maintain the WeatherApp project.
Assume you are allowed to edit code and documentation unless explicitly restricted.

---

## 1. Project Environment & Structure

- Use the project’s **Poetry environment** for all installs, commands, tests, and execution.
- Never install system-wide Python packages.
- Runtime code lives under `src/weatherapp/`.
- Tests live under `tests/`.
- Do not create new top-level directories unless explicitly requested.
- Keep all file paths inside the project root.

---

## 2. Supported Languages & Scope

- Primary language: **Python**
- Secondary / support files: Bash, JSON, YAML, Markdown
- Apply language-appropriate conventions; do not introduce cross-language style assumptions.

---

## 3. Python Coding Standards

- Follow **PEP 8**, with a max line length of **100 characters**.
- Naming:
  - Variables / functions: `snake_case`
  - Classes: `CamelCase`
  - Constants: `ALL_CAPS_WITH_UNDERSCORES`
- Use type hints where practical.
- Handle errors with `try/except` and log relevant context.
- Preserve existing behavior unless explicitly instructed to change it.
- Keep changes minimal and localized.

---

## 4. GUI Implementation

- Use **PyQt6** unless explicitly instructed otherwise.
- The main window must support:
  - Current conditions
  - Hourly forecast (up to 48 hours)
  - Daily forecast (7–10 days)
- Keep the UI responsive:
  - Never block the Qt event loop.
  - Use background threads, workers, or signals/slots for I/O.
- Styling should remain lightweight and functional.

---

## 5. Weather Data Workflow

- Build on existing scripts (`data/get_weather_data.py`, `format/show_weather.py`, `utils/weather_code_mapper.py`).
- Avoid unnecessary refactoring of working code.
- Cache weather data under `.cache/` in the project root.
- Respect cache refresh rules.
- Prefer parameters or dependency injection over global state.

---

## 6. Dependencies & Packaging

- Add dependencies **only when necessary**, always via Poetry.
- Update `pyproject.toml` accordingly.
- Do not introduce alternative package managers.
- Provide Linux Mint–friendly instructions for running the app from source when relevant.
- Standalone binaries or installers should be prepared only if explicitly requested.

---

## 7. Testing & Validation

- Prefer existing tests when available.
- Add minimal tests when needed, focusing on:
  - Data parsing
  - Formatting
  - Error handling
- Mock all network and API calls.
- Use `pytest` unless explicitly instructed otherwise.
- Avoid breaking unrelated functionality.

---

## 8. Documentation & Markdown

- Keep documentation concise, factual, and actionable.
- Use consistent headings, lists, and fenced code blocks.
- Use present tense and active voice.
- Markdown filenames should be lowercase with hyphens.
- Include brief summaries of non-obvious changes when modifying behavior.

---

## 9. Agent Behavior & Self-Review

Before finalizing changes, verify that:

- Only relevant files were modified.
- No blocking I/O occurs on the main GUI thread.
- Cache logic is respected and not duplicated.
- New dependencies are justified and documented.
- Existing functionality remains intact unless intentionally changed.
- Changes are minimal, purposeful, and consistent with the project’s structure.

When performing multi-step tasks, provide short progress updates and a concise summary of completed actions.

---

## 10. Incremental Development

The project evolves through numbered versions.

Rules:

- Each version must compile and run.
- Do not implement future features early.
- Modify only the files required for the current version.
- Preserve backward compatibility with previous versions.
