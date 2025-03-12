#!/usr/bin/env python3
"""
Screenshot Command Handler for Second Brain

This script handles the [Screenshot] command in the chat interface.
It parses the command and calls the process_screenshot.py script.

Usage:
    python handle_screenshot_command.py "[Screenshot] /path/to/image.png"
    python handle_screenshot_command.py "[Screenshot] /path/to/image.png \"Custom Title\""
"""

import os
import sys
import re
import subprocess
import shlex

def parse_screenshot_command(command_text):
    """Parse the [Screenshot] command from chat."""
    # Remove the [Screenshot] prefix
    command_text = command_text.replace("[Screenshot]", "", 1).strip()
    
    # Check if there's a quoted title
    match = re.search(r'^(.*?)(?:\s+"([^"]+)")?$', command_text)
    
    if not match:
        return None, None
    
    image_path = match.group(1).strip()
    title = match.group(2) if match.group(2) else None
    
    return image_path, title

def handle_screenshot_command(command_text):
    """Handle the [Screenshot] command."""
    image_path, title = parse_screenshot_command(command_text)
    
    if not image_path:
        return "Error: Invalid screenshot command format. Please use: [Screenshot] /path/to/image.png"
    
    # Expand ~ to user's home directory
    image_path = os.path.expanduser(image_path)
    
    # Check if the image exists
    if not os.path.exists(image_path):
        return f"Error: Image not found at {image_path}"
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the process_screenshot.py script
    process_script = os.path.join(script_dir, "process_screenshot.py")
    
    # Build the command
    cmd = [sys.executable, process_script, image_path]
    if title:
        cmd.extend(["--title", title])
    
    try:
        # Run the process_screenshot.py script
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return f"Error processing screenshot: {result.stderr}"
        
        return result.stdout
    except Exception as e:
        return f"Error executing screenshot processing: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python handle_screenshot_command.py \"[Screenshot] /path/to/image.png\"")
        return 1
    
    command_text = sys.argv[1]
    
    if not command_text.startswith("[Screenshot]"):
        print("Error: Command must start with [Screenshot]")
        return 1
    
    result = handle_screenshot_command(command_text)
    print(result)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 