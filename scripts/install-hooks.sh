#!/usr/bin/env bash
# Install pre-commit hook

HOOK_DIR=".git/hooks"
HOOK_FILE="$HOOK_DIR/pre-commit"

if [ ! -d "$HOOK_DIR" ]; then
    echo "❌ Not a git repository"
    exit 1
fi

# Create pre-commit hook
cat > "$HOOK_FILE" << 'EOF'
#!/usr/bin/env bash
# Pre-commit hook for code quality checks

set -e

echo "🔍 Running pre-commit checks..."

# Check if we're in the right directory
if [ ! -d ".git" ]; then
    echo "❌ Not in git root directory"
    exit 1
fi

# Backend checks
if git diff --cached --name-only | grep -q "^backend/.*\.py$"; then
    echo "🐍 Checking Python code..."
    
    cd backend
    
    # Black formatting
    echo "  → Running black..."
    if ! black --check app/ 2>/dev/null; then
        echo "  ⚠️  Auto-formatting with black..."
        black app/
        git add app/
    fi
    
    # isort
    echo "  → Running isort..."
    if ! isort --check-only app/ 2>/dev/null; then
        echo "  ⚠️  Auto-sorting imports with isort..."
        isort app/
        git add app/
    fi
    
    # flake8 (no auto-fix)
    echo "  → Running flake8..."
    flake8 app/ --max-line-length=120 --exclude=__pycache__,migrations || {
        echo "❌ flake8 errors found. Please fix them before committing."
        cd ..
        exit 1
    }
    
    cd ..
    echo "✅ Python checks passed"
fi

# Frontend checks
if git diff --cached --name-only | grep -q "^frontend/.*\.\(ts\|tsx\)$"; then
    echo "⚛️  Checking TypeScript code..."
    
    cd frontend
    
    # ESLint (with auto-fix)
    echo "  → Running ESLint..."
    if ! npm run lint -- --quiet 2>/dev/null; then
        echo "  ⚠️  Auto-fixing with ESLint..."
        npm run lint -- --fix 2>/dev/null || true
        git add src/
    fi
    
    # TypeScript compilation
    echo "  → Checking TypeScript..."
    npx tsc --noEmit || {
        echo "❌ TypeScript errors found. Please fix them before committing."
        cd ..
        exit 1
    }
    
    cd ..
    echo "✅ TypeScript checks passed"
fi

echo "✨ All pre-commit checks passed!"
exit 0
EOF

chmod +x "$HOOK_FILE"

echo "✅ Pre-commit hook installed successfully!"
echo "📝 The hook will run automatically before each commit"
echo "💡 To bypass: git commit --no-verify"
