# [Screenshot] Command

## Description
The `[Screenshot]` command allows you to process screenshots and extract text using OCR (Optical Character Recognition). This command helps you capture information from images and automatically create notes in your Second Brain.

## Usage

### Basic Format
```
[Screenshot] /path/to/your/screenshot.png
```

### With Custom Title
```
[Screenshot] /path/to/your/screenshot.png "Custom Title for the Note"
```

## Examples

Process a screenshot with an automatic title (based on filename):
```
[Screenshot] ~/Desktop/meeting_notes.png
```

Process a screenshot with a custom title:
```
[Screenshot] ~/Desktop/screenshot.png "Meeting Notes from Product Team"
```

## What It Does

When you use the `[Screenshot]` command:

1. The system extracts text from the image using OCR
2. It saves a copy of the screenshot in `Resources/Screenshots/`
3. It creates a new fleeting note in `Notes/Fleeting/` with:
   - The extracted text
   - A link to the saved screenshot
   - Metadata including creation date and tags
   - Questions to explore and possible next steps

## Requirements

To use this command, you need:
- Python 3
- Tesseract OCR
- Python packages: pytesseract and Pillow (automatically installed)

## Related Commands

- `[Thought]` - For capturing fleeting thoughts
- `[Daily]` - For daily journal entries

## See Also

For more detailed information about screenshot processing, see [SCREENSHOT_PROCESSING.md](SCREENSHOT_PROCESSING.md). 