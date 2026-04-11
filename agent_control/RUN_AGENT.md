# Hermes Agent Execution Instructions

You are operating as a development agent inside the WeatherApp repository.

Your task is defined in:

`agent_control/CURRENT_TASK.md`

Before beginning, read the following project control documents:

1. `agent_control/AGENT.md`
2. `agent_control/CONSTRAINTS.md`
3. `agent_control/PROJECT.md`
4. `agent_control/ARCHITECTURE.md`
5. `agent_control/ROADMAP.md`
6. `agent_control/PLAN.md`
7. `agent_control/STATE.md`
8. `agent_control/CHECKLIST.md`

Follow these steps exactly.

---

## Step 1 — Load Context

Read the documents listed above in order.

These files define:

- project constraints
- architecture
- development standards
- current roadmap
- the active task

Do not begin coding until all documents are understood.

---

## Step 2 — Understand the Current Task

Read:

`agent_control/CURRENT_TASK.md`

Determine:

- the specific goal
- the required deliverables
- the files that may need modification

If the task conflicts with project constraints, follow `agent_control/CONSTRAINTS.md`.

---

## Step 3 — Create an Implementation Plan

Update:

`agent_control/PLAN.md`

Include:

- files to create
- files to modify
- major implementation steps
- risks or uncertainties

Keep the plan concise and actionable.

---

## Step 4 — Implement the Task

Follow these rules:

- Respect all constraints defined in `agent_control/AGENT.md` and `agent_control/CONSTRAINTS.md`.
- Modify only files necessary to complete the task.
- Preserve existing functionality unless instructed otherwise.
- Keep implementations simple and maintainable.
- Avoid speculative features.

All code must follow project coding standards.

---

## Step 5 — Validate Changes

Before finishing:

1. Ensure new code compiles and imports correctly.
2. Verify GUI responsiveness (no blocking on the Qt main thread).
3. Ensure existing modules are not broken.
4. Confirm that new files are placed in correct directories.

---

## Step 6 — Update Project State

Update:

`agent_control/STATE.md`

Include:

- what was implemented
- which files were modified
- any limitations or unfinished work

---

## Step 7 — Self-Review

Run the checklist in:

`agent_control/CHECKLIST.md`

Ensure all items pass.

If issues are detected, correct them before finishing.

---

## Step 8 — Stop

When the task is complete:

- do not start new tasks
- do not modify roadmap
- do not add extra features

The agent should stop after completing the current task.

The human operator will review and commit changes.
