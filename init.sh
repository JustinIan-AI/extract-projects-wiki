#!/bin/bash
set -e

echo "=== make-your-harness Initialization ==="
echo ""

echo "1. Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    echo "   Python3 not found, please install Python 3.8+"
    exit 1
fi
echo "   ✓ Python3 found: $(python3 --version)"

echo ""
echo "2. Installing Python dependencies..."
cd skills/repo-to-wiki && pip install -r skills/nexus-mapper/scripts/requirements.txt -q

echo ""
echo "3. Running tests..."
cd skills/repo-to-wiki && python -m pytest tests/ -v --tb=short

echo ""
echo "=== Verification Complete ==="
echo ""
echo "Next steps:"
echo "1. Read feature_list.json to see current feature state"
echo "2. Pick ONE unfinished feature to work on"
echo "3. Implement only that feature"
echo "4. Re-run verification before claiming done"
