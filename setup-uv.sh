#!/bin/bash
# setup-uv.sh - Quick setup script for uv dependency management

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                     UV SETUP FOR ZOLO-ZCLI                                   ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed"
    echo ""
    echo "Please install uv first:"
    echo ""
    echo "  # macOS/Linux:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "  # Or via pip:"
    echo "  pip install uv"
    echo ""
    echo "  # Or via Homebrew (macOS):"
    echo "  brew install uv"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ uv is installed: $(uv --version)"
echo ""

# Check Python version
echo "🐍 Checking Python version..."
if [ -f .python-version ]; then
    REQUIRED_VERSION=$(cat .python-version)
    echo "   Required: Python $REQUIRED_VERSION"
    
    # Check if required Python is available
    if command -v python$REQUIRED_VERSION &> /dev/null; then
        echo "   ✅ Python $REQUIRED_VERSION found: $(python$REQUIRED_VERSION --version)"
    else
        echo "   ⚠️  Python $REQUIRED_VERSION not found"
        echo "   Installing via uv..."
        uv python install $REQUIRED_VERSION
    fi
else
    echo "   Using system Python: $(python3 --version)"
fi
echo ""

# Generate lock file if it doesn't exist
if [ ! -f uv.lock ]; then
    echo "📦 Generating uv.lock file..."
    uv lock
    echo "   ✅ Lock file generated"
else
    echo "📦 Lock file already exists"
    echo "   To regenerate: uv lock --upgrade"
fi
echo ""

# Install dependencies
echo "⬇️  Installing dependencies..."
uv sync --all-extras
echo "   ✅ Dependencies installed"
echo ""

# Verify installation
echo "🧪 Verifying installation..."
if uv run python -c "import zCLI; print(f'✅ zCLI v{zCLI.__version__} imported successfully')" 2>/dev/null; then
    echo "   ✅ zCLI package is working"
else
    echo "   ⚠️  zCLI not in editable mode yet"
    echo "   Installing in editable mode..."
    uv pip install -e .
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ SETUP COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo ""
echo "  # Run tests"
echo "  uv run pytest"
echo ""
echo "  # Start zCLI shell"
echo "  uv run zolo shell"
echo ""
echo "  # Run migrations"
echo "  uv run zolo migrate app.py"
echo ""
echo "See UV_SETUP.md for more information."
echo ""

