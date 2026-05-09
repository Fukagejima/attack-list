@echo off
set PYTHON_CMD=

where python >nul 2>&1
if %errorlevel%==0 set PYTHON_CMD=python

if "%PYTHON_CMD%"=="" (
    where python3 >nul 2>&1
    if %errorlevel%==0 set PYTHON_CMD=python3
)

if "%PYTHON_CMD%"=="" (
    where py >nul 2>&1
    if %errorlevel%==0 set PYTHON_CMD=py
)

if "%PYTHON_CMD%"=="" (
    echo [ERROR] Python not found.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)

echo [OK] Python found: %PYTHON_CMD%
%PYTHON_CMD% --version

cd /d "%~dp0"

if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [INFO] Created .env file. Please set your ANTHROPIC_API_KEY.
        notepad .env
        pause
    )
)

%PYTHON_CMD% -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing packages...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Install failed.
        pause
        exit /b 1
    )
)

echo [INFO] Starting app at http://localhost:8501
%PYTHON_CMD% -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false

pause