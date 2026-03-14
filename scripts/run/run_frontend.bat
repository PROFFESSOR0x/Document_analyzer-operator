@echo off
REM Start Frontend Development Server

echo Starting Document Analyzer Frontend...

cd /d "%~dp0..\.."
cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)

REM Start development server
call npm run dev
