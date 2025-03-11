#!/bin/bash

# Screenshot Processing Script for Second Brain
# This script is a wrapper for the process_screenshot.py Python script

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SECOND_BRAIN_DIR="$(dirname "$SCRIPT_DIR")"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if the required Python packages are installed
if ! python3 -c "import pytesseract, PIL" &> /dev/null; then
    echo "Installing required Python packages..."
    pip3 install -r "$SCRIPT_DIR/requirements.txt"
fi

# Check if Tesseract is installed
if ! command -v tesseract &> /dev/null; then
    echo "Error: Tesseract OCR is required but not installed."
    echo "Please install Tesseract OCR:"
    echo "  - macOS: brew install tesseract"
    echo "  - Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "  - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
    exit 1
fi

# Change to the Second Brain directory
cd "$SECOND_BRAIN_DIR"

# Process the screenshot
python3 "$SCRIPT_DIR/process_screenshot.py" "$@" 