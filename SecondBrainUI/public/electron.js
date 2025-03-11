const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const axios = require('axios');

// Detect if running in development or production
const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

let mainWindow;
let secondBrainPath = '';

// Claude integration for dynamic responses
async function askClaude(question, context, type) {
  try {
    console.log(`Question for Claude: ${question}`);
    console.log(`Context: ${context}`);
    console.log(`Type: ${type}`);
    
    // Instead of redirecting users to ask Claude separately,
    // we'll provide direct answers based on the context we have
    
    if (question.match(/sorry\??/i)) {
      return {
        text: `No need to apologize! I'm here to help you with your Second Brain system. Would you like to:

• Create a new note? Try saying "Create a note about [topic]"
• Find existing notes? Try "Find notes about [topic]"
• Learn more about the system? Try "Tell me about the Second Brain structure"

Just let me know what you'd like to do!`
      };
    }
    
    if (question.match(/how do (you|I) work/i) || question.match(/what can you do/i)) {
      return {
        text: `I'm your Second Brain assistant. I help you organize and manage your knowledge system in a few key ways:

1. **Capturing Notes**: I can create different types of notes (daily journals, fleeting thoughts, project updates)
2. **Finding Information**: I can search through your notes to find what you need
3. **Processing Content**: I help turn your raw thoughts into organized knowledge
4. **Maintaining Structure**: I follow the PARA method to keep your notes organized

Try asking me to "Create a note about [topic]" or "Find notes related to [topic]" to get started!`
      };
    }
    
    if (question.match(/tell me about|what is|explain (the|a) (second brain|system|folders|structure)/i)) {
      return {
        text: `Your Second Brain is a personal knowledge management system organized into these key folders:

• **Notes/Fleeting**: Quick capture of temporary thoughts and ideas
• **Knowledge**: Permanent, processed information organized by concepts
• **Projects**: Project-specific notes and materials
• **Resources**: Reference materials and external content
• **Journal**: Daily, weekly, and monthly reflections
• **Tags**: Themes that connect different notes
• **Archive**: Completed projects and inactive materials

This structure follows the PARA method (Projects, Areas, Resources, Archive) with some customizations for knowledge management.`
      };
    }
    
    if (question.match(/commands|how (do|can) I use|what should I (say|type)/i)) {
      return {
        text: `Here are the main commands you can use:

**Content Creation:**
• \`[Thought] Your idea\` - Creates a fleeting note
• \`[Daily] Today's reflection\` - Adds to your daily journal
• \`[Weekly] Week's progress\` - Updates weekly review
• \`[Monthly] Monthly summary\` - Updates monthly review
• \`[Project: Name] Update\` - Adds to a specific project

**Finding Information:**
• \`Find notes about topic\` - Searches your notes
• \`Summarize my notes on topic\` - Creates a summary

You can also use natural language like "Create a note about productivity" or "Find information about meetings."`
      };
    }
    
    // For other questions, provide a generic helpful response
    return {
      text: `I understand you're asking about "${question}". Your Second Brain system is designed to help you capture, organize, and retrieve information efficiently.

I can help you with:
• Creating and organizing notes
• Finding information you've stored
• Maintaining your knowledge system
• Processing your thoughts into structured content

Would you like to create a note, find information, or learn more about a specific aspect of the system?`
    };
  } catch (error) {
    console.error('Error with Claude integration:', error);
    return {
      error: true,
      message: 'Could not process the request'
    };
  }
}

function createWindow() {
  const desktopSize = require('electron').screen.getPrimaryDisplay().workAreaSize;
  
  mainWindow = new BrowserWindow({
    width: Math.min(1200, desktopSize.width),
    height: Math.min(800, desktopSize.height),
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true,
    }
  });

  const startUrl = isDev
    ? 'http://localhost:3000'
    : `file://${path.join(__dirname, '../build/index.html')}`;
  
  mainWindow.loadURL(startUrl);
  
  // Uncomment during development if you need DevTools
  // if (isDev) {
  //   mainWindow.webContents.openDevTools();
  // }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.on('ready', async () => {
  createWindow();
  
  // Check if the secondBrainPath exists in config
  const userDataPath = app.getPath('userData');
  const configPath = path.join(userDataPath, 'config.json');
  
  try {
    if (fs.existsSync(configPath)) {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      secondBrainPath = config.secondBrainPath;
      
      // Verify the path still exists
      if (!fs.existsSync(secondBrainPath)) {
        secondBrainPath = '';
      }
    }
  } catch (error) {
    console.error('Error reading config:', error);
    secondBrainPath = '';
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// Handle selecting the Second Brain directory
ipcMain.handle('select-directory', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  
  if (!result.canceled && result.filePaths.length > 0) {
    secondBrainPath = result.filePaths[0];
    
    // Save the path to config
    const userDataPath = app.getPath('userData');
    const configPath = path.join(userDataPath, 'config.json');
    
    fs.writeFileSync(configPath, JSON.stringify({ secondBrainPath }));
    
    return secondBrainPath;
  }
  
  return null;
});

// Get the Second Brain path
ipcMain.handle('get-second-brain-path', () => {
  return secondBrainPath;
});

// Get directory structure
ipcMain.handle('get-directory-structure', async (event, dir = '') => {
  try {
    const fullPath = dir ? path.join(secondBrainPath, dir) : secondBrainPath;
    const items = fs.readdirSync(fullPath);
    
    return items.map(item => {
      const itemPath = path.join(fullPath, item);
      const relativePath = path.relative(secondBrainPath, itemPath);
      const isDirectory = fs.statSync(itemPath).isDirectory();
      
      return {
        name: item,
        path: relativePath,
        isDirectory
      };
    });
  } catch (error) {
    console.error('Error getting directory structure:', error);
    return [];
  }
});

// Get file content
ipcMain.handle('get-file-content', async (event, filePath) => {
  try {
    const fullPath = path.join(secondBrainPath, filePath);
    return fs.readFileSync(fullPath, 'utf8');
  } catch (error) {
    console.error('Error reading file:', error);
    return null;
  }
});

// Create or update a file
ipcMain.handle('create-or-update-file', async (event, { filePath, content }) => {
  try {
    const fullPath = path.join(secondBrainPath, filePath);
    
    // Create directory if it doesn't exist
    const dirPath = path.dirname(fullPath);
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }
    
    const fileExists = fs.existsSync(fullPath);
    
    if (fileExists) {
      const existingContent = fs.readFileSync(fullPath, 'utf8');
      fs.writeFileSync(fullPath, existingContent + '\n\n' + content);
    } else {
      fs.writeFileSync(fullPath, content);
    }
    
    return { success: true, filePath };
  } catch (error) {
    console.error('Error creating/updating file:', error);
    return { success: false, error: error.message };
  }
});

// Handle Claude integration
ipcMain.handle('ask-claude', async (event, { question, context, type }) => {
  try {
    return await askClaude(question, context, type);
  } catch (error) {
    console.error('Error with Claude integration:', error);
    return { 
      error: true, 
      message: 'Failed to process with Claude'
    };
  }
});

// Legacy create-note handler - reimplemented directly
ipcMain.handle('create-note', async (event, { filePath, content }) => {
  try {
    const fullPath = path.join(secondBrainPath, filePath);
    
    // Create directory if it doesn't exist
    const dirPath = path.dirname(fullPath);
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }
    
    fs.writeFileSync(fullPath, content);
    return { success: true, filePath };
  } catch (error) {
    console.error('Error creating note:', error);
    return { success: false, error: error.message };
  }
});

// Legacy update-note handler - reimplemented directly
ipcMain.handle('update-note', async (event, { filePath, content }) => {
  try {
    const fullPath = path.join(secondBrainPath, filePath);
    
    if (fs.existsSync(fullPath)) {
      const existingContent = fs.readFileSync(fullPath, 'utf8');
      fs.writeFileSync(fullPath, existingContent + '\n\n' + content);
      return { success: true, filePath };
    } else {
      return { success: false, error: 'File not found' };
    }
  } catch (error) {
    console.error('Error updating note:', error);
    return { success: false, error: error.message };
  }
}); 