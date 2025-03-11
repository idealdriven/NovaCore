#!/bin/bash

# Second Brain Web UI Setup Script
echo "Setting up Second Brain Web UI..."

# Create project directories
mkdir -p second-brain-web/client second-brain-web/server
cd second-brain-web

# Initialize backend (Express)
echo "Setting up backend..."
cd server

# Create package.json
cat > package.json << EOL
{
  "name": "second-brain-server",
  "version": "1.0.0",
  "description": "Backend server for Second Brain Web UI",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "keywords": [
    "second-brain",
    "express",
    "api"
  ],
  "author": "",
  "license": "MIT"
}
EOL

# Create .env file
cat > .env << EOL
PORT=5000
OPENAI_API_KEY=your_openai_api_key_here
SECOND_BRAIN_DIR=$(pwd)/../../
EOL

# Create directories
mkdir -p controllers routes services utils

# Create server.js
cat > server.js << EOL
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables
dotenv.config();

// Create Express app
const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// Basic route
app.get('/api', (req, res) => {
  res.json({ message: 'Second Brain API is running' });
});

// Start server
app.listen(PORT, () => {
  console.log(\`Server running on port \${PORT}\`);
});
EOL

# Create services directory structure
mkdir -p services
cat > services/intentDetector.js << EOL
/**
 * Detects intent from user message
 * @param {string} message - User message
 * @returns {Object} Intent object
 */
exports.detectIntent = (message) => {
  // Basic command detection logic
  const dailyMatch = message.match(/^\[Daily\](.*)/i);
  const thoughtMatch = message.match(/^\[Thought\](.*)/i);
  const projectMatch = message.match(/^\[Project: (.*?)\](.*)/i);
  
  if (dailyMatch) {
    return {
      command: 'daily',
      content: dailyMatch[1].trim(),
      args: {}
    };
  } else if (thoughtMatch) {
    return {
      command: 'thought',
      content: thoughtMatch[1].trim(),
      args: {}
    };
  } else if (projectMatch) {
    return {
      command: 'project',
      content: projectMatch[2].trim(),
      args: {
        name: projectMatch[1].trim()
      }
    };
  }
  
  // Natural language understanding (simplified)
  if (message.toLowerCase().includes('i had a thought') || 
      message.toLowerCase().includes('i was thinking')) {
    return {
      command: 'thought',
      content: message,
      args: {},
      isNaturalLanguage: true
    };
  }
  
  // No command detected
  return {
    command: null,
    content: message,
    args: {}
  };
};
EOL

cat > services/commandProcessor.js << EOL
const fs = require('fs-extra');
const path = require('path');

/**
 * Process a command based on detected intent
 * @param {Object} intent - Intent object from intentDetector
 * @param {string} secondBrainDir - Path to Second Brain directory
 * @returns {Object} Command result
 */
exports.processCommand = async (intent, secondBrainDir) => {
  const { command, content, args, isNaturalLanguage } = intent;
  
  // Handle different commands
  switch (command) {
    case 'daily':
      return await createDailyJournal(content, secondBrainDir);
    case 'thought':
      return await createFleetingNote(content, secondBrainDir);
    case 'project':
      return await updateProject(content, args.name, secondBrainDir);
    default:
      return {
        success: false,
        description: "No command action taken"
      };
  }
};

// Create daily journal entry
async function createDailyJournal(content, secondBrainDir) {
  try {
    const today = new Date();
    const dateString = today.toISOString().split('T')[0]; // YYYY-MM-DD
    const journalDir = path.join(secondBrainDir, 'Journal', 'Daily');
    const filePath = path.join(journalDir, \`\${dateString}.md\`);
    
    // Create directory if it doesn't exist
    await fs.ensureDir(journalDir);
    
    // Create frontmatter
    const frontmatter = \`---
date: \${today.toISOString()}
type: daily
---

# Daily Journal: \${dateString}

\${content}
\`;

    // Write file
    await fs.writeFile(filePath, frontmatter);
    
    return {
      success: true,
      description: \`Created daily journal for \${dateString}\`,
      path: \`Journal/Daily/\${dateString}.md\`
    };
  } catch (error) {
    console.error('Error creating daily journal:', error);
    return {
      success: false,
      description: "Failed to create daily journal",
      error: error.message
    };
  }
}

// Create fleeting note
async function createFleetingNote(content, secondBrainDir) {
  try {
    const now = new Date();
    const timestamp = now.getTime();
    const fleetingDir = path.join(secondBrainDir, 'Notes', 'Fleeting');
    const filePath = path.join(fleetingDir, \`\${timestamp}.md\`);
    
    // Create directory if it doesn't exist
    await fs.ensureDir(fleetingDir);
    
    // Create frontmatter
    const frontmatter = \`---
created: \${now.toISOString()}
type: fleeting
---

# Fleeting Note

\${content}
\`;

    // Write file
    await fs.writeFile(filePath, frontmatter);
    
    return {
      success: true,
      description: "Created fleeting note",
      path: \`Notes/Fleeting/\${timestamp}.md\`
    };
  } catch (error) {
    console.error('Error creating fleeting note:', error);
    return {
      success: false,
      description: "Failed to create fleeting note",
      error: error.message
    };
  }
}

// Update project
async function updateProject(content, projectName, secondBrainDir) {
  try {
    const now = new Date();
    const projectDir = path.join(secondBrainDir, 'Projects', 'Active');
    const filePath = path.join(projectDir, \`\${projectName.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.md\`);
    
    // Create directory if it doesn't exist
    await fs.ensureDir(projectDir);
    
    // Check if file exists
    const exists = await fs.pathExists(filePath);
    
    if (exists) {
      // Append to existing file
      const existingContent = await fs.readFile(filePath, 'utf8');
      const updatedContent = \`\${existingContent}

## Update: \${now.toISOString()}

\${content}
\`;
      await fs.writeFile(filePath, updatedContent);
      
      return {
        success: true,
        description: \`Updated project "\${projectName}"\`,
        path: \`Projects/Active/\${path.basename(filePath)}\`
      };
    } else {
      // Create new file
      const newContent = \`---
created: \${now.toISOString()}
updated: \${now.toISOString()}
type: project
name: \${projectName}
status: active
---

# Project: \${projectName}

## Update: \${now.toISOString()}

\${content}
\`;
      await fs.writeFile(filePath, newContent);
      
      return {
        success: true,
        description: \`Created new project "\${projectName}"\`,
        path: \`Projects/Active/\${path.basename(filePath)}\`
      };
    }
  } catch (error) {
    console.error('Error updating project:', error);
    return {
      success: false,
      description: "Failed to update project",
      error: error.message
    };
  }
}
EOL

# Go back to project root
cd ..

# Set up frontend with Create React App
echo "Setting up frontend..."
npx create-react-app client

cd client

# Create .env file
cat > .env << EOL
REACT_APP_API_URL=http://localhost:5000/api
EOL

# Update package.json to add dependencies
npx npm-add-script \
  -k "dependencies.axios" -v "^1.3.5" \
  -k "dependencies.react-markdown" -v "^8.0.7" \
  -k "dependencies.react-syntax-highlighter" -v "^15.5.0" \
  -k "dependencies.tailwindcss" -v "^3.3.2" \
  -k "dependencies.@headlessui/react" -v "^1.7.14" \
  -k "devDependencies.postcss" -v "^8.4.23" \
  -k "devDependencies.autoprefixer" -v "^10.4.14"

# Create directories
mkdir -p src/components/Chat src/components/FileBrowser src/services

# Create services directory
cat > src/services/api.js << EOL
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatService = {
  sendMessage: (message) => api.post('/chat/message', { message }),
  getHistory: () => api.get('/chat/history'),
};

export const fileService = {
  getStructure: () => api.get('/files/structure'),
  getFileContent: (filePath) => api.get('/files/content', { params: { filePath } }),
  createNote: (content, filePath, tags) => api.post('/files/note', { content, filePath, tags }),
};

export default api;
EOL

# Create a simple App.js
cat > src/App.js << EOL
import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Second Brain Web UI</h1>
        <p>
          Your chat interface for knowledge management is being set up.
        </p>
        <p>
          Follow the implementation guide to complete the setup.
        </p>
      </header>
    </div>
  );
}

export default App;
EOL

# Go back to project root
cd ..

# Create README
cat > README.md << EOL
# Second Brain Web UI

A web-based chat interface for your Second Brain knowledge management system.

## Getting Started

1. Install dependencies:

\`\`\`bash
# Install backend dependencies
cd server
npm install

# Install frontend dependencies
cd ../client
npm install
\`\`\`

2. Configure environment variables:

Edit \`server/.env\` to set your OpenAI API key and Second Brain directory path.

3. Start the development servers:

\`\`\`bash
# Start backend
cd server
npm run dev

# In another terminal, start frontend
cd client
npm start
\`\`\`

4. Open your browser to [http://localhost:3000](http://localhost:3000) to see the web UI.

## Implementation Guide

Refer to the implementation guide document for details on how to complete the setup
and customize the application.

## Features

- Chat interface for interacting with your Second Brain
- File browser for viewing your knowledge base
- Command processing for knowledge management
- Natural language understanding
- Markdown rendering with syntax highlighting

## Next Steps

After basic setup, consider implementing:

1. Command auto-detection and suggestion
2. Authentication
3. Search functionality
4. UI enhancements
5. Mobile responsiveness
6. Dark mode
7. File editing
8. Tag support
EOL

echo "Project setup complete! Next steps:"
echo "1. Navigate to the project directory: cd second-brain-web"
echo "2. Install dependencies for both frontend and backend"
echo "3. Follow the implementation guide to complete the setup" 