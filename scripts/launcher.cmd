@echo off

set "APP_DIR=%LOCALAPPDATA%\InventorySystem"
set "VENV_PY=%APP_DIR%\venv\Scripts\python.exe"

if "%~1"=="--version" (
    CALL :version
    exit /b 0
)

if "%~1"=="-v" (
    CALL :version
    exit /b 0
)

if "%~1"=="--help" (
    CALL :help
    exit /b 0
)

if "%~1"=="-h" (
    CALL :help
    exit /b 0
)

if "%~1"=="update" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%APP_DIR%\repo\scripts\update.ps1"
    exit /b %ERRORLEVEL%
)

if "%~1"=="uninstall" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%APP_DIR%\repo\scripts\uninstall.ps1"
    exit /b 0
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

:version
git -C "%APP_DIR%\repo" describe --tags --always
exit /b

:help
echo "Usage: InventorySystem [options]"
echo "Options:"
echo "  -h, --help     Display this help message"
echo "  -v, --version  Display the current version"
echo "  update         Update the application to the latest version"
echo "  uninstall      Remove the application and launcher"
exit /b