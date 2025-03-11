import React from 'react';
import { MdFolderOpen } from 'react-icons/md';

const SetupModal = ({ onSelectDirectory }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 max-w-md w-full">
        <h2 className="text-xl font-bold mb-4">Welcome to Second Brain UI</h2>
        <p className="mb-6">
          To get started, please select the location of your Second Brain directory on your computer.
        </p>
        
        <div className="flex justify-center">
          <button
            onClick={onSelectDirectory}
            className="flex items-center bg-primary hover:bg-primary-dark text-white py-2 px-4 rounded-lg transition duration-200"
          >
            <MdFolderOpen size={20} className="mr-2" />
            Select Directory
          </button>
        </div>
        
        <div className="mt-8 text-sm text-gray-600">
          <p className="mb-2">Note: This application needs to access your local files to manage your Second Brain.</p>
          <p>If you don't have a Second Brain directory set up yet, please select where you'd like to create one.</p>
        </div>
      </div>
    </div>
  );
};

export default SetupModal; 