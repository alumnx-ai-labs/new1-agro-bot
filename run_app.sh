#!/bin/bash
# run_app.sh - Runs both frontend and backend simultaneously

echo "🚀 Starting Farmer Assistant MVP - Full Stack"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Error: No virtual environment detected!"
    echo "   Please run: source venv/bin/activate"
    exit 1
fi

# Set environment variables
export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)
export GOOGLE_CLOUD_REGION="us-central1"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python -c "import flask, google.cloud.firestore, vertexai" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Please run: pip install -r requirements.txt"
    exit 1
fi

# Create log directory
mkdir -p logs

echo "🎯 Starting services..."
echo "📡 Backend (Cloud Function simulation): http://localhost:8080"
echo "🌐 Frontend (Web interface): http://localhost:5500"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=========================="

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $(jobs -p) 2>/dev/null
    wait
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Start backend (Cloud Function simulation) in background
echo "🔧 Starting backend service..."
functions-framework --target=farmer_assistant --source=cloud_functions/main.py --port=8080 --debug > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! curl -s http://localhost:8080/health_check > /dev/null 2>&1; then
    echo "⚠️  Backend might be starting up, continuing anyway..."
fi

# Start frontend in background
echo "🌐 Starting frontend service..."
cd webapp
export CLOUD_FUNCTION_URL="http://localhost:8080"
python app.py > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 3

# Check if frontend started successfully
if curl -s http://localhost:5500/health > /dev/null 2>&1; then
    echo "✅ Frontend started successfully"
else
    echo "⚠️  Frontend might be starting up..."
fi

echo ""
echo "🎉 Services are running!"
echo "📱 Open your browser and go to: http://localhost:5500"
echo "🔧 Backend API available at: http://localhost:8080"
echo ""
echo "📋 Logs:"
echo "   Backend: tail -f logs/backend.log"
echo "   Frontend: tail -f logs/frontend.log"
echo ""
echo "🔄 Waiting for services... (Press Ctrl+C to stop)"

# Keep script running and show live status
while true; do
    sleep 10
    
    # Check if services are still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend service stopped unexpectedly"
        break
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend service stopped unexpectedly"
        break
    fi
    
    # Optional: Show a simple status update every minute
    # echo "⏰ Services running... $(date '+%H:%M:%S')"
done

# If we get here, something went wrong
cleanup