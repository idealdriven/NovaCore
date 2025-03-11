import React, { useState } from 'react';
import { FaCamera, FaFileUpload } from 'react-icons/fa';

const { exec } = window.require('child_process');
const { dialog } = window.require('electron').remote;
const path = window.require('path');
const fs = window.require('fs');

const ScreenshotHandler = ({ secondBrainPath, onProcessComplete }) => {
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);

  const selectScreenshot = async () => {
    try {
      const result = await dialog.showOpenDialog({
        properties: ['openFile'],
        filters: [
          { name: 'Images', extensions: ['png', 'jpg', 'jpeg', 'gif', 'bmp'] }
        ]
      });

      if (!result.canceled && result.filePaths.length > 0) {
        processScreenshot(result.filePaths[0]);
      }
    } catch (err) {
      setError(`Error selecting file: ${err.message}`);
    }
  };

  const processScreenshot = (imagePath) => {
    setProcessing(true);
    setError(null);

    // Get title from user
    dialog.showInputBox({
      title: 'Screenshot Title',
      message: 'Enter a title for this screenshot (optional):',
      buttons: ['Cancel', 'Process'],
      defaultId: 1,
    }).then(result => {
      if (result.response === 1) { // User clicked Process
        const title = result.text.trim();
        const scriptPath = path.join(secondBrainPath, 'Commands', 'screenshot.sh');
        
        // Check if the script exists
        if (!fs.existsSync(scriptPath)) {
          setError(`Screenshot processing script not found at: ${scriptPath}`);
          setProcessing(false);
          return;
        }

        // Build the command
        let command = `"${scriptPath}" "${imagePath}"`;
        if (title) {
          command += ` --title "${title}"`;
        }

        // Execute the command
        exec(command, (err, stdout, stderr) => {
          setProcessing(false);
          
          if (err) {
            setError(`Error processing screenshot: ${err.message}`);
            console.error(stderr);
            return;
          }
          
          console.log(stdout);
          
          if (onProcessComplete) {
            onProcessComplete(stdout);
          }
        });
      } else {
        setProcessing(false);
      }
    }).catch(err => {
      setError(`Error getting title: ${err.message}`);
      setProcessing(false);
    });
  };

  return (
    <div className="screenshot-handler">
      <button 
        onClick={selectScreenshot}
        disabled={processing}
        className="flex items-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
      >
        {processing ? (
          <span className="flex items-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Processing...
          </span>
        ) : (
          <>
            <FaFileUpload className="mr-2" /> Process Screenshot
          </>
        )}
      </button>
      
      {error && (
        <div className="text-red-500 mt-2">
          {error}
        </div>
      )}
    </div>
  );
};

export default ScreenshotHandler; 