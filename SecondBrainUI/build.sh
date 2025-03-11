#!/bin/bash

# Exit on error
set -e

echo "=== Second Brain UI Build Script ==="
echo "This script will build the Second Brain UI application for your platform."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js and try again."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed. Please install npm and try again."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the application
echo "Building the application..."
npm run dist

echo ""
echo "Build completed! You can find your installer in the 'dist' directory."
echo "For help using the application, see the SecondBrainUI_Usage.md file." 