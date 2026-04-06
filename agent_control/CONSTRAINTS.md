# Development Constraints

These constraints override all other instructions unless explicitly lifted by a task.

The agent must not violate these rules.

---

## Architecture Stability

Do not reorganize the project structure.

Specifically forbidden actions:

- renaming directories
- moving modules between directories
- introducing new top-level directories
- splitting modules into multiple files
- merging existing modules

The directory layout defined in ARCHITECTURE.md must remain stable.

---

## Existing Code Protection

The following modules are considered stable and must not be modified
unless explicitly instructed in CURRENT_TASK.md:

src/weatherapp/data/get_weather_data.py
src/weatherapp/format/show_weather.py
src/weatherapp/utils/weather_code_mapper.py

Do not rewrite, refactor, or optimize these modules.

---

## Dependency Discipline

Do not introduce new dependencies unless absolutely necessary.

When a dependency is required:

- install only via Poetry
- update pyproject.toml
- justify the dependency in the task summary

Avoid adding large frameworks or unnecessary libraries.

---

## Refactoring Restrictions

Do not perform large refactors.

Forbidden actions include:

- renaming large numbers of variables or functions
- reorganizing module contents
- rewriting working implementations for stylistic reasons
- replacing working libraries with alternatives

If the code works and meets the requirements, leave it unchanged.

---

## Feature Scope Control

Implement only the feature described in CURRENT_TASK.md.

Do not:

- implement future roadmap features
- add optional improvements not requested
- introduce new configuration systems
- redesign the user interface

Keep changes minimal and focused.

---

## Performance and Threading

The GUI thread must never perform blocking I/O.

Network or API calls must run in worker threads.

Do not introduce synchronous network calls in GUI components.

---

## File Modification Limits

When implementing a task:

- modify only files required for the task
- avoid touching unrelated modules
- keep diffs minimal

Large-scale edits are discouraged unless necessary.

---

## Error Handling

Handle runtime errors gracefully.

Do not allow exceptions to crash the GUI application.

Errors should be reported in the interface when appropriate.

---

## Documentation Discipline

Documentation should be concise.

Avoid generating large documentation sections unless explicitly requested.

Keep Markdown files readable and focused.

---

## When in Doubt

If an action might violate these constraints:

do not perform it.

Instead report the limitation in the final summary.
