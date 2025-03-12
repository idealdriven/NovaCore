# Second Brain Web UI - Implementation Guide

> **IMPORTANT UPDATE**: While this guide describes a client/server web application architecture, the current implementation has evolved to use Electron for a desktop application approach. Please refer to the SecondBrainUI directory and its documentation for the actual implementation details. This document is kept for reference purposes.

This guide will walk you through implementing a basic version of the Web UI chat interface for your Second Brain system. We'll focus on creating a minimal viable product (MVP) that demonstrates the core functionality.

## Project Structure

```
second-brain-web/
├── client/                 # React frontend
│   ├── public/
│   │   ├── index.html
│   │   └── ...
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── contexts/       # State management
│   │   ├── services/       # API services
│   │   ├── App.js          # Main app component
│   │   └── index.js        # Entry point
│   ├── package.json
│   └── ...
├── server/                 # Express backend
│   ├── controllers/        # Route handlers
│   ├── middleware/         # Middleware functions
│   ├── routes/             # API routes
│   ├── services/           # Business logic
│   ├── utils/              # Utility functions
│   ├── .env                # Environment variables
│   ├── package.json
│   └── server.js           # Entry point
└── README.md
```

## Step 1: Set Up the Project

### Create Project Directories

```bash
# Create project folder
mkdir -p second-brain-web/client second-brain-web/server
cd second-brain-web
```

### Initialize Frontend (React)

```bash
# Create React app
npx create-react-app client
cd client

# Install dependencies
npm install axios react-markdown react-syntax-highlighter tailwindcss @headlessui/react
npm install -D postcss autoprefixer

# Initialize Tailwind CSS
npx tailwindcss init -p

# Go back to project root
cd ..
```

### Initialize Backend (Express)

```bash
# Move to server directory
cd server

# Initialize package.json
npm init -y

# Install dependencies
npm install express cors dotenv openai body-parser jsonwebtoken bcrypt fs-extra markdown-it

# Development dependencies
npm install -D nodemon

# Go back to project root
cd ..
```

## Step 2: Configure Backend

### Create Server Entry Point (server/server.js)

```javascript
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

// Import routes
const chatRoutes = require('./routes/chat');
const fileRoutes = require('./routes/files');

// Use routes
app.use('/api/chat', chatRoutes);
app.use('/api/files', fileRoutes);

// Basic route
app.get('/api', (req, res) => {
  res.json({ message: 'Second Brain API is running' });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

### Create Chat Routes (server/routes/chat.js)

```javascript
const express = require('express');
const router = express.Router();
const chatController = require('../controllers/chatController');

// Process a chat message
router.post('/message', chatController.processMessage);

// Get chat history
router.get('/history', chatController.getChatHistory);

module.exports = router;
```

### Create File Routes (server/routes/files.js)

```javascript
const express = require('express');
const router = express.Router();
const fileController = require('../controllers/fileController');

// Get directory structure
router.get('/structure', fileController.getDirectoryStructure);

// Get file content
router.get('/content', fileController.getFileContent);

// Create a new note
router.post('/note', fileController.createNote);

module.exports = router;
```

### Create Chat Controller (server/controllers/chatController.js)

```javascript
const fs = require('fs-extra');
const path = require('path');
const OpenAI = require('openai');
const { processCommand } = require('../services/commandProcessor');
const { detectIntent } = require('../services/intentDetector');

// Initialize OpenAI
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Path to Second Brain directory
const SECOND_BRAIN_DIR = process.env.SECOND_BRAIN_DIR || path.join(__dirname, '../../second-brain');

// Process a chat message
exports.processMessage = async (req, res) => {
  try {
    const { message } = req.body;
    
    // Detect intent from message
    const intent = detectIntent(message);
    
    // Process command if detected
    let commandResult = null;
    if (intent.command) {
      commandResult = await processCommand(intent, SECOND_BRAIN_DIR);
    }
    
    // Generate AI response
    const aiResponse = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        { role: "system", content: "You are an assistant for a Second Brain knowledge management system." },
        { role: "user", content: message }
      ],
    });
    
    // Format response
    const response = {
      message: aiResponse.choices[0].message.content,
      action: commandResult,
      intent: intent,
    };
    
    res.json(response);
  } catch (error) {
    console.error('Error processing message:', error);
    res.status(500).json({ error: 'Failed to process message' });
  }
};

// Get chat history
exports.getChatHistory = (req, res) => {
  // In a real implementation, this would fetch from a database
  res.json({ 
    history: [
      { role: 'assistant', content: 'Welcome to your Second Brain! How can I help you today?' }
    ] 
  });
};
```

### Create File Controller (server/controllers/fileController.js)

```javascript
const fs = require('fs-extra');
const path = require('path');
const markdownIt = require('markdown-it');

// Path to Second Brain directory
const SECOND_BRAIN_DIR = process.env.SECOND_BRAIN_DIR || path.join(__dirname, '../../second-brain');
const md = new markdownIt();

// Get directory structure
exports.getDirectoryStructure = async (req, res) => {
  try {
    const structure = await buildDirectoryTree(SECOND_BRAIN_DIR);
    res.json(structure);
  } catch (error) {
    console.error('Error getting directory structure:', error);
    res.status(500).json({ error: 'Failed to get directory structure' });
  }
};

// Get file content
exports.getFileContent = async (req, res) => {
  try {
    const { filePath } = req.query;
    const fullPath = path.join(SECOND_BRAIN_DIR, filePath);
    
    // Security check to prevent directory traversal
    if (!fullPath.startsWith(SECOND_BRAIN_DIR)) {
      return res.status(403).json({ error: 'Access denied' });
    }
    
    const exists = await fs.pathExists(fullPath);
    if (!exists) {
      return res.status(404).json({ error: 'File not found' });
    }
    
    const content = await fs.readFile(fullPath, 'utf8');
    const html = md.render(content);
    
    res.json({
      content,
      html,
      path: filePath,
      lastModified: (await fs.stat(fullPath)).mtime
    });
  } catch (error) {
    console.error('Error getting file content:', error);
    res.status(500).json({ error: 'Failed to get file content' });
  }
};

// Create a new note
exports.createNote = async (req, res) => {
  try {
    const { content, filePath, tags } = req.body;
    const fullPath = path.join(SECOND_BRAIN_DIR, filePath);
    
    // Security check to prevent directory traversal
    if (!fullPath.startsWith(SECOND_BRAIN_DIR)) {
      return res.status(403).json({ error: 'Access denied' });
    }
    
    // Create directory if it doesn't exist
    await fs.ensureDir(path.dirname(fullPath));
    
    // Create frontmatter
    const now = new Date();
    const frontmatter = `---
created: ${now.toISOString()}
tags: ${tags ? tags.join(', ') : ''}
---

`;

    // Write file
    await fs.writeFile(fullPath, frontmatter + content);
    
    res.json({
      success: true,
      path: filePath,
      created: now
    });
  } catch (error) {
    console.error('Error creating note:', error);
    res.status(500).json({ error: 'Failed to create note' });
  }
};

// Helper function to build directory tree
async function buildDirectoryTree(dir, relativePath = '') {
  const items = await fs.readdir(dir);
  const result = [];
  
  for (const item of items) {
    const fullPath = path.join(dir, item);
    const itemRelativePath = path.join(relativePath, item);
    const stats = await fs.stat(fullPath);
    
    if (stats.isDirectory()) {
      const children = await buildDirectoryTree(fullPath, itemRelativePath);
      result.push({
        name: item,
        path: itemRelativePath,
        type: 'directory',
        children
      });
    } else {
      result.push({
        name: item,
        path: itemRelativePath,
        type: 'file',
        size: stats.size,
        modified: stats.mtime
      });
    }
  }
  
  return result;
}
```

## Step 3: Configure Frontend

### Update Tailwind Config (client/tailwind.config.js)

```javascript
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          // ... other shades
          600: '#0284c7',
          700: '#0369a1',
        },
      },
    },
  },
  plugins: [],
}
```

### Create API Service (client/src/services/api.js)

```javascript
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
```

### Create Chat Component (client/src/components/Chat/ChatContainer.js)

```javascript
import React, { useState, useEffect, useRef } from 'react';
import { chatService } from '../../services/api';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

const ChatContainer = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Load chat history when component mounts
    const loadHistory = async () => {
      try {
        const response = await chatService.getHistory();
        setMessages(response.data.history || []);
      } catch (error) {
        console.error('Error loading chat history:', error);
      }
    };
    
    loadHistory();
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (text) => {
    // Add user message to chat
    const userMessage = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMessage]);
    
    // Show loading state
    setLoading(true);
    
    try {
      // Send message to API
      const response = await chatService.sendMessage(text);
      
      // Add AI response to chat
      const aiMessage = { 
        role: 'assistant', 
        content: response.data.message,
        action: response.data.action,
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage = { 
        role: 'system', 
        content: 'Sorry, there was an error processing your message. Please try again.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4">
        <MessageList messages={messages} />
        <div ref={messagesEndRef} />
      </div>
      <div className="border-t border-gray-200 p-4">
        <MessageInput onSendMessage={handleSendMessage} disabled={loading} />
      </div>
    </div>
  );
};

export default ChatContainer;
```

### Create Message Components (client/src/components/Chat/MessageList.js)

```javascript
import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

const MessageList = ({ messages }) => {
  return (
    <div className="space-y-4">
      {messages.map((message, index) => (
        <div 
          key={index} 
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div 
            className={`max-w-3/4 rounded-lg p-3 ${
              message.role === 'user' 
                ? 'bg-primary-600 text-white' 
                : message.role === 'system' 
                  ? 'bg-yellow-100 text-gray-800' 
                  : 'bg-gray-100 text-gray-800'
            }`}
          >
            <ReactMarkdown
              components={{
                code({node, inline, className, children, ...props}) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={tomorrow}
                      language={match[1]}
                      PreTag="div"
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                }
              }}
            >
              {message.content}
            </ReactMarkdown>
            
            {message.action && (
              <div className="mt-2 p-2 bg-gray-50 rounded border border-gray-200 text-sm">
                <div className="font-bold text-gray-700">Action performed:</div>
                <div className="text-gray-600">{message.action.description}</div>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default MessageList;
```

### Create Message Input Component (client/src/components/Chat/MessageInput.js)

```javascript
import React, { useState } from 'react';

const MessageInput = ({ onSendMessage, disabled }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex space-x-2">
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type a message..."
        className="flex-1 rounded-lg border border-gray-300 p-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
        disabled={disabled}
      />
      <button
        type="submit"
        className={`rounded-lg bg-primary-600 px-4 py-2 text-white ${
          disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-primary-700'
        }`}
        disabled={disabled}
      >
        {disabled ? 'Sending...' : 'Send'}
      </button>
    </form>
  );
};

export default MessageInput;
```

### Create File Browser Component (client/src/components/FileBrowser/FileBrowser.js)

```javascript
import React, { useState, useEffect } from 'react';
import { fileService } from '../../services/api';

const FileBrowser = ({ onFileSelect }) => {
  const [structure, setStructure] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedFolders, setExpandedFolders] = useState({});

  useEffect(() => {
    const loadStructure = async () => {
      try {
        setLoading(true);
        const response = await fileService.getStructure();
        setStructure(response.data);
        setError(null);
      } catch (err) {
        console.error('Error loading file structure:', err);
        setError('Failed to load directory structure');
      } finally {
        setLoading(false);
      }
    };
    
    loadStructure();
  }, []);

  const toggleFolder = (path) => {
    setExpandedFolders((prev) => ({
      ...prev,
      [path]: !prev[path],
    }));
  };

  const renderItem = (item, depth = 0) => {
    const isExpanded = expandedFolders[item.path];
    
    return (
      <div key={item.path} className="select-none">
        <div 
          className={`flex items-center py-1 px-2 hover:bg-gray-100 cursor-pointer`}
          style={{ paddingLeft: `${(depth + 1) * 0.5}rem` }}
          onClick={() => {
            if (item.type === 'directory') {
              toggleFolder(item.path);
            } else {
              onFileSelect(item.path);
            }
          }}
        >
          <span className="mr-1">
            {item.type === 'directory' ? (
              isExpanded ? '📂' : '📁'
            ) : (
              '📄'
            )}
          </span>
          <span className="truncate">{item.name}</span>
        </div>
        
        {item.type === 'directory' && isExpanded && (
          <div className="ml-2">
            {item.children.map((child) => renderItem(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return <div className="p-4">Loading files...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">{error}</div>;
  }

  return (
    <div className="h-full overflow-y-auto bg-white">
      <div className="p-2 font-bold border-b">Second Brain</div>
      <div className="py-2">
        {structure.map((item) => renderItem(item))}
      </div>
    </div>
  );
};

export default FileBrowser;
```

### Create Main App Component (client/src/App.js)

```javascript
import React, { useState } from 'react';
import ChatContainer from './components/Chat/ChatContainer';
import FileBrowser from './components/FileBrowser/FileBrowser';
import { fileService } from './services/api';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState(null);
  const [showSidebar, setShowSidebar] = useState(true);

  const handleFileSelect = async (filePath) => {
    try {
      const response = await fileService.getFileContent(filePath);
      setSelectedFile(filePath);
      setFileContent(response.data);
    } catch (error) {
      console.error('Error loading file:', error);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar with file browser */}
      <div 
        className={`${
          showSidebar ? 'w-64' : 'w-0'
        } transition-all duration-300 border-r border-gray-200 bg-white overflow-hidden`}
      >
        <FileBrowser onFileSelect={handleFileSelect} />
      </div>
      
      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200 h-14 flex items-center px-4">
          <button 
            className="mr-4 text-gray-500"
            onClick={() => setShowSidebar(!showSidebar)}
          >
            {showSidebar ? '◀️' : '▶️'}
          </button>
          <h1 className="text-xl font-semibold text-gray-800">Second Brain Chat</h1>
        </header>
        
        {/* Content area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Chat container */}
          <div className="flex-1 flex flex-col">
            <ChatContainer />
          </div>
          
          {/* Preview panel (conditionally rendered) */}
          {fileContent && (
            <div className="w-1/2 border-l border-gray-200 bg-white overflow-auto">
              <div className="p-2 bg-gray-100 border-b flex justify-between">
                <div className="truncate font-medium">{selectedFile}</div>
                <button 
                  className="text-gray-500"
                  onClick={() => setFileContent(null)}
                >
                  ✕
                </button>
              </div>
              <div 
                className="p-4 prose max-w-none"
                dangerouslySetInnerHTML={{ __html: fileContent.html }}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
```

### Update Index CSS (client/src/index.css)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

.prose {
  max-width: 100%;
}
```

## Step 4: Configure Environment Variables

### Create .env File for Backend (server/.env)

```
PORT=5000
OPENAI_API_KEY=your_openai_api_key_here
SECOND_BRAIN_DIR=/path/to/your/second/brain/directory
```

### Create .env File for Frontend (client/.env)

```
REACT_APP_API_URL=http://localhost:5000/api
```

## Step 5: Run the Application

### Start the Backend

```bash
cd server
npm run dev
```

### Start the Frontend

```bash
cd client
npm start
```

The application should now be running at http://localhost:3000

## Next Steps

Once you have the basic implementation running, you can enhance it by:

1. Adding command auto-detection and suggestion
2. Implementing authentication
3. Adding search functionality
4. Enhancing the UI with animations and transitions
5. Implementing responsive design for mobile devices
6. Adding dark mode support
7. Implementing file creation and editing
8. Adding support for tags and metadata

This basic implementation provides the foundation for your Web UI chat interface, which you can then expand upon based on your priorities and needs. 