# Installation Guide for Second Brain UI

This guide walks you through installing and running the Second Brain UI application.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v16 or later): [Download Node.js](https://nodejs.org/)
- **npm** (usually comes with Node.js)

## Installation Options

### Option 1: Use the Build Scripts (Recommended)

1. **Clone or download** this repository to your local machine
2. **Open a terminal or command prompt** and navigate to the SecondBrainUI directory
3. **Run the build script** for your platform:
   - **macOS/Linux**: 
     ```
     ./build.sh
     ```
   - **Windows**: 
     ```
     build.bat
     ```
4. **Wait for the build to complete**. This might take a few minutes as it downloads dependencies and builds the application.
5. **Find your installer** in the `dist` directory:
   - macOS: `Second Brain UI-{version}.dmg`
   - Windows: `Second Brain UI Setup {version}.exe`
   - Linux: `second-brain-ui-{version}.AppImage`
6. **Run the installer** and follow the on-screen instructions

### Option 2: Manual Installation

1. **Clone or download** this repository to your local machine
2. **Open a terminal or command prompt** and navigate to the SecondBrainUI directory
3. **Install dependencies**:
   ```
   npm install
   ```
4. **Build the application**:
   ```
   npm run dist
   ```
5. **Find your installer** in the `dist` directory and run it

### Option 3: Development Mode

If you want to run the application in development mode:

1. **Clone or download** this repository
2. **Install dependencies**:
   ```
   npm install
   ```
3. **Start in development mode**:
   ```
   npm run electron-dev
   ```

## First-Time Setup

When you first launch the application:

1. You'll be prompted to **select your Second Brain directory**
2. This should be the root directory of your Second Brain knowledge management system
3. The application will remember this location for future use

## Usage

For detailed usage instructions, please refer to the `SecondBrainUI_Usage.md` file.

## Troubleshooting

If you encounter any issues during installation:

- **Ensure Node.js and npm are correctly installed** by running `node -v` and `npm -v`
- **Check your system meets the requirements** for Electron applications
- **For build errors**, try deleting the `node_modules` directory and reinstalling dependencies
- **For permission errors**, make sure you have admin/sudo rights when installing

## Updating

To update to a newer version:

1. Download the latest version
2. Run through the installation process again
3. Your existing settings and Second Brain path will be preserved 