@echo off
REM Setup script for AI Memory Experiment Multi-Language Support

echo ================================================
echo AI Memory Experiment - Multi-Language Setup
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo + Python found
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo X Failed to install dependencies
    pause
    exit /b 1
)

echo + Dependencies installed successfully
echo.

REM Create directories if they don't exist
echo Creating directories...
if not exist "templates" mkdir templates
if not exist "static" mkdir static
if not exist "experiment_data" mkdir experiment_data

echo + Directories created
echo.

REM Check if language_selection.html exists
if not exist "templates\language_selection.html" (
    echo ! language_selection.html not found in templates/
    echo   Please copy language_selection.html to templates/ folder
) else (
    echo + language_selection.html found
)

echo.

REM Check if app.py exists
if not exist "app.py" (
    echo ! app.py not found in current directory
    echo   Please make sure app.py is in the root directory
) else (
    echo + app.py found
)

echo.
echo ================================================
echo Setup Complete!
echo ================================================
echo.
echo To start the experiment server, run:
echo   python app.py
echo.
echo Then open your browser to:
echo   http://127.0.0.1:8080
echo.
echo Supported languages:
echo   - English (en)
echo   - Chinese (zh)
echo.
echo To change language manually:
echo   http://127.0.0.1:8080/set_lang/en
echo   http://127.0.0.1:8080/set_lang/zh
echo.
pause
