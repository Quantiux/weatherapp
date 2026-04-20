# Implementation Plan — Version 5.14 (README rewrite)

Goal:

Produce a clear, polished, professional README.md suitable for a public GitHub repository that accurately describes the current WeatherApp state. Modify only README.md for the product content; agent_control/PLAN.md and agent_control/STATE.md will be updated to record plan and outcome.

Files to create/modify:

- Modify: README.md
- Create/Update: agent_control/PLAN.md (this file)
- Update: agent_control/STATE.md (after verification)

Acceptance criteria:

1. README.md contains the required sections listed in agent_control/CURRENT_TASK.md: title, short description, features, screenshots, installation, running instructions, data source, project structure (brief), future improvements, and license.
2. Screenshots use the provided images (docs/screenshots/current.png, hourly.png, daily.png) with standard Markdown image syntax.
3. Installation includes the libxcb-cursor0 note and example commands using Poetry.
4. Running instructions use the module entry: `poetry run python -m weatherapp.app` (as specified in CURRENT_TASK.md).
5. README is concise, factual, avoids emojis and exaggerated claims, and reflects the repository state.

Tasks (small, ordered):

Task 1 — Draft README (5–15 min)
- Write the full README.md content following the sections and style requirements.
- Keep language professional and concise.

Task 2 — Sanity check (2–5 min)
- Ensure image paths exist (docs/screenshots/...) and the file names match.
- Ensure the run command and installation steps match CURRENT_TASK.md.

Task 3 — Update STATE.md (5 min)
- Document that README.md was updated and list files changed.
- Note that no Python source files were modified.

Verification:
- Manual review of README.md content for accuracy and tone.
- Confirm images referenced exist in docs/screenshots/.
- Confirm no source files were changed (only README.md, PLAN.md, STATE.md updated).

Notes / Constraints:
- Do not modify Python source files.
- Keep diffs minimal and avoid adding new dependencies.
- Do not stage or commit any changes; human will review and commit.
