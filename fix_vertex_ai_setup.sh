#!/bin/bash
# fix_vertex_ai_setup.sh

echo "🔧 Fixing Vertex AI setup for your project"

# Get project ID
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"agro-bot-1212"}
echo "📝 Using Project ID: $PROJECT_ID"

# Enable required APIs
echo "🔌 Enabling required APIs..."

# Core APIs for Vertex AI
gcloud services enable aiplatform.googleapis.com --project=$PROJECT_ID
gcloud services enable ml.googleapis.com --project=$PROJECT_ID
gcloud services enable compute.googleapis.com --project=$PROJECT_ID
gcloud services enable storage.googleapis.com --project=$PROJECT_ID

echo "✅ APIs enabled"

# Check available models in your region
echo "🔍 Checking available embedding models in us-central1..."

# Try to list available models
gcloud ai models list \
    --region=us-central1 \
    --filter="displayName:embedding OR displayName:gecko" \
    --project=$PROJECT_ID

echo ""
echo "💡 If no models are listed above, try these solutions:"
echo "1. Wait a few minutes for API enablement to propagate"
echo "2. Try a different region (us-east1, us-west1, europe-west1)"
echo "3. Check if your project has Vertex AI enabled"

echo ""
echo "🚀 Now try running the ingestion script again:"
echo "python scripts/enhanced_ingest_schemes.py"