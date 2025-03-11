#!/usr/bin/env python3
"""
Screenshot Processing Script for Second Brain

This script processes screenshots and extracts text using OCR.
It then creates a note with the extracted text in the Second Brain.

Usage:
    python process_screenshot.py <path_to_screenshot> [note_title]

Requirements:
    - pytesseract
    - Pillow (PIL)
    - tesseract-ocr (system dependency)

Install dependencies:
    pip install pytesseract Pillow
    
    # On macOS:
    brew install tesseract
    
    # On Ubuntu/Debian:
    sudo apt-get install tesseract-ocr
    
    # On Windows:
    # Download and install from https://github.com/UB-Mannheim/tesseract/wiki
"""

import os
import sys
import datetime
import argparse
from pathlib import Path
import pytesseract
from PIL import Image

def extract_text_from_image(image_path):
    """Extract text from an image using OCR."""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return None

def create_note_from_screenshot(image_path, note_title=None):
    """Create a note in the Second Brain from a screenshot."""
    # Extract text from the image
    extracted_text = extract_text_from_image(image_path)
    
    if not extracted_text:
        print("No text could be extracted from the image.")
        return False
    
    # Generate a filename for the note
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    
    if not note_title:
        # Use the image filename as the note title if none provided
        note_title = os.path.splitext(os.path.basename(image_path))[0]
    
    # Clean the title for use in a filename
    clean_title = "".join(c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in note_title)
    clean_title = clean_title.replace(' ', '_').lower()
    
    # Create the note filename
    note_filename = f"{timestamp}_{clean_title}.md"
    note_path = os.path.join("Notes", "Fleeting", note_filename)
    
    # Create a copy of the image in the Screenshots directory
    screenshot_dir = os.path.join("Resources", "Screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)
    
    screenshot_filename = f"{timestamp}_{clean_title}{os.path.splitext(image_path)[1]}"
    screenshot_path = os.path.join(screenshot_dir, screenshot_filename)
    
    # Copy the image
    try:
        with open(image_path, 'rb') as src_file:
            with open(screenshot_path, 'wb') as dst_file:
                dst_file.write(src_file.read())
    except Exception as e:
        print(f"Error copying screenshot: {e}")
        return False
    
    # Create the note content
    relative_path = os.path.join("Resources", "Screenshots", screenshot_filename)
    
    note_content = f"""# {note_title} - Screenshot Note

## Metadata
- Created: {datetime.datetime.now().strftime("%Y-%m-%d")}
- Tags: #screenshot #ocr
- Status: Fleeting Note

## Raw Thought
Screenshot processed with OCR

## Content

This note was automatically generated from a screenshot. The image has been processed using OCR to extract text.

![Screenshot]({relative_path})

## Extracted Text

{extracted_text}

## Questions to Explore
- How can I use this information?
- What actions should I take based on this content?
- Are there any connections to my existing notes?
- Is there additional context I should add?

## Possible Next Steps
- Review the extracted text for accuracy
- Add additional context or thoughts
- Connect this information to related notes
- Convert to a permanent note if valuable
"""
    
    # Write the note to a file
    try:
        with open(note_path, 'w') as note_file:
            note_file.write(note_content)
        print(f"Note created successfully at: {note_path}")
        print(f"Screenshot saved at: {screenshot_path}")
        return True
    except Exception as e:
        print(f"Error creating note: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Process a screenshot and create a note in Second Brain')
    parser.add_argument('image_path', help='Path to the screenshot image')
    parser.add_argument('--title', help='Title for the note (optional)')
    
    args = parser.parse_args()
    
    # Check if the image exists
    if not os.path.exists(args.image_path):
        print(f"Error: Image not found at {args.image_path}")
        return 1
    
    # Process the screenshot
    success = create_note_from_screenshot(args.image_path, args.title)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 