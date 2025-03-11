@echo off
echo === Second Brain UI Build Script ===
echo This script will build the Second Brain UI application for Windows.
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Node.js is not installed. Please install Node.js and try again.
    exit /b 1
)

REM Check if npm is installed
where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: npm is not installed. Please install npm and try again.
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
call npm install

REM Build the application
echo Building the application...
call npm run dist

echo.
echo Build completed! You can find your installer in the 'dist' directory.
echo For help using the application, see the SecondBrainUI_Usage.md file.
pause 