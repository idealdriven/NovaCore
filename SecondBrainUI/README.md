# Second Brain UI

A desktop application for interacting with your Second Brain knowledge management system.

## Features

- **Chat Interface**: Interact with your Second Brain using natural language and command prefixes
- **File Explorer**: Browse and navigate your Second Brain directory structure
- **Note Viewer/Editor**: View and edit markdown notes directly in the application
- **Local-first**: All data is stored locally in your Second Brain directory

## Commands

The application supports various commands through the chat interface:

- **[Thought] your thought here** - Creates a new fleeting note with your thought
- **[Daily] your daily note** - Adds content to today's daily note
- **[Weekly] your weekly note** - Adds content to this week's note
- **[Monthly] your monthly note** - Adds content to this month's note
- **[Project: Project Name] update** - Updates a specific project note
- **Find notes about topic** - Searches for notes related to a topic

See the full list of commands in your Second Brain's Commands directory.

## Development

### Prerequisites

- Node.js 16+
- npm or yarn

### Setup

1. Clone the repository
2. Install dependencies:
   ```
   npm install
   ```
3. Start the development server:
   ```
   npm run electron-dev
   ```

### Building

To build the application for your platform:

```
npm run dist
```

This will create an installer in the `dist` directory.

## License

MIT 