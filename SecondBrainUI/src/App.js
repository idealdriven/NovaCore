import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import FileExplorer from './components/FileExplorer';
import NoteViewer from './components/NoteViewer';
import SetupModal from './components/SetupModal';

const { ipcRenderer } = window.require('electron');

function App() {
  const [secondBrainPath, setSecondBrainPath] = useState('');
  const [showSetupModal, setShowSetupModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkPath = async () => {
      try {
        const path = await ipcRenderer.invoke('get-second-brain-path');
        setSecondBrainPath(path);
        
        if (!path) {
          setShowSetupModal(true);
        }
      } catch (error) {
        console.error('Error checking path:', error);
        setShowSetupModal(true);
      } finally {
        setIsLoading(false);
      }
    };

    checkPath();
  }, []);

  const handleSelectDirectory = async () => {
    try {
      const path = await ipcRenderer.invoke('select-directory');
      setSecondBrainPath(path);
      setShowSetupModal(false);
    } catch (error) {
      console.error('Error selecting directory:', error);
    }
  };

  const handleFileSelect = async (filePath) => {
    if (filePath.endsWith('.md')) {
      setSelectedFile(filePath);
      try {
        const content = await ipcRenderer.invoke('get-file-content', filePath);
        setFileContent(content);
      } catch (error) {
        console.error('Error loading file:', error);
        setFileContent('');
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-background">
      {showSetupModal && (
        <SetupModal onSelectDirectory={handleSelectDirectory} />
      )}

      {!showSetupModal && (
        <>
          <div className="w-1/4 border-r border-gray-300 overflow-auto">
            <FileExplorer 
              rootPath={secondBrainPath}
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
            />
          </div>

          <div className="flex flex-col w-2/4 border-r border-gray-300">
            {selectedFile ? (
              <NoteViewer 
                content={fileContent} 
                filePath={selectedFile}
                onContentChange={async (newContent) => {
                  setFileContent(newContent);
                  await ipcRenderer.invoke('update-note', {
                    filePath: selectedFile,
                    content: newContent
                  });
                }}
              />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                <p>Select a file to view its contents</p>
              </div>
            )}
          </div>

          <div className="w-1/4 overflow-hidden flex flex-col">
            <ChatInterface 
              secondBrainPath={secondBrainPath} 
              onFileCreated={handleFileSelect}
            />
          </div>
        </>
      )}
    </div>
  );
}

export default App; 