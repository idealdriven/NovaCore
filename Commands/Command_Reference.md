# Second Brain Command Reference

This document contains all the commands, prefixes, and phrases you can use to interact with your Second Brain through AI chat. Use this as a quick reference when you're unsure of how to ask for specific actions.

## Natural Language Understanding

While this guide provides specific command formats, your AI assistant is designed to understand natural language requests even when you don't use the exact command format. The system will:

1. Analyze your message content and intent
2. Map it to the most appropriate command
3. Execute the relevant action
4. Confirm what was done

For example, saying "I had a thought about combining AI with blockchain" will be interpreted as a `[Thought]` command, even without the brackets.

See `Commands/Natural_Language_Understanding.md` for a comprehensive guide on how natural language requests are processed.

## Content Creation Commands

### Core Creation Prefixes

| Command/Prefix | Purpose | Example | Result |
|----------------|---------|---------|--------|
| **[Daily]** | Create daily journal entry | [Daily] Energy: 8/10. Today I learned about neural networks. | Creates entry in Journal/Daily/ |
| **[Weekly]** | Create weekly review | [Weekly] Completed project X, started learning Y. | Creates entry in Journal/Weekly/ |
| **[Monthly]** | Create monthly reflection | [Monthly] Key achievements: finished course Z. | Creates entry in Journal/Monthly/ |
| **[Thought]** | Capture quick ideas | [Thought] What if we combined X and Y technologies? | Creates note in Notes/Fleeting/ |
| **[Project: Name]** | Update project | [Project: Website] Completed wireframes, starting on frontend. | Updates file in Projects/Active/ |
| **[Learning: Topic]** | Document learning | [Learning: Python] Today I learned about decorators. | Creates note in Knowledge/ or Resources/ |
| **[Creation: Name]** | Track creative work | [Creation: Novel] Developed character arcs for chapter 3. | Creates/updates in Projects/Active/ |
| **[Concept]** | Capture concept | [Concept] The flywheel effect in business refers to... | Creates note in Knowledge/Concepts/ |
| **[Fact]** | Record factual info | [Fact] 60% of the human body is water. | Creates note in Knowledge/Facts/ |
| **[Procedure]** | Document methods | [Procedure] How to set up Docker on MacOS. | Creates note in Knowledge/Procedures/ |
| **[Question]** | Note research questions | [Question] How do quantum computers handle error correction? | Creates note in Notes/Fleeting/ |
| **[Meeting: Topic]** | Record meeting notes | [Meeting: Team Sync] Discussed roadmap, assigned tasks. | Creates note in appropriate project folder |
| **[Contact]** | Log contact info | [Contact] Met Jane Doe, AI researcher at X company. | Creates note in People/ |
| **[Resource]** | Note learning resources | [Resource] Book: "Thinking Fast and Slow" by Kahneman. | Creates note in Resources/ |
| **[Reflection]** | Deeper contemplation | [Reflection] How my understanding of AI has evolved. | Creates note in Notes/Permanent/ |
| **[Tag]** | Create/update tags | [Tag] #productivity should include time management. | Updates file in Tags/ |

### Developer-Specific Prefixes

| Command/Prefix | Purpose | Example | Result |
|----------------|---------|---------|--------|
| **[Code: Language]** | Document code snippets | [Code: Python] Here's a pattern for implementing decorators... | Creates note in Knowledge/Procedures/CodeSnippets/ |
| **[CodeReview]** | Capture code review notes | [CodeReview] Reviewed authentication module, need to improve error handling. | Creates note in Projects/ or Knowledge/ |
| **[Library: Name]** | Document library usage | [Library: React] Notes on using React hooks effectively. | Creates note in Knowledge/Concepts/Programming/ |
| **[DevEnvironment]** | Document environment setup | [DevEnvironment] Steps to configure my development environment for this project. | Creates note in Resources/DevTools/ |
| **[Architecture]** | Document system design | [Architecture] The authentication flow works as follows... | Creates note in Projects/ or Knowledge/ |
| **[Debug: Issue]** | Track debugging insights | [Debug: Memory Leak] Discovered the cause was... | Creates note in Knowledge/Troubleshooting/ |

## Processing Commands

| Command | Purpose | Example | 
|---------|---------|---------|
| **[Process]** | Convert fleeting to permanent | [Process] Please develop my fleeting note on AI ethics into a permanent note. | 
| **Please convert** | Move note to new location | Please convert my fleeting note about X into a concept note in Knowledge/Concepts/. |
| **Develop this note** | Expand with more content | Develop this note about machine learning with more details on neural networks. |
| **Move this note** | Change location | Move this note to Projects/Active/ and format as a project plan. |
| **Combine notes** | Merge related notes | Please combine my notes on Docker and containerization into a single comprehensive note. |
| **Split this note** | Divide into multiple | Split this note into separate notes for each ML algorithm covered. |

## Specialized Commands for Cursor Integration

| Command | Purpose | Example | 
|---------|---------|---------|
| **Connect to codebase** | Link notes to code | Connect this note to my authentication service codebase. | 
| **Implement based on** | Use notes for implementation | Implement a login function based on my security notes in Knowledge/Concepts/Programming/. |
| **Document this code** | Create notes from code | Document this authentication code in my Second Brain under Projects/Active/auth_service/. |
| **Refactor using** | Apply concepts to code | Refactor this function using the design patterns in my Knowledge/Concepts/Programming/ notes. |
| **Update documentation** | Sync docs with changes | Update my API documentation notes based on the changes we just made to the code. |
| **Extract concepts from** | Learn from code | Extract key concepts from this code snippet and add them to my Second Brain. |

## Retrieval and Search Commands

| Command | Purpose | Example |
|---------|---------|---------|
| **Find notes about** | Search by topic | Find notes about machine learning in my Second Brain. |
| **Show me all** | List category | Show me all my project notes. |
| **What do I know about** | Knowledge query | What do I know about quantum computing based on my notes? |
| **Summarize my notes on** | Get summary | Summarize my notes on productivity systems. |
| **List all notes tagged** | Search by tag | List all notes tagged with #AI. |
| **Find connections between** | Discover relationships | Find connections between my notes on psychology and marketing. |

## Organization and Maintenance Commands

| Command | Purpose | Example |
|---------|---------|---------|
| **Review my notes** | Assessment | Review my notes on machine learning and suggest improvements. |
| **Help me organize** | Restructure | Help me organize my scattered notes on programming languages. |
| **Create a map of content for** | Generate overview | Create a map of content for my AI-related notes. |
| **Update metadata** | Refresh info | Update metadata for all notes in the Knowledge/Concepts/ directory. |
| **Archive** | Move to archive | Archive my completed project on website redesign. |
| **Check for orphaned notes** | Find disconnected | Check for orphaned notes in my Second Brain. |
| **Suggest connections for** | Find relationships | Suggest connections for my note on neural networks. |

## Contextual Directives

Include these phrases within your commands for additional context:

| Directive | Purpose | Example |
|-----------|---------|---------|
| **Store in [location]** | Specify location | [Thought] Store this in Knowledge/Concepts/ instead of fleeting notes. |
| **Connect to [notes]** | Create links | Connect this to my notes on machine learning and neural networks. |
| **Add tags** | Specify tags | Add tags #productivity #GTD #habits to this note. |
| **Format as** | Specify format | Format this as a step-by-step guide with numbered steps. |
| **Priority: [level]** | Add priority | Priority: High - need to review this concept soon. |
| **Develop further with** | Add content | Develop further with examples and case studies. |

## Weekly and Monthly Review Commands

| Command | Purpose | Example |
|---------|---------|---------|
| **Weekly review** | Process week | Please help me conduct my weekly review for the past week. |
| **Monthly review** | Process month | It's time for my monthly review for March 2025. |
| **Process my fleeting notes** | Organize | Please process all my fleeting notes from this week. |
| **Create a summary of** | Summarize period | Create a summary of my journal entries from the past month. |
| **Identify patterns in** | Find trends | Identify patterns in my daily journals from the past two weeks. |

## AI Assistance Commands

| Command | Purpose | Example |
|---------|---------|---------|
| **Suggest improvements for** | Enhancement | Suggest improvements for my note structure on programming concepts. |
| **Help me understand** | Explanation | Help me understand how these concepts connect based on my notes. |
| **Analyze my notes on** | Analysis | Analyze my notes on productivity and identify gaps in my system. |
| **Research and add** | Expansion | Research and add more information about quantum computing to my existing note. |
| **Suggest a project based on** | Ideation | Suggest a project based on my notes about data visualization. |

## Complete Examples of Complex Commands

### Processing Fleeting Notes into Structured Content
```
[Process] Please review my fleeting note about reinforcement learning. Develop it into a comprehensive concept note in Knowledge/Concepts/Core/, add connections to my existing notes on neural networks and decision theory, and include a section on practical applications. Also update the #machine-learning tag to include this new note.
```

### Creating Project from Existing Notes
```
Please create a new project called "Build Personal Dashboard" in Projects/Active/ based on my existing notes about data visualization, personal metrics, and web development. Format it with clear objectives, resource requirements, and a phased implementation plan.
```

### Comprehensive Weekly Review
```
[Weekly] Please help with my weekly review: Summarize key points from my daily journals, process any remaining fleeting notes into appropriate permanent locations, update my project status notes for "ML Course" and "Website Redesign", and suggest any new connections between notes I created this week.
```

### Creating Learning Pathway
```
Based on my notes tagged with #artificial-intelligence, create a learning pathway in Knowledge/Procedures/ that outlines a structured approach to deepening my understanding, starting with foundational concepts I already know and progressing to advanced topics I've shown interest in.
```

## Tips for Effective Commands

1. **Be specific** about exactly what you want
2. **Start with the appropriate prefix** for new content
3. **Include location information** when needed
4. **Mention related notes** to create connections
5. **Use multiple commands** for complex operations (I'll execute them in sequence)
6. **Ask for confirmation** if you're unsure about a major reorganization
7. **Provide feedback** about what works well and what doesn't

Remember that you can always use natural language to explain what you want. If a specific command doesn't exist for your needs, simply describe what you're looking for, and I'll help implement it.

## Second Brain Agent Initialization Prompt

To fully initialize an AI assistant (like Claude in Cursor) as your Second Brain Agent, you can use a special initialization prompt. This prompt configures the AI to understand its role in managing your Second Brain system and provides it with comprehensive instructions.

### When to Use the Initialization Prompt

Use this prompt when:
- Starting a new conversation with an AI assistant in Cursor
- Wanting to ensure the AI has complete understanding of its role as a Second Brain Agent
- Needing to reset or clarify the AI's understanding of your Second Brain system

### How to Use the Initialization Prompt

1. Copy the full prompt from the README.md file (under the "Second Brain Agent Initialization Prompt" section)
2. Paste it at the beginning of a new conversation with your AI assistant in Cursor
3. The assistant will confirm it understands its role and is ready to help you manage your Second Brain

### Benefits of Using the Initialization Prompt

- Ensures consistent handling of your Second Brain across conversations
- Provides the AI with complete context about your system's structure
- Configures the AI to write in your voice when creating notes
- Sets clear expectations for how files should be enhanced and structured
- Establishes templates for different note types
- Configures the AI to act proactively in organizing and connecting your knowledge

See the full prompt in the README.md file in the root directory of your Second Brain system. 