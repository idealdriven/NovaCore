# Your Second Brain

A structured knowledge management system designed to work effectively with AI assistants.

## 📋 Overview

This Second Brain is organized to help you capture, organize, and retrieve your knowledge in a way that's both human-friendly and optimized for AI understanding. The structure follows a hybrid approach inspired by various knowledge management systems like PARA, Zettelkasten, and others.

## 🚀 Installation

### From GitHub

1. Clone the repository:
   ```bash
   git clone https://github.com/sirioberati/SecondBrain.git
   ```

2. Navigate to the cloned directory:
   ```bash
   cd SecondBrain
   ```

3. Open the folder in Cursor:
   - Launch Cursor
   - Go to File > Open Folder
   - Select your cloned SecondBrain directory

4. Initialize Your Second Brain:
   - In Cursor, open the README.md file
   - Type the following command in the chat:
     ```
     start initializing Second Brain
     ```
   - This will trigger the AI assistant to help set up and manage your Second Brain

5. Start using the Second Brain structure by adding your own notes and knowledge.

### Requirements

- **AI Agents**: This Second Brain system works best with AI agents like [Cursor](https://cursor.sh/) that can help you manage and interact with your knowledge base.
- **Markdown Editor**: Any text editor that supports Markdown (VS Code, Obsidian, etc.)
- **Git**: For version control and synchronization (optional but recommended)

## 🗂️ Directory Structure

### 1. Knowledge

Where you store factual information and concepts.

- **Concepts/**
  - **Core/**: Fundamental ideas and principles you understand
  - **Derived/**: Concepts built upon core concepts, your own interpretations
- **Facts/**: Discrete pieces of information
  - **Verified/**: Facts with sources and verification
  - **Unverified/**: Information that needs more research
- **Procedures/**: How-to guides, processes, and methods
- **References/**: Citations, quotes, and external information sources

### 2. Projects

For task-oriented work with defined outcomes.

- **Active/**: Currently working on
- **Completed/**: Finished projects (keep here before moving to Archive)

### 3. Journal

For time-based reflections and thoughts.

- **Daily/**: Daily reflections, thoughts, and experiences
- **Weekly/**: Weekly summaries and insights
- **Monthly/**: Monthly reviews and bigger-picture reflections

### 4. Resources

Reference materials and learning content.

- **Books/**: Notes and summaries from books
- **Articles/**: Insights from articles you've read
- **Videos/**: Notes from videos, talks, and presentations
- **Courses/**: Learning materials from courses
- **Templates/**: Reusable formats for consistent note-taking

### 5. Notes

For capturing thoughts at different stages.

- **Fleeting/**: Quick, unprocessed thoughts (inbox)
- **Permanent/**: Refined, processed notes
- **Literature/**: Notes taken directly from sources

### 6. People

Information about individuals.

- **Personal/**: Friends, family, personal contacts
- **Professional/**: Colleagues, mentors, industry contacts

### 7. Tags

Cross-referencing system using text files named after tags.

### 8. Metadata

Information about your notes and system itself.

### 9. Archive

Inactive content that might be useful in the future.

## 📝 File Naming Conventions

For optimal AI understanding, use the following conventions:

1. **Use descriptive filenames**: `quantum_computing_basics.md` instead of `qc1.md`
2. **Include dates when relevant**: `2023-10-15_project_milestone.md`
3. **Use kebab-case or snake_case**: `machine-learning-fundamentals.md` or `machine_learning_fundamentals.md`
4. **Add prefixes for special categories**: `ref_Einstein_relativity.md`, `proc_making_sourdough.md`

## 🔖 Content Structure

For each note file, consider including:

```markdown
# Title

## Metadata
- Created: YYYY-MM-DD
- Modified: YYYY-MM-DD
- Tags: #tag1, #tag2, #tag3
- Related: [[linked-note-1]], [[linked-note-2]]

## Content
Your actual note content goes here.

## References
- Source 1
- Source 2
```

## 🤖 AI Enhancement Tips

To make your second brain more useful for AI interaction:

1. **Be consistent**: Use the same structure across notes
2. **Use clear language**: Avoid ambiguity and jargon unless defined
3. **Cross-reference**: Link related concepts and notes
4. **Include context**: Provide background information when needed
5. **Use metadata**: Tags, dates, categories help AI understand relationships
6. **Update regularly**: Keep your knowledge current and relevant

## 📱 Using Chat Agent Functionality

Your Second Brain can be updated directly through chat interactions with AI assistants like Claude. This provides a frictionless way to maintain your knowledge system without manually creating and editing files.

### Message Prefixes

Use these prefixes at the start of your messages to indicate content type:

#### Core Prefixes
- **[Daily]** - For daily journal entries
- **[Weekly]** - For weekly reviews
- **[Monthly]** - For monthly reflections
- **[Thought]** - For fleeting notes/quick thoughts
- **[Project: Name]** - For project updates
- **[Learning: Topic]** - For learning notes
- **[Creation: Name]** - For creative projects
- **[Screenshot]** - For processing screenshots with OCR

#### Additional Prefixes
- **[Concept]** - For concept notes
- **[Fact]** - For factual information
- **[Procedure]** - For how-to guides or methods
- **[Question]** - For research questions
- **[Meeting]** - For meeting notes
- **[Contact]** - For information about people
- **[Resource]** - For books, articles, videos
- **[Reflection]** - For deeper contemplation
- **[Tag]** - For creating/updating tag files

### Example Workflow

```
You: [Daily] Today I focused on the ML project. Energy: 7/10. Made progress on data preprocessing.

AI: Created journal entry at Journal/Daily/2023-10-21.md. Also updated Projects/Active/ml_project.md to reflect today's progress.

You: [Thought] What if we combined transformer architectures with reinforcement learning?

AI: Added your thought to Notes/Fleeting/transformer_rl_combination.md. Would you like to develop this into a more permanent note?
```

### Tips for Chat-Based Updates

1. **Include contextual details**: Mention related notes, tags, or where to store information
2. **Review and verify**: Periodically check that the AI has organized information correctly
3. **Follow up**: Ask the AI to help connect new notes to existing knowledge
4. **Use for processing**: Have the AI convert fleeting notes into permanent notes
5. **Request summaries**: Ask the AI to summarize sections of your Second Brain

## 📷 Screenshot Processing

Your Second Brain can now process screenshots and extract text using OCR (Optical Character Recognition). This feature allows you to:

1. **Capture information from images** and convert it to searchable text
2. **Automatically create notes** from screenshots
3. **Store screenshots** in an organized manner

### Using Screenshot Processing

To process a screenshot:

```bash
Commands/screenshot.sh /path/to/your/screenshot.png [--title "Optional Title"]
```

The system will:
- Extract text from the image using OCR
- Save a copy of the screenshot in `Resources/Screenshots/`
- Create a fleeting note with the extracted text

For detailed instructions, see [Commands/SCREENSHOT_PROCESSING.md](Commands/SCREENSHOT_PROCESSING.md).

## 🚀 Getting Started

1. Begin by adding a few notes to each main section
2. Create daily journal entries to build a habit
3. Process your fleeting notes into permanent notes weekly
4. Tag and cross-reference your notes as you create them
5. Review and update your system monthly

Remember, your Second Brain is a living system that will evolve as you use it. The most valuable second brain is one that you actively use and maintain!

## 👤 Creator

This Second Brain system was created by Sirio Berati.

- Instagram: [@heysirio](https://www.instagram.com/heysirio)
- GitHub: [sirioberati](https://github.com/sirioberati)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤖 Second Brain Agent Initialization Prompt

To initialize your Second Brain Agent in Cursor, use this command:
```
start initializing Second Brain
```

Then use the following prompt to initialize an AI assistant as your Second Brain Agent:

```
Act as my Second Brain Agent - an intelligent assistant that helps me capture, organize, connect, and retrieve knowledge using the Building a Second Brain methodology and PARA framework. You have the ability to create and edit files in my Second Brain system, understand my requests, and provide thoughtful responses that enhance my personal knowledge management.

Command prefix for initialization: "start initializing Second Brain"

Your core capabilities include:

1. CAPTURE: Create notes from my thoughts and ideas, enhancing them with additional context, connections, and structure.
   - Save fleeting notes in Notes/Fleeting/
   - Create structured notes in Knowledge/
   - Update project notes in Projects/
   - Add reference materials in Resources/
   - Maintain journal entries in Journal/

2. ORGANIZE: Structure information according to the PARA framework and add appropriate metadata.
   - Add consistent metadata (title, date, type, tags)
   - Use markdown formatting for better readability
   - Create meaningful file names
   - Suggest connections to existing notes

3. RETRIEVE: Help me find and use information I've previously captured.
   - Search for relevant notes when I ask questions
   - Summarize existing knowledge on topics
   - Connect ideas across different notes

4. ENHANCE: Add value to my raw thoughts by:
   - Expanding initial ideas into more detailed notes
   - Adding relevant questions to consider
   - Suggesting next steps or actions
   - Writing in a natural first-person voice as if I wrote it
   - Adding appropriate headers and structure

5. FILE OPERATIONS: Manage my knowledge base files by:
   - Creating new notes in the appropriate directories
   - Updating existing notes
   - Moving notes between directories when needed
   - Following proper file naming conventions (descriptive_kebab_case.md)

When I share a thought or idea, treat it as something to be captured in my Second Brain. Respond by creating a well-structured note with appropriate metadata, expanded content, and suggestions for connections or next steps. Always confirm when you've created or updated a file.

Always write notes in the first person as if I wrote them myself, while enhancing the content with thoughtful additions, questions, and structure. Notes should feel like natural extensions of my own thinking, not third-party analysis.

Follow these starting templates for different note types:

For fleeting notes:
```md
# [Topic] - Initial Thoughts

## Metadata
- Created: YYYY-MM-DD
- Tags: #tag1 #tag2 #tag3
- Status: Fleeting Note

## Raw Thought
[Original unedited thought exactly as expressed]

## Content

[Thoughtful reflection on the topic, including personal insights and considerations]

## Questions to Explore
- [Question 1 about how the idea might evolve or impact other areas]
- [Question 2 about potential implications or applications]
- [Question 3 about connections to other concepts]
- [Question 4 about personal relevance or implementation]

## Possible Next Steps
- [Action 1 to develop this thought further]
- [Action 2 for practical application]
- [Action 3 for integration with existing knowledge]
- [Action 4 for future exploration]
```

For project notes:
```md
---
title: "Project Name"
date: "YYYY-MM-DD"
type: "project"
status: "active"
tags: ["project", "tag1", "tag2"]
---

# Project: [Name]

## Objective
[What I'm trying to accomplish]

## Current Status
[Where things stand now]

## Next Actions
[Immediate next steps]

## Notes
[Ongoing thoughts about the project]
```

Remember, you're an extension of my thinking, designed to help me build a more robust and useful external thinking system.

Copy and paste this prompt at the beginning of a new conversation with your AI assistant in Cursor to initialize it as your Second Brain Agent.