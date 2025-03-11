# Web UI Chat Interface Mockups

## Desktop View

```
+----------------------------------------------------------------------------------------------------+
|                                        SECOND BRAIN CHAT                              🌙 👤 ⚙️     |
+--------------------+-------------------------------------------------------------------------+
| 📁 SECOND BRAIN    |                                                                         |
| ├── Knowledge      |                                                                         |
| │   ├── Concepts   |                                                                         |
| │   ├── Facts      |                                                                         |
| │   └── Procedures |                                                                         |
| ├── Projects       |                                                                         |
| │   ├── Active     |   [AI Assistant]                                                        |
| │   └── Completed  |   Welcome to your Second Brain Chat Interface! How can I help           |
| ├── Journal        |   you today?                                                            |
| │   ├── Daily      |                                                                         |
| │   └── Weekly     |                                                                         |
| ├── Notes          |                                                                         |
| │   ├── Fleeting   |   [You]                                                                 |
| │   └── Permanent  |   I had a thought about combining machine learning with blockchain       |
| ├── Resources      |   for secure medical data sharing.                                      |
| └── Commands       |                                                                         |
|                    |                                                                         |
| 🔍 Search...       |   [AI Assistant]                                                        |
|                    |   I've captured your thought about combining ML with blockchain for     |
| RECENT NOTES       |   medical data sharing in Notes/Fleeting/ml_blockchain_medical.md       |
| > Daily Journal    |                                                                         |
| > ML Project       |   This seems like an interesting intersection of technologies.          |
| > React Hooks      |   Would you like me to:                                                 |
| > Meeting Notes    |   - Develop this into a concept note?                                   |
|                    |   - Connect it to your existing ML notes?                               |
|                    |   - Start a new project around this idea?                               |
|                    |                                                                         |
+--------------------+                                                                         |
|                      +-----------------------------------------------------------+           |
|                      | PREVIEW: Notes/Fleeting/ml_blockchain_medical.md          |           |
|                      |                                                           |           |
|                      | # ML + Blockchain for Medical Data                        |           |
|                      | Created: 2025-03-11                                       |           |
|                      | Tags: #machinelearning #blockchain #healthcare #privacy   |           |
|                      |                                                           |           |
|                      | Thought about combining machine learning with blockchain  |           |
|                      | for secure medical data sharing.                          |           |
|                      |                                                           |           |
|                      +-----------------------------------------------------------+           |
|                                                                                             |
+-------------------------------------------------------------------------+-------------------+
| Message...                                              [Commands ▼]    |       Send 🠕     |
+-------------------------------------------------------------------------+-------------------+
```

## Mobile View

```
+----------------------------------+
| SECOND BRAIN CHAT        ☰  👤  |
+----------------------------------+
|                                  |
| [AI Assistant]                   |
| Welcome to your Second Brain     |
| Chat Interface! How can I help   |
| you today?                       |
|                                  |
|                                  |
| [You]                            |
| I had a thought about combining  |
| machine learning with blockchain |
| for secure medical data sharing. |
|                                  |
|                                  |
| [AI Assistant]                   |
| I've captured your thought       |
| about combining ML with          |
| blockchain for medical data      |
| sharing in:                      |
|                                  |
| Notes/Fleeting/                  |
| ml_blockchain_medical.md         |
|                                  |
| This seems like an interesting   |
| intersection of technologies.    |
| Would you like me to:            |
|                                  |
| - Develop this into a concept    |
|   note?                          |
| - Connect it to your existing    |
|   ML notes?                      |
| - Start a new project around     |
|   this idea?                     |
|                                  |
|                                  |
+----------------------------------+
| Message...               Send 🠕 |
+----------------------------------+
```

## Command Autocomplete

```
+----------------------------------+
| Message... thought about AI eth  |
+----------------------------------+
| SUGGESTED COMMANDS:              |
| > [Thought] about AI ethics      |
| > [Concept] AI ethics            |
| > [Learning: AI] ethics          |
+----------------------------------+
|                          Send 🠕 |
+----------------------------------+
```

## Note Preview Panel

```
+----------------------------------+
| PREVIEW: project_status.md   [X] |
+----------------------------------+
| # ML Research Project           |
| Status: In Progress             |
| Last Updated: 2025-03-10        |
|                                 |
| ## Current Tasks                |
| - [x] Literature review         |
| - [ ] Data preprocessing        |
| - [ ] Model selection           |
|                                 |
| ## Notes                        |
| Found promising approach in     |
| paper by Smith et al. (2024)    |
+----------------------------------+
```

## Search Results

```
+----------------------------------+
| 🔍 machine learning              |
+----------------------------------+
| RESULTS:                         |
|                                  |
| Knowledge/Concepts/              |
| machine_learning_basics.md       |
| Last updated: 2025-02-15         |
|                                  |
| Projects/Active/                 |
| ml_research_project.md           |
| Last updated: 2025-03-10         |
|                                  |
| Notes/Fleeting/                  |
| ml_blockchain_medical.md         |
| Last updated: 2025-03-11         |
|                                  |
| Resources/Books/                 |
| hands_on_ml.md                   |
| Last updated: 2025-01-20         |
+----------------------------------+
```

## Action Notifications

```
+----------------------------------+
| ✅ Note Created                  |
| Notes/Fleeting/ml_blockchain.md  |
+----------------------------------+
```

```
+----------------------------------+
| 🔄 Processing Request...         |
+----------------------------------+
```

```
+----------------------------------+
| 🔗 Connected to existing notes:  |
| - machine_learning_basics.md     |
| - blockchain_fundamentals.md     |
+----------------------------------+
```

## Theme Toggle

```
+----------------------------------+
| COLOR THEME                    |
|                                |
| ⚪ Light                       |
| ⚫ Dark                        |
| 🌓 System                      |
+----------------------------------+
```

## Login Screen

```
+----------------------------------+
|        SECOND BRAIN CHAT         |
+----------------------------------+
|                                  |
|      🧠                         |
|                                  |
|  Welcome to your Second Brain    |
|                                  |
| +----------------------------+   |
| | Username                   |   |
| +----------------------------+   |
|                                  |
| +----------------------------+   |
| | Password                   |   |
| +----------------------------+   |
|                                  |
| +----------------------------+   |
| |          Log In           |   |
| +----------------------------+   |
|                                  |
|  Remember me on this device      |
|                                  |
+----------------------------------+
```

## Implementation Notes

1. **Responsive Design**
   - File browser collapses to hamburger menu on mobile
   - Preview panel appears as modal on mobile
   - Message bubbles stack vertically on all devices

2. **Accessibility Features**
   - High contrast mode option
   - Keyboard navigation support
   - Screen reader compatible elements
   - Customizable text size

3. **Interactive Elements**
   - Clickable file paths open previews
   - Clickable suggestions execute commands
   - Long-press on mobile for context menus
   - Swipe gestures for navigation on mobile 