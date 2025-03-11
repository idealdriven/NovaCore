#!/bin/bash

# Create directory structure for Second Brain

# Knowledge
mkdir -p Knowledge/Concepts/Core
mkdir -p Knowledge/Concepts/Derived
mkdir -p Knowledge/Facts/Verified
mkdir -p Knowledge/Facts/Unverified
mkdir -p Knowledge/Procedures
mkdir -p Knowledge/References

# Projects
mkdir -p Projects/Active
mkdir -p Projects/Completed

# Journal
mkdir -p Journal/Daily
mkdir -p Journal/Weekly
mkdir -p Journal/Monthly

# Resources
mkdir -p Resources/Books
mkdir -p Resources/Articles
mkdir -p Resources/Videos
mkdir -p Resources/Courses
mkdir -p Resources/Templates

# Notes
mkdir -p Notes/Fleeting
mkdir -p Notes/Permanent
mkdir -p Notes/Literature

# People
mkdir -p People/Personal
mkdir -p People/Professional

# Other main directories
mkdir -p Tags
mkdir -p Metadata
mkdir -p Archive

# Add placeholder files to ensure directories are tracked by Git
find . -type d -not -path "*/\.*" -not -path "./SecondBrainUI*" | while read dir; do
    # Skip if it's the root directory
    if [ "$dir" = "." ]; then
        continue
    fi
    
    # Check if directory is empty
    if [ -z "$(ls -A "$dir")" ]; then
        touch "$dir/.gitkeep"
        echo "Created placeholder in $dir"
    fi
done

echo "Directory structure created successfully!" 