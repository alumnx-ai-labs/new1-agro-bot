#!/bin/bash
# setup.sh - Enhanced one-stop setup for Farmer Assistant MVP

echo "🌱 Farmer Assistant MVP - Complete Setup"
echo "========================================"

# Step 1: Check Python version
echo "🐍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+' || echo "0.0")
# if (( $(echo "$python_version < 3.8" | bc -l 2>/dev/null || echo "1") )); then
#     echo "❌ Python 3.8+ required. Current version: $python_version"
#     echo "   Please install a newer Python version"
#     exit 1
# fi
# echo "✅ Python $python_version detected"

# Step 2: Check Google Cloud SDK
echo "☁️  Checking Google Cloud SDK..."
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK not found"
    echo "   Please install it from: https://cloud.google.com/sdk/docs/install"
    echo "   Then run this script again"
    exit 1
fi
echo "✅ Google Cloud SDK found"

# Step 3: Create virtual environment
echo "📦 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    echo "   Creating new virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Step 4: Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Step 5: Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Step 6: Create .env file
echo "📝 Setting up configuration..."
if [ ! -f ".env" ]; then
    echo "   Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Please edit .env file with your Google Cloud project details"
    echo "   Required fields:"
    echo "   - GOOGLE_CLOUD_PROJECT=your-project-id"
    echo ""
    read -p "   Press Enter after you've updated the .env file..."
else
    echo "✅ .env file already exists"
fi

# Step 7: Check Google Cloud authentication
echo "🔐 Checking Google Cloud authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null 2>&1; then
    echo "❌ Not authenticated with Google Cloud"
    echo "   Please run: gcloud auth application-default login"
    echo "   Then run this script again or continue manually"
    exit 1
fi
echo "✅ Google Cloud authentication verified"

# Step 8: Check project configuration
echo "🎯 Verifying project configuration..."
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No Google Cloud project configured"
    echo "   Please run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi
echo "✅ Project configured: $PROJECT_ID"

# Step 9: Make scripts executable
echo "🔧 Setting up script permissions..."
chmod +x *.sh 2>/dev/null || true
echo "✅ Script permissions set"

# Step 10: Run tests
echo "🧪 Running tests to verify setup..."
python -m pytest tests/ -v --tb=short

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📋 What's ready:"
    echo "   ✅ Python environment configured"
    echo "   ✅ Dependencies installed"
    echo "   ✅ Google Cloud authentication verified"
    echo "   ✅ All tests passing"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Run the application: ./run_app.sh"
    echo "   2. Open browser to: http://localhost:5500"
    echo "   3. Deploy to cloud: ./deploy.sh"
    echo ""
    echo "💡 Useful commands:"
    echo "   - Test only: ./test_local.sh"
    echo "   - View logs: tail -f logs/*.log"
    echo "   - Stop services: Ctrl+C in run_app.sh"
    
else
    echo ""
    echo "❌ Setup completed but tests failed"
    echo ""
    echo "🔧 Common issues and fixes:"
    echo "   1. Check .env file has correct GOOGLE_CLOUD_PROJECT"
    echo "   2. Ensure Firebase project has Blaze plan (not Spark)"
    echo "   3. Verify: gcloud auth application-default login"
    echo "   4. Check: gcloud config set project YOUR_PROJECT_ID"
    echo ""
    echo "📖 Try running tests individually:"
    echo "   python -m pytest tests/test_basic.py -v"
    echo ""
    echo "🚀 You can still try running the app:"
    echo "   ./run_app.sh"
fi