# Current Task

Implement Version-4 of WeatherApp.

Goal
Refactor the Version-3 GUI into a tab-based interface using QTabWidget.

This is a UI architecture refactor only. All data fetching, worker logic, and formatting rules from Version-3 must remain unchanged.

---

Constraint priority rule:
CONSTRAINTS.md overrides all other instructions.

---

## Scope of Changes

Modify only when necessary:

- `src/weatherapp/gui/main_window.py`
- `src/weatherapp/gui/worker.py` (only if required for widget reuse)
- `src/weatherapp/app.py`

---

## Core Refactor Requirement

Replace the root QVBoxLayout structure with a QTabWidget.

Each existing UI section must be MOVED (not recreated) into a tab.

---

### Tabs

#### 1. NOW

- Contains ONLY current weather widgets
- Must preserve existing layout and styling exactly
- No redesign of internal components

---

#### 2. HOURLY

- Contains existing 24-hour forecast scroll area
- Must preserve grid structure, formatting, and row generation logic

---

#### 3. 7-DAY

- Contains existing 7-day forecast scroll area
- Must preserve 15-column grid layout and all formatting rules

---

## Implementation Constraints (IMPORTANT)

- Do NOT recreate forecast or daily widgets
- Do NOT duplicate layout logic
- Move existing widget containers into tabs
- Keep all QScrollArea structures intact
- Keep signal/slot logic unchanged

---

## Layout Rules

- Use QTabWidget as central container
- Tab order must be:
  NOW → HOURLY → 7-DAY
- Default tab: NOW
- Ensure resizing does not distort grid layouts

---

## Worker Rules

- Worker remains unchanged
- Must continue emitting:
  - current weather
  - hourly forecast
  - daily forecast
- No structural changes required

---

## Functional Requirements

- Refresh updates all tabs simultaneously
- Auto-refresh (10 minutes) applies to all tabs
- No per-tab refresh logic

---

## Success Criteria

- App launches without UI regressions
- Tabs correctly display existing UI sections
- No duplicated forecast rows or widgets
- All data updates correctly in all tabs
- Layout remains stable when resizing
