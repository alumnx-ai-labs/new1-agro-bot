#!/bin/bash

echo "🌱 Setting up Farmer Assistant MVP - Phase 1"

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
if (( $(echo "$python_version < 3.8" | bc -l) )); then
    echo "❌ Python 3.8+ required. Current version: $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check for Google Cloud SDK
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK not found. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and fill in your values"
echo "2. Run: gcloud auth application-default login"
echo "3. Run: ./test_local.sh to test locally"
echo "4. Run: ./deploy.sh to deploy to production"