@echo off
setlocal enabledelayedexpansion

echo Installing AI Surveillance System...

:: Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Please run this script as Administrator
    pause
    exit /b 1
)

:: Check available disk space (in MB)
for /f "usebackq delims== tokens=2" %%x in (`wmic LogicalDisk where "DeviceID='%~d0'" get FreeSpace /format:value`) do set FREE_SPACE=%%x
set /a FREE_SPACE_MB=%FREE_SPACE:~0,-7%
if %FREE_SPACE_MB% LSS 1000 (
    echo Insufficient disk space. Need at least 1GB free.
    pause
    exit /b 1
)

:: Set project directory
set "PROJECT_DIR=%~dp0.."
cd /d "%PROJECT_DIR%"

:: Check Python installation and version
python --version > nul 2>&1
if errorlevel 1 (
    echo Installing Python...
    if exist "install\dependencies\python-3.9.0-amd64.exe" (
        install\dependencies\python-3.9.0-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
        if errorlevel 1 (
            echo Failed to install Python
            pause
            exit /b 1
        )
    ) else (
        echo Python installer not found in dependencies folder!
        pause
        exit /b 1
    )
)

:: Verify Python version
for /f "tokens=2 delims=." %%I in ('python -c "import sys; print(sys.version.split()[0])"') do (
    if %%I LSS 8 (
        echo Python 3.8 or higher is required
        pause
        exit /b 1
    )
)

:: Install Visual C++ Redistributable if needed
if exist "install\dependencies\vc_redist.x64.exe" (
    echo Installing Visual C++ Redistributable...
    install\dependencies\vc_redist.x64.exe /quiet /norestart
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

:: Verify pip is available
pip --version > nul 2>&1
if errorlevel 1 (
    echo pip not found in virtual environment
    pause
    exit /b 1
)

:: Install packages from local directory
echo Installing dependencies...
if exist "install\packages" (
    pip install --no-index --find-links=install\packages -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo Package directory not found!
    pause
    exit /b 1
)

:: Create necessary directories
echo Creating project directories...
mkdir recordings 2>nul
mkdir models 2>nul
mkdir logs 2>nul

:: Copy AI models if they exist
if exist "install\dependencies\models\*" (
    echo Copying AI models...
    xcopy /E /I /Y install\dependencies\models models
)

:: Test write permissions
echo Testing write permissions...
echo. 2>recordings\test.txt
if errorlevel 1 (
    echo Warning: Cannot write to recordings directory
)
del recordings\test.txt 2>nul

:: Create environment variables file if it doesn't exist
if not exist ".env" (
    echo Creating default environment file...
    echo PYTHONPATH=%PROJECT_DIR% > .env
)

echo Installation complete!
echo To start the system:
echo 1. Open Command Prompt as Administrator
echo 2. Navigate to %PROJECT_DIR%
echo 3. Run: venv\Scripts\activate
echo 4. Run: python src\main.py

:: Check if installation was successful
if errorlevel 0 (
    echo Setup completed successfully!
) else (
    echo Setup failed! Please check the error messages above.
    pause
    exit /b 1
)

pause
