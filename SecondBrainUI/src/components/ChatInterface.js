import React, { useState, useRef, useEffect } from 'react';
import { MdSend } from 'react-icons/md';
import MessageList from './MessageList';
import { processUserMessage } from '../services/IntentDetectionService';

const { ipcRenderer } = window.require('electron');

const ChatInterface = ({ secondBrainPath, onFileCreated }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const messageEndRef = useRef(null);

  useEffect(() => {
    if (messageEndRef.current) {
      messageEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isProcessing) return;

    const userMessage = input.trim();
    setInput('');
    
    // Add user message to chat
    setMessages(prev => [...prev, { 
      id: Date.now(), 
      content: userMessage, 
      sender: 'user' 
    }]);
    
    setIsProcessing(true);
    
    try {
      // Process the message to determine intent and perform actions
      const result = await processUserMessage(userMessage, secondBrainPath);
      
      // Add system response
      setMessages(prev => [...prev, { 
        id: Date.now(), 
        content: result.responseMessage, 
        sender: 'assistant' 
      }]);
      
      // If a file was created or updated, notify parent component
      if (result.filePath) {
        onFileCreated(result.filePath);
      }
    } catch (error) {
      console.error('Error processing message:', error);
      setMessages(prev => [...prev, { 
        id: Date.now(), 
        content: `Error: ${error.message || 'Failed to process your request'}`, 
        sender: 'assistant' 
      }]);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-background-light">
      <div className="p-4 border-b border-gray-300 bg-white">
        <h2 className="text-lg font-semibold">Second Brain Assistant</h2>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4">
        <MessageList messages={messages} />
        <div ref={messageEndRef} />
      </div>
      
      <div className="p-4 border-t border-gray-300 bg-white">
        <form onSubmit={handleSubmit} className="flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isProcessing}
            placeholder={isProcessing ? "Processing..." : "Type a message..."}
            className="flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <button
            type="submit"
            disabled={isProcessing || !input.trim()}
            className="ml-2 p-2 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <MdSend size={20} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface; 