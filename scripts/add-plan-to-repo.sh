#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/add-plan-to-repo.sh owner/repo [plan_path] [branch_name]
# Examples:
#   ./scripts/add-plan-to-repo.sh youruser/yourrepo
#   ./scripts/add-plan-to-repo.sh youruser/yourrepo docs/plan.md add-repotrackr-plan
#
# Prereqs:
#   - GitHub CLI: https://cli.github.com/ (gh auth login)
#   - git, curl

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: GitHub CLI (gh) is required. Install from https://cli.github.com/" >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "Error: git is required." >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl is required." >&2
  exit 1
fi

if [ $# -lt 1 ]; then
  echo "Usage: $0 <owner/repo> [plan_path] [branch_name]" >&2
  exit 1
fi

TARGET_REPO="$1"
PLAN_PATH="${2:-docs/plan.md}"
BRANCH_NAME="${3:-add-repotrackr-plan}"
WORKDIR="$(mktemp -d)"

# Template sources in this repository (caprolt/repotrackr)
PLAN_TEMPLATE_URL="https://raw.githubusercontent.com/caprolt/repotrackr/main/planning/template-plan-with-instructions.md"
CONFIG_TEMPLATE_URL="https://raw.githubusercontent.com/caprolt/repotrackr/main/planning/repotrackr.yml.template"

cleanup() { rm -rf "$WORKDIR"; }
trap cleanup EXIT

echo "Cloning $TARGET_REPO..."
gh repo clone "$TARGET_REPO" "$WORKDIR/repo" -- --quiet
cd "$WORKDIR/repo"

DEFAULT_BRANCH="$(git remote show origin | awk '/HEAD branch/ {print $NF}')"
if [ -z "${DEFAULT_BRANCH}" ]; then
  DEFAULT_BRANCH="main"
fi

echo "Creating branch $BRANCH_NAME from $DEFAULT_BRANCH..."
git checkout -b "$BRANCH_NAME" "origin/$DEFAULT_BRANCH" 2>/dev/null || git checkout -b "$BRANCH_NAME"

# If a plan already exists, bail to avoid overwriting
if [ -f "$PLAN_PATH" ]; then
  echo "A plan file already exists at $PLAN_PATH. Aborting to avoid overwriting."
  exit 0
fi

mkdir -p "$(dirname "$PLAN_PATH")"

echo "Fetching plan scaffold..."
curl -fSL "$PLAN_TEMPLATE_URL" -o "$PLAN_PATH"

# Replace placeholders in the scaffold to be more helpful
REPO_HTML_URL="$(gh repo view --json url -q .url 2>/dev/null || echo "https://github.com/${TARGET_REPO}")"
# macOS/BSD sed compatibility: use backup extension then remove
sed -i.bak "s|\\[GitHub Repository URL\\]|$REPO_HTML_URL|g" "$PLAN_PATH" || true
rm -f "${PLAN_PATH}.bak" || true

# Add repotrackr.yml if not present
if [ ! -f "repotrackr.yml" ] && [ ! -f ".repotrackr.yml" ]; then
  echo "Adding repotrackr.yml..."
  curl -fSL "$CONFIG_TEMPLATE_URL" -o "repotrackr.yml"
  # Update default plan path in config
  sed -i.bak "s|docs/plan.md|$PLAN_PATH|g" "repotrackr.yml" || true
  rm -f "repotrackr.yml.bak" || true
fi

git add "$PLAN_PATH"
[ -f "repotrackr.yml" ] && git add repotrackr.yml

cat >.gitmessage <<MSG
Add RepoTrackr planning scaffold and config

- Adds $PLAN_PATH (scaffolded plan with instructions)
- Adds repotrackr.yml (declares plan path and markers)
MSG

GIT_CONFIG_MESSAGE="$(cat .gitmessage)"

git commit -m "$GIT_CONFIG_MESSAGE"

echo "Pushing branch..."
if ! git push -u origin "$BRANCH_NAME"; then
  echo "Error: Failed to push branch. Check your permissions to $TARGET_REPO." >&2
  exit 1
fi

PR_TITLE="Add RepoTrackr planning scaffold ($PLAN_PATH)"
read -r -d '' PR_BODY <<'EOF'
This PR introduces a minimal, self-explaining planning document compatible with RepoTrackr.

What is RepoTrackr?
- A lightweight dashboard that reads a single Markdown plan in your repo
- It counts checkbox tasks, shows progress, and tracks status over time

What this PR adds:
- docs/plan.md (or your chosen path): a scaffold with usage instructions, examples, and recognized status markers
- repotrackr.yml: optional metadata declaring where the plan lives and which markers are used

How to get started:
1) Edit the plan file's placeholders (Project Name, Dates, etc.)
2) Add tasks using the markers:
   - [ ] todo
   - [~] doing
   - [x] done
   - [!] blocked
3) Merge this PR
4) In RepoTrackr, add your repository URL and plan path (defaults to docs/plan.md)

Want a different path?
- Move the file and update repotrackr.yml (plan_paths) or specify the path when adding the project in RepoTrackr.

Don't want this?
- Simply close this PR—no changes are applied.

Questions?
- See inline instructions at the top of the plan file
- Or check the RepoTrackr repo for more docs
EOF


echo "Opening pull request..."
if ! gh pr create --title "$PR_TITLE" --body "$PR_BODY" --base "$DEFAULT_BRANCH" --head "$BRANCH_NAME"; then
  echo "Error: Failed to create PR. You may not have permission or the repository may require different settings." >&2
  exit 1
fi

echo "Done. Review and merge the PR to enable RepoTrackr parsing."