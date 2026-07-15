#!/usr/bin/env bash
set -euo pipefail

# install-gitleaks-precommit.sh
# Installs Gitleaks and sets up a pre-commit git hook to block secrets.

GITLEAKS_VERSION="8.18.2"
HOOK_DIR="$(git rev-parse --git-dir 2>/dev/null || echo '.git')"
HOOK_FILE="$HOOK_DIR/hooks/pre-commit"

echo "==> Checking Gitleaks installation..."

if command -v gitleaks &>/dev/null; then
    INSTALLED=$(gitleaks version 2>/dev/null || echo "unknown")
    echo "    Gitleaks already installed: $INSTALLED"
else
    echo "    Installing Gitleaks v${GITLEAKS_VERSION}..."
    case "$(uname -s)" in
        Darwin*)
            if command -v brew &>/dev/null; then
                brew install gitleaks
            else
                curl -sSfL "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_darwin_$(uname -m).tar.gz" \
                    | tar -xz -C /usr/local/bin gitleaks
            fi
            ;;
        Linux*)
            curl -sSfL "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_$(uname -m).tar.gz" \
                | tar -xz -C /usr/local/bin gitleaks
            ;;
        CYGWIN*|MINGW*|MSYS*)
            if command -v scoop &>/dev/null; then
                scoop install gitleaks
            else
                echo "    Windows detected. Please install Gitleaks manually via:"
                echo "      scoop install gitleaks"
                echo "      or download from https://github.com/gitleaks/gitleaks/releases"
                echo "      Then re-run this script."
                exit 1
            fi
            ;;
        *)
            echo "    Unsupported platform: $(uname -s)"
            exit 1
            ;;
    esac
    echo "    Gitleaks v${GITLEAKS_VERSION} installed successfully."
fi

echo "==> Installing pre-commit hook at $HOOK_FILE..."

cat > "$HOOK_FILE" << 'HOOK'
#!/usr/bin/env bash
set -euo pipefail

echo "🔍 Scanning staged changes for secrets..."

GITLEAKS_CONFIG=".gitleaks.toml"
if [ -f "$GITLEAKS_CONFIG" ]; then
    CONFIG_FLAG="--config=$GITLEAKS_CONFIG"
else
    CONFIG_FLAG=""
fi

if command -v gitleaks &>/dev/null; then
    gitleaks protect --staged $CONFIG_FLAG 2>&1
    RESULT=$?
    if [ $RESULT -ne 0 ]; then
        echo ""
        echo "❌ SECRETS DETECTED — Commit blocked!"
        echo "   Potential API keys, tokens, or passwords were found in staged changes."
        echo "   Review the findings above before committing."
        echo "   If this is a false positive, update .gitleaks.toml allowlist."
        exit 1
    fi
else
    echo "⚠️  Gitleaks not installed — skipping secret scan."
    echo "   Install it: https://github.com/gitleaks/gitleaks#installing"
fi
HOOK

chmod +x "$HOOK_FILE"
echo "✅ Pre-commit hook installed at $HOOK_FILE"
echo "   Staged changes will now be scanned for secrets before every commit."