#!/bin/bash

# Build script for frontend
echo "Building frontend application..."

# Install dependencies
npm ci

# Build the application
npm run build

echo "Frontend build complete!"
echo "Built files are in the 'dist' directory"
