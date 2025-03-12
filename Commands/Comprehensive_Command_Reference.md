# Comprehensive Second Brain Command Reference

This document contains all commands, prefixes, and phrases you can use to interact with your Second Brain through AI chat. It combines the core commands and all commands for the specialized folders.

## Natural Language Understanding

While this guide provides specific command formats, your AI assistant is designed to understand natural language requests even when you don't use the exact command format. The system will:

1. Analyze your message content and intent
2. Map it to the most appropriate command
3. Execute the relevant action
4. Confirm what was done

For example, saying "I had a thought about combining AI with blockchain" will be interpreted as a `[Thought]` command, even without the brackets.

See `Commands/Natural_Language_Understanding.md` for a comprehensive guide on how natural language requests are processed.

## Core Creation Commands

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

## Developer-Specific Commands

| Command/Prefix | Purpose | Example | Result |
|----------------|---------|---------|--------|
| **[Code: Language]** | Document code snippets | [Code: Python] Here's a pattern for implementing decorators... | Creates note in Knowledge/Procedures/CodeSnippets/ |
| **[CodeReview]** | Capture code review notes | [CodeReview] Reviewed authentication module, need to improve error handling. | Creates note in Projects/ or Knowledge/ |
| **[Library: Name]** | Document library usage | [Library: React] Notes on using React hooks effectively. | Creates note in Knowledge/Concepts/Programming/ |
| **[DevEnvironment]** | Document environment setup | [DevEnvironment] Steps to configure my development environment for this project. | Creates note in Resources/DevTools/ |
| **[Architecture]** | Document system design | [Architecture] The authentication flow works as follows... | Creates note in Projects/ or Knowledge/ |
| **[Debug: Issue]** | Track debugging insights | [Debug: Memory Leak] Discovered the cause was... | Creates note in Knowledge/Troubleshooting/ |

## Interests Commands

| Command/Prefix | Purpose | Example | Result |
|----------------|---------|---------|--------|
| **[Hobby: Name]** | Document hobby activities | [Hobby: Chess] Learned the Sicilian Defense opening. | Creates/updates note in Interests/Hobbies/ |
| **[Sport: Name]** | Track sports activities/interests | [Sport: Running] Completed 5K in 25 minutes today. | Creates/updates note in Interests/Sports/ |
| **[Art: Type]** | Document art interests | [Art: Painting] Discovered the work of Gerhard Richter. | Creates/updates note in Interests/Arts/ |
| **[Music: Genre/Artist]** | Track music interests | [Music: Jazz] Exploring Miles Davis discography. | Creates/updates note in Interests/Music/ |
| **[Literature: Genre/Author]** | Document reading interests | [Literature: Sci-Fi] Reading "Dune" by Frank Herbert. | Creates/updates note in Interests/Literature/ |
| **[Tech: Topic]** | Track technology interests | [Tech: AI] Learning about transformer architecture. | Creates/updates note in Interests/Technology/ |

## Personal Commands

| Command/Prefix | Purpose | Example | Result |
|----------------|---------|---------|--------|
| **[Dream]** | Record dreams | [Dream] I was flying over a city made of books. | Creates note in Personal/Dreams/ |
| **[Goal: Timeframe]** | Document personal goals | [Goal: 3 months] Complete Python certification. | Creates note in Personal/Goals/ |
| **[Fear]** | Document fears or concerns | [Fear] Public speaking makes me nervous because... | Creates note in Personal/Fears/ |
| **[Value]** | Document personal values | [Value] Integrity means always doing the right thing even when... | Creates note in Personal/Values/ |
| **[Reflection: Topic]** | Deep personal reflections | [Reflection: Career] My journey in tech has taught me... | Creates note in Personal/Reflections/ |

## Lifestyle Commands

| Command/Prefix | Purpose | Example | Result |
|----------------|---------|---------|--------|
| **[Recipe: Name]** | Document food recipes | [Recipe: Pasta Carbonara] Ingredients: eggs, pancetta... | Creates note in Lifestyle/Food/ |
| **[Restaurant: Name]** | Track restaurant experiences | [Restaurant: Nobu] Amazing sushi, great atmosphere. | Creates note in Lifestyle/Food/ |
| **[Cuisine: Type]** | Document cuisine interests | [Cuisine: Thai] Key ingredients and favorite dishes. | Creates note in Lifestyle/Food/ |
| **[Travel: Location]** | Document travel experiences | [Travel: Japan] Visited Tokyo and Kyoto in April. | Creates note in Lifestyle/Travel/ |
| **[Health: Topic]** | Track health information | [Health: Sleep] Improving sleep quality with these habits. | Creates note in Lifestyle/Health/ |
| **[Fitness: Activity]** | Document fitness activities | [Fitness: Strength] New workout routine for upper body. | Creates note in Lifestyle/Fitness/ |
| **[Fashion: Type]** | Track fashion interests | [Fashion: Minimalism] Building a capsule wardrobe. | Creates note in Lifestyle/Fashion/ |

## Media Commands

| Command/Prefix | Purpose | Example | Result |
|----------------|---------|---------|--------|
| **[Movie: Title]** | Document movie notes | [Movie: Inception] Analysis of dream layers and symbolism. | Creates note in Media/Movies/ |
| **[TV: Show]** | Document TV show notes | [TV: Breaking Bad] Character development in season 3. | Creates note in Media/TV Shows/ |
| **[Podcast: Name]** | Document podcast notes | [Podcast: Lex Fridman] Notes from interview with Richard Feynman. | Creates note in Media/Podcasts/ |
| **[Book: Title]** | Document book notes | [Book: Atomic Habits] Key takeaways on habit formation. | Creates note in Media/Books/ |
| **[Article: Title]** | Document article notes | [Article: The Future of AI] Summary and insights. | Creates note in Media/Articles/ |

## Professional Commands

| Command/Prefix | Purpose | Example | Result |
|----------------|---------|---------|--------|
| **[Career: Topic]** | Document career development | [Career: Promotion] Steps to prepare for next level. | Creates note in Professional/Career/ |
| **[Skill: Name]** | Track skill development | [Skill: Public Speaking] Techniques for managing anxiety. | Creates note in Professional/Skills/ |
| **[Network: Person/Event]** | Document networking | [Network: Tech Conference] Contacts made and follow-ups. | Creates note in Professional/Networking/ |
| **[Education: Topic]** | Track educational pursuits | [Education: MBA] Notes on financial accounting course. | Creates note in Professional/Education/ |

## Creativity Commands

| Command/Prefix | Purpose | Example | Result |
|----------------|---------|---------|--------|
| **[Idea: Topic]** | Capture creative ideas | [Idea: App] A meditation app that adapts to user's stress levels. | Creates note in Creativity/Ideas/ |
| **[Inspiration: Source]** | Document sources of inspiration | [Inspiration: Nature] How patterns in leaves could inspire UI design. | Creates note in Creativity/Inspiration/ |
| **[Creative Project: Name]** | Track creative projects | [Creative Project: Novel] Character development for protagonist. | Creates note in Creativity/Projects/ |
| **[Design: Type]** | Document design ideas | [Design: Logo] Sketches for personal brand identity. | Creates note in Creativity/Designs/ |

## Collections Commands

| Command/Prefix | Purpose | Example | Result |
|----------------|---------|---------|--------|
| **[Quote: Source]** | Collect meaningful quotes | [Quote: Marcus Aurelius] "The happiness of your life depends upon..." | Creates note in Collections/Quotes/ |
| **[Image: Description]** | Document image collections | [Image: Sunset] Collection of inspiring sunset photographs. | Creates note in Collections/Images/ |
| **[Video: Title/Creator]** | Document video collections | [Video: TED Talks] Favorite talks on creativity. | Creates note in Collections/Videos/ |
| **[Link: Topic]** | Collect useful links | [Link: Web Development] Useful resources for learning React. | Creates note in Collections/Links/ |

## Niche Topics Commands

| Command/Prefix | Purpose | Example | Result |
|----------------|---------|---------|--------|
| **[Philosophy: Branch/Thinker]** | Document philosophical ideas | [Philosophy: Stoicism] Practicing negative visualization. | Creates note in Niche Topics/Philosophy/ |
| **[Psychology: Concept]** | Document psychological concepts | [Psychology: Cognitive Biases] Understanding confirmation bias. | Creates note in Niche Topics/Psychology/ |
| **[Science: Field]** | Document scientific interests | [Science: Quantum Physics] Notes on entanglement. | Creates note in Niche Topics/Science/ |
| **[History: Period/Event]** | Document historical interests | [History: Renaissance] Key figures and innovations. | Creates note in Niche Topics/History/ |
| **[Language: Name]** | Track language learning | [Language: Spanish] Conjugation rules for irregular verbs. | Creates note in Niche Topics/Languages/ |
| **[Productivity: Method]** | Document productivity systems | [Productivity: Pomodoro] How I've adapted the technique. | Creates note in Niche Topics/Productivity/ |
| **[Mindfulness: Practice]** | Document mindfulness practices | [Mindfulness: Meditation] Body scan technique notes. | Creates note in Niche Topics/Mindfulness/ |
| **[Finance: Topic]** | Document financial knowledge | [Finance: Investing] Notes on index fund strategies. | Creates note in Niche Topics/Finance/ |

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

## Natural Language Understanding

Your AI assistant will recognize natural language cues to categorize content into the appropriate folders, even without explicit commands. For example:

- "I've been getting into chess lately..." → Interests/Hobbies/chess.md
- "Last night I dreamt about..." → Personal/Dreams/[date]_dream.md
- "Made an amazing pasta dish tonight..." → Lifestyle/Food/pasta_recipes.md
- "Just watched Inception and noticed..." → Media/Movies/inception.md
- "Planning my next career move toward..." → Professional/Career/career_planning.md
- "What if we created an app that..." → Creativity/Ideas/app_concepts.md
- "I love this line from Marcus Aurelius..." → Collections/Quotes/stoicism_quotes.md
- "The Stoic practice of negative visualization..." → Niche Topics/Philosophy/stoicism.md

See `Commands/Natural_Language_Understanding.md` for a comprehensive guide on natural language processing.

## Tips for Effective Commands

1. **Be specific** about exactly what you want
2. **Start with the appropriate prefix** for new content
3. **Include location information** when needed
4. **Mention related notes** to create connections
5. **Use multiple commands** for complex operations (I'll execute them in sequence)
6. **Ask for confirmation** if you're unsure about a major reorganization
7. **Provide feedback** about what works well and what doesn't

Remember that you can always use natural language to explain what you want. If a specific command doesn't exist for your needs, simply describe what you're looking for, and I'll help implement it. 