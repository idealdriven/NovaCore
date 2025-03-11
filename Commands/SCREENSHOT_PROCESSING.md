# Screenshot Processing for Second Brain

This feature allows you to extract text from screenshots and automatically create notes in your Second Brain system.

## Prerequisites

Before using this feature, you need to install:

1. **Python 3**: The script requires Python 3.6 or later
2. **Tesseract OCR**: The OCR engine used to extract text from images

### Installation Instructions

#### Tesseract OCR Installation

- **macOS**:
  ```
  brew install tesseract
  ```

- **Ubuntu/Debian**:
  ```
  sudo apt-get install tesseract-ocr
  ```

- **Windows**:
  Download and install from https://github.com/UB-Mannheim/tesseract/wiki

#### Python Dependencies

The script will automatically install the required Python packages (`pytesseract` and `Pillow`) if they're not already installed.

## Usage

### Command Line

You can process a screenshot from the command line using:

```bash
# From the Second Brain root directory
Commands/screenshot.sh /path/to/your/screenshot.png [--title "Optional Title"]
```

Or:

```bash
# From any directory
/path/to/Second/Brain/Commands/screenshot.sh /path/to/your/screenshot.png
```

### Examples

Process a screenshot with an automatic title (based on filename):
```bash
Commands/screenshot.sh ~/Desktop/meeting_notes.png
```

Process a screenshot with a custom title:
```bash
Commands/screenshot.sh ~/Desktop/screenshot.png --title "Meeting Notes from Product Team"
```

## How It Works

1. The script takes a screenshot image as input
2. It uses Tesseract OCR to extract text from the image
3. It creates a copy of the screenshot in `Resources/Screenshots/`
4. It generates a new fleeting note in `Notes/Fleeting/` with:
   - The extracted text
   - A link to the saved screenshot
   - Metadata including creation date and tags
   - Questions to explore and possible next steps

## Output

The script will create:

1. A copy of your screenshot in `Resources/Screenshots/`
2. A new note in `Notes/Fleeting/` with the extracted text

## Troubleshooting

If you encounter issues:

- Ensure Tesseract OCR is properly installed
- Check that the image is clear and contains readable text
- For poor OCR results, try improving the image quality or contrast
- Make sure you have write permissions in your Second Brain directory

## Integration with Second Brain UI

In future updates, this functionality will be integrated directly into the Second Brain UI application for a more seamless experience. 