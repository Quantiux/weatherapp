#!/usr/bin/env bash

# -------------------------------------------------------------------------------
# release.sh
#
# Creates a release of the project by publishing the `app/` subtree to GitHub.
#
# Workflow performed by this script:
#   1. Stage and commit any pending development changes.
#   2. Create an annotated Git tag for the release.
#   3. Extract the `app/` directory as a git subtree.
#   4. Push that subtree to the public GitHub repository (origin/master).
#   5. Push the release tag to GitHub.
#
# Usage:
#   ./release.sh <tag> "<commit message>"
#
# Example:
#   ./release.sh v1.0.0 "Initial public release"
#
# The local repository remains a full development repo; only the `app/`
# subtree is published to the remote repository.
# -----------------------------------------------------------------------------

set -e

TAG="$1"
MESSAGE="$2"

if [ -z "$TAG" ] || [ -z "$MESSAGE" ]; then
  echo "Usage: ./release.sh <tag> <commit message>"
  exit 1
fi

# Ensure we're on the dev branch
current=$(git branch --show-current)
if [ "$current" != "dev" ]; then
  echo "Switch to the dev branch before releasing."
  exit 1
fi

echo "=== Committing changes ==="
git add -A
git commit -m "$MESSAGE" || echo "No changes to commit"

echo "=== Creating tag $TAG ==="
git tag -a "$TAG" -m "$MESSAGE"

echo "=== Publishing subtree (app/) ==="
git subtree push --prefix=app origin master

echo "=== Pushing tags ==="
git push origin --tags

echo "=== Release complete: $TAG ==="
