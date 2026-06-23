#!/usr/bin/env bash
set -euo pipefail

echo "=== PurgeCSS Audit ==="

cd "$(dirname "$0")/.."

# Check if tailwind content paths cover all source directories
CONTENT_PATHS=$(node -e "
  const cfg = require('./apps/web/tailwind.config.js');
  console.log(cfg.content.join('\n'));
")

echo "Tailwind content paths:"
echo "$CONTENT_PATHS"
echo ""

# Find .tsx files that might use Tailwind classes but aren't in content paths
echo "Checking for uncovered source files..."
UNCOVERED=0
while IFS= read -r file; do
    covered=false
    while IFS= read -r pattern; do
        # Convert glob pattern to rough match
        dir_match=$(echo "$pattern" | sed 's|/\.\*\*/\*\.{js,ts,jsx,tsx,mdx}|/|')
        if [[ "$file" == *"$dir_match"* ]]; then
            covered=true
            break
        fi
    done <<< "$CONTENT_PATHS"
    if [ "$covered" = false ]; then
        echo "  UNCOVERED: $file"
        UNCOVERED=$((UNCOVERED + 1))
    fi
done < <(find apps/web -name "*.tsx" -o -name "*.ts" | grep -v node_modules | grep -v .next | grep -v __tests__)

if [ "$UNCOVERED" -gt 0 ]; then
    echo "FAIL: $UNCOVERED files with potential Tailwind classes are not in content paths"
    exit 1
fi

echo "PASS: All source files covered by Tailwind content paths"
echo ""

# Check for potentially unused custom utilities
echo "Checking for unused custom classes..."
UNUSED=0
for cls in "contain-layout" "contain-paint" "contain-strict" "contain-content" "contain-size" "animate-pulse-slow" "animate-glow" "animate-float" "animate-scan"; do
    count=$(grep -r "\"$cls\"\|'$cls'\|$cls\b" apps/web --include="*.tsx" --include="*.ts" --include="*.css" -l 2>/dev/null | wc -l)
    if [ "$count" -eq 0 ]; then
        echo "  UNUSED: .$cls (0 references)"
        UNUSED=$((UNUSED + 1))
    fi
done

if [ "$UNUSED" -gt 0 ]; then
    echo "WARN: $UNUSED potentially unused custom classes found (check safelist in tailwind.config.js)"
else
    echo "PASS: All custom classes are in use"
fi

echo ""
echo "=== PurgeCSS audit complete ==="
