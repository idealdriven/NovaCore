// FileOperationService.js - Handles all file operations for the Second Brain
const { ipcRenderer } = window.require('electron');

// Helper function to get the current date in YYYYMMDD format
const getFormattedDate = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}${month}${day}`;
};

// Helper function to format a date for display
const formatDisplayDate = (date = new Date()) => {
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long', 
    day: 'numeric'
  });
};

// Helper function to get the week number
const getWeekNumber = (date = new Date()) => {
  const firstDayOfYear = new Date(date.getFullYear(), 0, 1);
  const pastDaysOfYear = (date - firstDayOfYear) / 86400000;
  return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7);
};

// Create a new fleeting note
export const createFleetingNote = async (content) => {
  try {
    const date = getFormattedDate();
    const title = content.split('\n')[0].substring(0, 40).replace(/[^\w\s-]/g, '').trim().replace(/\s+/g, '_').toLowerCase();
    const filePath = `Notes/Fleeting/${date}_${title}.md`;
    
    // Format content with metadata
    const now = new Date();
    const formattedContent = `# ${content.split('\n')[0]}\n\n` +
      `Created: ${now.toISOString()}\n` +
      `Tags: #fleeting\n\n` +
      `${content}\n`;
    
    const result = await ipcRenderer.invoke('create-note', {
      filePath,
      content: formattedContent
    });
    
    if (result.success) {
      return { success: true, filePath };
    } else {
      throw new Error(result.error || 'Failed to create fleeting note');
    }
  } catch (error) {
    console.error('Error creating fleeting note:', error);
    throw error;
  }
};

// Create or update a daily note
export const createDailyNote = async (content) => {
  try {
    const date = getFormattedDate();
    const filePath = `Notes/Journal/Daily/${date}.md`;
    
    // Check if the file already exists
    let existingContent = '';
    try {
      existingContent = await ipcRenderer.invoke('get-file-content', filePath);
    } catch (error) {
      // File doesn't exist, create new one with header
      existingContent = `# Daily Note - ${formatDisplayDate()}\n\n`;
    }
    
    // Append new content
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    const updatedContent = existingContent + 
      `\n## ${timeString}\n\n${content}\n\n`;
    
    const result = await ipcRenderer.invoke('update-note', {
      filePath,
      content: updatedContent
    });
    
    if (result.success) {
      return { success: true, filePath };
    } else {
      throw new Error(result.error || 'Failed to update daily note');
    }
  } catch (error) {
    console.error('Error updating daily note:', error);
    throw error;
  }
};

// Create or update a weekly note
export const createWeeklyNote = async (content) => {
  try {
    const now = new Date();
    const weekNumber = getWeekNumber(now);
    const year = now.getFullYear();
    const filePath = `Notes/Journal/Weekly/${year}_W${weekNumber}.md`;
    
    // Check if the file already exists
    let existingContent = '';
    try {
      existingContent = await ipcRenderer.invoke('get-file-content', filePath);
    } catch (error) {
      // File doesn't exist, create new one with header
      const startOfWeek = new Date(now);
      startOfWeek.setDate(now.getDate() - now.getDay());
      const endOfWeek = new Date(startOfWeek);
      endOfWeek.setDate(startOfWeek.getDate() + 6);
      
      const dateRange = `${startOfWeek.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${endOfWeek.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
      
      existingContent = `# Weekly Note - Week ${weekNumber}, ${year} (${dateRange})\n\n`;
    }
    
    // Append new content
    const updatedContent = existingContent + 
      `\n## ${formatDisplayDate()}\n\n${content}\n\n`;
    
    const result = await ipcRenderer.invoke('update-note', {
      filePath,
      content: updatedContent
    });
    
    if (result.success) {
      return { success: true, filePath };
    } else {
      throw new Error(result.error || 'Failed to update weekly note');
    }
  } catch (error) {
    console.error('Error updating weekly note:', error);
    throw error;
  }
};

// Create or update a monthly note
export const createMonthlyNote = async (content) => {
  try {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const filePath = `Notes/Journal/Monthly/${year}_${month}.md`;
    
    // Check if the file already exists
    let existingContent = '';
    try {
      existingContent = await ipcRenderer.invoke('get-file-content', filePath);
    } catch (error) {
      // File doesn't exist, create new one with header
      const monthName = now.toLocaleDateString('en-US', { month: 'long' });
      existingContent = `# Monthly Note - ${monthName} ${year}\n\n`;
    }
    
    // Append new content
    const updatedContent = existingContent + 
      `\n## ${formatDisplayDate()}\n\n${content}\n\n`;
    
    const result = await ipcRenderer.invoke('update-note', {
      filePath,
      content: updatedContent
    });
    
    if (result.success) {
      return { success: true, filePath };
    } else {
      throw new Error(result.error || 'Failed to update monthly note');
    }
  } catch (error) {
    console.error('Error updating monthly note:', error);
    throw error;
  }
};

// Update a project note
export const updateProjectNote = async (projectName, content) => {
  try {
    // Sanitize project name for file path
    const sanitizedName = projectName.replace(/[^\w\s-]/g, '').trim().replace(/\s+/g, '_').toLowerCase();
    const filePath = `Projects/${sanitizedName}/notes.md`;
    
    // Check if the file already exists
    let existingContent = '';
    try {
      existingContent = await ipcRenderer.invoke('get-file-content', filePath);
    } catch (error) {
      // File doesn't exist, create new one with header
      existingContent = `# ${projectName}\n\n`;
    }
    
    // Append new content
    const updatedContent = existingContent + 
      `\n## ${formatDisplayDate()}\n\n${content}\n\n`;
    
    const result = await ipcRenderer.invoke('update-note', {
      filePath,
      content: updatedContent
    });
    
    if (result.success) {
      return { success: true, filePath };
    } else {
      throw new Error(result.error || 'Failed to update project note');
    }
  } catch (error) {
    console.error('Error updating project note:', error);
    throw error;
  }
}; 