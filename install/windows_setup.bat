@echo off
echo Installing AI Surveillance System...

:: Check Python installation
python --version > nul 2>&1
if errorlevel 1 (
    echo Installing Python...
    if exist "dependencies\python-3.9.0-amd64.exe" (
        dependencies\python-3.9.0-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
    ) else (
        echo Python installer not found in dependencies folder!
        exit /b 1
    )
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Install packages from local directory
echo Installing dependencies...
pip install --no-index --find-links=packages -r ..\requirements.txt

:: Create necessary directories
mkdir ..\recordings 2>nul
mkdir ..\models 2>nul

:: Copy AI models if they exist
if exist "dependencies\models\*" (
    echo Copying AI models...
    xcopy /E /I /Y dependencies\models ..\models
)

echo Setup complete! Run 'python src/main.py' to start the system.
pause
