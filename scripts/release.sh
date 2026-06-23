#!/usr/bin/env bash
set -euo pipefail

# ARIA OS Release Script
# Usage: ./scripts/release.sh [major|minor|patch] [--dry-run]
# Example: ./scripts/release.sh patch --dry-run

SEMVER="${1:-patch}"
DRY_RUN="${2:-}"
VERSION_FILE="apps/web/package.json"
CHANGELOG="CHANGELOG.md"

if [ "$SEMVER" != "major" ] && [ "$SEMVER" != "minor" ] && [ "$SEMVER" != "patch" ]; then
    echo "Usage: $0 [major|minor|patch] [--dry-run]"
    exit 1
fi

cd "$(dirname "$0")/.."

# Ensure working tree is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "FAIL: Working tree is not clean. Commit or stash changes first."
    exit 1
fi

# Extract current version
CURRENT_VERSION=$(node -p "require('./$VERSION_FILE').version")
echo "Current version: $CURRENT_VERSION"

# Calculate new version
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"
case "$SEMVER" in
    major) NEW_VERSION="$((MAJOR + 1)).0.0" ;;
    minor) NEW_VERSION="$MAJOR.$((MINOR + 1)).0" ;;
    patch) NEW_VERSION="$MAJOR.$MINOR.$((PATCH + 1))" ;;
esac
echo "New version: $NEW_VERSION"

if [ "$DRY_RUN" = "--dry-run" ]; then
    echo "Dry run — no changes made."
    exit 0
fi

# Update package.json
node -e "
    const pkg = require('./$VERSION_FILE');
    pkg.version = '$NEW_VERSION';
    require('fs').writeFileSync('./$VERSION_FILE', JSON.stringify(pkg, null, 2) + '\n');
"
echo "Updated $VERSION_FILE to $NEW_VERSION"

# Check if changelog has entry for new version
if grep -q "^## \[$NEW_VERSION\]" "$CHANGELOG"; then
    echo "OK: CHANGELOG entry for $NEW_VERSION found"
else
    echo "WARN: No CHANGELOG entry for $NEW_VERSION. Add one before releasing."
fi

# Verify build
echo "Verifying build..."
cd apps/web
npm run lint > /dev/null 2>&1 && echo "  Lint: OK" || echo "  Lint: WARN (ignoring)"
npm run type-check > /dev/null 2>&1 && echo "  Type-check: OK" || { echo "  Type-check: FAIL"; exit 1; }
npm run build > /dev/null 2>&1 && echo "  Build: OK" || { echo "  Build: FAIL"; exit 1; }

# Verify backend
cd ../..
python -m ruff check apps/api/ packages/ services/ > /dev/null 2>&1 && echo "  Ruff: OK" || { echo "  Ruff: FAIL"; exit 1; }
python -m pytest tests/ -q --no-cov > /dev/null 2>&1 && echo "  Tests: OK" || { echo "  Tests: FAIL"; exit 1; }

# Git tag
git add "$VERSION_FILE"
git commit -m "chore(release): v$NEW_VERSION"
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"

echo ""
echo "=== Release v$NEW_VERSION complete ==="
echo "Run 'git push --follow-tags' to publish."
