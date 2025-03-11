import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { MdEdit, MdSave, MdCancel } from 'react-icons/md';

const NoteViewer = ({ content, filePath, onContentChange }) => {
  const [editMode, setEditMode] = useState(false);
  const [editableContent, setEditableContent] = useState('');
  const [fileName, setFileName] = useState('');

  useEffect(() => {
    if (filePath) {
      const parts = filePath.split('/');
      setFileName(parts[parts.length - 1]);
    }
    setEditableContent(content);
  }, [filePath, content]);

  const handleEdit = () => {
    setEditMode(true);
    setEditableContent(content);
  };

  const handleSave = () => {
    onContentChange(editableContent);
    setEditMode(false);
  };

  const handleCancel = () => {
    setEditMode(false);
    setEditableContent(content);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-gray-300 bg-white flex justify-between items-center">
        <h2 className="text-lg font-semibold truncate">{fileName}</h2>
        <div className="flex">
          {editMode ? (
            <>
              <button
                onClick={handleSave}
                className="p-1 rounded hover:bg-green-100 text-green-600 mr-2"
                title="Save"
              >
                <MdSave size={20} />
              </button>
              <button
                onClick={handleCancel}
                className="p-1 rounded hover:bg-red-100 text-red-600"
                title="Cancel"
              >
                <MdCancel size={20} />
              </button>
            </>
          ) : (
            <button
              onClick={handleEdit}
              className="p-1 rounded hover:bg-blue-100 text-blue-600"
              title="Edit"
            >
              <MdEdit size={20} />
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-auto p-4">
        {editMode ? (
          <textarea
            value={editableContent}
            onChange={(e) => setEditableContent(e.target.value)}
            className="w-full h-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary resize-none font-mono"
          />
        ) : (
          <div className="prose max-w-none">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
};

export default NoteViewer; 