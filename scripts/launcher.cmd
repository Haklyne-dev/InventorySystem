@echo off

set "APP_DIR=%LOCALAPPDATA%\InventorySystem"
set "VENV_PY=%APP_DIR%\venv\Scripts\python.exe"

if "%~1"=="--version" (
    git -C "%APP_DIR%\repo" describe --tags --exact-match
    exit /b 0
)

if "%~1"=="update" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%APP_DIR%\repo\scripts\update.ps1"
    exit /b %ERRORLEVEL%
)

cd /d "%APP_DIR%\repo\src"
"%VENV_PY%" "main.py" %*
set "STATUS=%ERRORLEVEL%"

if "%STATUS%"=="42" (
    echo Server requested an update, updating now...
    powershell -NoProfile -ExecutionPolicy Bypass -File "%APP_DIR%\repo\scripts\update.ps1"
    cd /d "%APP_DIR%\repo\src"
    "%VENV_PY%" "main.py" %*
    exit /b %ERRORLEVEL%
)

exit /b %STATUS%