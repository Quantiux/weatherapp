#!/usr/bin/env bash

set -e

# -------------------------------
# Hermes Agent Runner for WeatherApp
# -------------------------------

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

CONTROL_DIR="$PROJECT_ROOT/agent_control"

echo "=== Hermes Development Runner ==="
echo "Project root: $PROJECT_ROOT"
echo "Control folder: $CONTROL_DIR"
echo

# ---- 1. Sanity checks ----
REQUIRED_FILES=(
  "$CONTROL_DIR/AGENT.md"
  "$CONTROL_DIR/CONSTRAINTS.md"
  "$CONTROL_DIR/PROJECT.md"
  "$CONTROL_DIR/ARCHITECTURE.md"
  "$CONTROL_DIR/ROADMAP.md"
  "$CONTROL_DIR/CURRENT_TASK.md"
  "$CONTROL_DIR/PLAN.md"
  "$CONTROL_DIR/STATE.md"
  "$CONTROL_DIR/RUN_AGENT.md"
  "$CONTROL_DIR/CHECKLIST.md"
)

echo "Checking required control files..."
for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$file" ]; then
    echo "ERROR: Missing required file: $file"
    exit 1
  fi
done
echo "All required files present."
echo

# ---- 2. Git status check ----
if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "Git repository detected."

  if [ -n "$(git status --porcelain)" ]; then
    echo
    echo "ERROR: Uncommitted changes detected."
    echo
    git status --short
    echo
    echo "Please commit or stash changes before running Hermes."
    echo
    echo "Example:"
    echo "  git add ."
    echo "  git commit -m \"describe your changes\""
    echo
    echo "Then run:"
    echo "  ./run_hermes.sh"
    echo
    exit 1
  else
    echo "Working tree clean."
  fi

else
  echo "ERROR: Not inside a git repository."
  echo
  echo "Initialize git before running Hermes:"
  echo
  echo "  git init"
  echo "  git add ."
  echo "  git commit -m \"Initial commit\""
  echo
  exit 1
fi

echo

# ---- 3. Display CURRENT_TASK.md ----
echo "=== CURRENT TASK ==="
echo "----------------------------------"
cat "$CONTROL_DIR/CURRENT_TASK.md"
echo "----------------------------------"
echo

# ---- 4. Launch Hermes ----
echo "Launching Hermes..."
echo
echo "Instruction to Hermes:"
echo "\"Read $CONTROL_DIR/RUN_AGENT.md and begin.\""
echo

hermes

echo
echo "Hermes session finished."
echo

# ---- 5. Post-run change summary ----
echo "=== Repository changes after Hermes run ==="
echo

if [ -n "$(git status --porcelain)" ]; then
  git status --short
  echo
  echo "Diff summary:"
  git diff --stat
else
  echo "No file changes detected."
fi

echo
echo "Review changes carefully."
echo "When satisfied, commit them:"
echo
echo "  git add ."
echo "  git commit -m \"Hermes: describe changes\""
echo
