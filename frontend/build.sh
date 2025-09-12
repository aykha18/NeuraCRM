#!/bin/bash
# Build script for frontend deployment

echo "Building frontend for production..."

# Install dependencies
npm install

# Build the application
npm run build

echo "Frontend build completed!"
echo "Built files are in the 'dist' directory"
