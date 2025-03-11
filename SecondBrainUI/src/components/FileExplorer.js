import React, { useState, useEffect } from 'react';
import { MdFolder, MdFolderOpen, MdDescription, MdRefresh } from 'react-icons/md';

const { ipcRenderer } = window.require('electron');

const FileExplorer = ({ rootPath, onFileSelect, selectedFile }) => {
  const [directoryStructure, setDirectoryStructure] = useState([]);
  const [expandedFolders, setExpandedFolders] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const loadDirectoryStructure = async (dir = '') => {
    try {
      setIsLoading(true);
      const structure = await ipcRenderer.invoke('get-directory-structure', dir);
      if (dir === '') {
        setDirectoryStructure(structure);
      }
      setIsLoading(false);
      return structure;
    } catch (error) {
      console.error('Error loading directory structure:', error);
      setIsLoading(false);
      return [];
    }
  };

  useEffect(() => {
    if (rootPath) {
      loadDirectoryStructure();
    }
  }, [rootPath]);

  const handleToggleFolder = async (folderPath) => {
    setExpandedFolders(prev => {
      const newState = { ...prev };
      if (newState[folderPath]) {
        newState[folderPath] = false;
      } else {
        newState[folderPath] = true;
        // Load subdirectory when expanding
        loadDirectoryStructure(folderPath).then(subItems => {
          setDirectoryStructure(prev => {
            const updateItem = (items, path, subItems) => {
              return items.map(item => {
                if (item.path === path) {
                  return { ...item, children: subItems };
                } else if (item.isDirectory && item.children) {
                  return { ...item, children: updateItem(item.children, path, subItems) };
                }
                return item;
              });
            };
            
            return updateItem(prev, folderPath, subItems);
          });
        });
      }
      return newState;
    });
  };

  const handleFileClick = (filePath) => {
    onFileSelect(filePath);
  };

  const renderItems = (items) => {
    if (!items || items.length === 0) {
      return <div className="pl-4 py-1 text-gray-500">No items</div>;
    }

    return items
      .sort((a, b) => {
        // Directories first, then alphabetical
        if (a.isDirectory && !b.isDirectory) return -1;
        if (!a.isDirectory && b.isDirectory) return 1;
        return a.name.localeCompare(b.name);
      })
      .map((item) => {
        const isExpanded = expandedFolders[item.path];
        
        if (item.isDirectory) {
          return (
            <div key={item.path}>
              <div 
                className="flex items-center py-1 pl-4 hover:bg-gray-100 cursor-pointer"
                onClick={() => handleToggleFolder(item.path)}
              >
                <span className="mr-1 text-yellow-600">
                  {isExpanded ? <MdFolderOpen size={20} /> : <MdFolder size={20} />}
                </span>
                <span className="truncate">{item.name}</span>
              </div>
              
              {isExpanded && (
                <div className="ml-4">
                  {item.children ? renderItems(item.children) : <div className="text-gray-500 py-1">Loading...</div>}
                </div>
              )}
            </div>
          );
        } else {
          const isMarkdown = item.name.endsWith('.md');
          const isSelected = selectedFile === item.path;
          
          return (
            <div 
              key={item.path}
              className={`flex items-center py-1 pl-4 hover:bg-gray-100 cursor-pointer ${isSelected ? 'bg-blue-100' : ''}`}
              onClick={() => isMarkdown && handleFileClick(item.path)}
            >
              <span className={`mr-1 ${isMarkdown ? 'text-blue-600' : 'text-gray-600'}`}>
                <MdDescription size={18} />
              </span>
              <span className={`truncate ${!isMarkdown ? 'text-gray-500' : ''}`}>{item.name}</span>
            </div>
          );
        }
      });
  };

  const handleRefresh = () => {
    loadDirectoryStructure();
    setExpandedFolders({});
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 flex justify-between items-center border-b border-gray-300 bg-white">
        <h2 className="text-lg font-semibold">Files</h2>
        <button 
          onClick={handleRefresh} 
          className="p-1 rounded hover:bg-gray-200"
          title="Refresh"
          disabled={isLoading}
        >
          <MdRefresh size={20} className={isLoading ? 'animate-spin' : ''} />
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        {rootPath ? (
          isLoading && directoryStructure.length === 0 ? (
            <div className="p-4 text-gray-500">Loading...</div>
          ) : (
            renderItems(directoryStructure)
          )
        ) : (
          <div className="p-4 text-gray-500">No directory selected</div>
        )}
      </div>
    </div>
  );
};

export default FileExplorer; 