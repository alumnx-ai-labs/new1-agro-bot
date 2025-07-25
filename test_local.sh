#!/bin/bash
# test_local.sh
echo "🧪 Testing Farmer Assistant MVP locally"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: No virtual environment detected. Make sure you have activated your venv."
    echo "   Run: source venv/bin/activate"
    echo ""
fi

# Set environment for local testing
export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)
export GOOGLE_CLOUD_REGION="us-central1"

echo "🔍 Running basic tests..."
python -m pytest tests/ -v

if [ $? -eq 0 ]; then
    echo "✅ Tests passed!"
else
    echo "❌ Tests failed. Please fix issues before proceeding."
    exit 1
fi

echo "🎯 Tests completed successfully!"
echo ""
echo "To run the full application (frontend + backend), use:"
echo "   ./run_app.sh"