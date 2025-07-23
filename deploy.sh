#!/bin/bash

echo "🚀 Deploying Farmer Assistant MVP to Google Cloud"

# Check if user is logged in
if ! gcloud auth list --filter=status: