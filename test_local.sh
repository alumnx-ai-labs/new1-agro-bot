#!/bin/bash

echo "🧪 Testing Farmer Assistant MVP locally"

# Activate virtual environment
source venv/bin/activate

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

echo "🚀 Starting local Flask server..."
echo "🌐 Web interface will be available at: http://localhost:5000"
echo "📡 Cloud Function simulation at: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop the server"

# Start Flask app
cd webapp
python app.py