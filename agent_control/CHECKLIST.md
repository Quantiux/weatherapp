# Agent Self-Review Checklist

Before completing the task, verify every item below.

If any item fails, fix the issue before finishing.

---

## Task Completion

- The objective in CURRENT_TASK.md has been fully implemented.
- No features outside the current task were added.
- The task stops exactly at the defined scope.

---

## File Changes

- Only necessary files were created or modified.
- All new files are inside the correct project directories.
- No unintended files were created.

Expected locations:

`src/weatherapp/`
`tests/`
`agent_control/`

---

## Python Code Quality

- Code follows PEP 8 style guidelines.
- Line length does not exceed 100 characters.
- All modules import successfully.
- No unused imports remain.
- Functions and classes use appropriate naming conventions.

Naming conventions:

snake_case → variables and functions  
CamelCase → classes  
UPPER_CASE → constants

---

## GUI Safety (PyQt6)

- No blocking operations occur in the Qt main thread.
- All network or API calls run inside background workers.
- Signals and slots are used correctly.
- GUI updates occur only from the main thread.

---

## Architecture Compliance

- The existing project architecture was respected.
- Existing modules were not modified unless required.
- Data access continues to use the existing weather modules.

Required modules:

`src/weatherapp/data/get_weather_data.py`
`src/weatherapp/format/show_weather.py`
`src/weatherapp/utils/weather_code_mapper.py`

---

## Dependency Safety

- No unnecessary dependencies were added.
- Any new dependency was added through Poetry.
- pyproject.toml was updated if required.

---

## Project Integrity

- Existing functionality was not broken.
- Directory structure remains consistent.
- Cache behavior was not duplicated or bypassed.

---

## Documentation Updates

If new functionality was implemented:

- STATE.md was updated.
- PLAN.md reflects the implementation steps taken.

---

## Final Validation

Before stopping:

- All created modules import correctly.
- The GUI application launches successfully.
- No runtime errors are expected during startup.

If all checks pass, the task is complete.
