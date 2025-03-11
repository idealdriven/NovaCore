import React from 'react';
import ReactMarkdown from 'react-markdown';

const MessageList = ({ messages }) => {
  if (messages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-500">
        <p className="mb-4 text-center">Welcome to your Second Brain Assistant</p>
        <p className="text-sm text-center">Start by typing a message, for example:</p>
        <ul className="list-disc mt-2 text-sm">
          <li>[Thought] I need to organize my project ideas better</li>
          <li>[Daily] Here's what I accomplished today</li>
          <li>Find notes about artificial intelligence</li>
        </ul>
      </div>
    );
  }

  return (
    <div className="flex flex-col space-y-4">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`message-bubble ${
            message.sender === 'user' ? 'user-message' : 'assistant-message'
          }`}
        >
          {message.sender === 'assistant' ? (
            <ReactMarkdown>{message.content}</ReactMarkdown>
          ) : (
            message.content
          )}
        </div>
      ))}
    </div>
  );
};

export default MessageList; 