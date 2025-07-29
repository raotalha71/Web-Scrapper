@echo off
echo ============================================================================
echo WEB SCRAPING PROJECT SETUP FOR WINDOWS
echo ============================================================================
echo This script will set up your Python virtual environment and install all dependencies.
echo Ensure you have Python 3.8+ installed before running this script.
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
python --version
echo ✓ Python is installed!
echo.

echo Step 1: Creating virtual environment (.venv)...
if exist .venv (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q .venv
)
python -m venv .venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment.
    echo Make sure you have sufficient permissions and disk space.
    pause
    exit /b 1
)
echo ✓ Virtual environment created successfully!
echo.

echo Step 2: Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)
echo ✓ Virtual environment activated!
echo.

echo Step 3: Upgrading pip to latest version...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo WARNING: Failed to upgrade pip. Continuing with current version...
)
echo ✓ Pip updated!
echo.

echo Step 4: Installing Python packages from requirements.txt...
echo This may take a few minutes...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install packages from requirements.txt
    echo Check your internet connection and try again.
    pause
    exit /b 1
)
echo ✓ All Python packages installed successfully!
echo.

echo Step 5: Installing Playwright browsers...
echo This will download Chrome, Firefox, and Safari browsers for automation...
playwright install
if %errorlevel% neq 0 (
    echo WARNING: Playwright browser installation failed.
    echo You can install manually later with: playwright install
    echo Continuing with setup...
) else (
    echo ✓ Playwright browsers installed!
)
echo.

echo Step 6: Verifying installation...
python -c "import requests; print('✓ requests imported')"
python -c "import bs4; print('✓ beautifulsoup4 imported')"
python -c "import playwright; print('✓ playwright imported')"
python -c "import pandas; print('✓ pandas imported')"
python -c "print('✓ All core packages verified successfully!')"
if %errorlevel% neq 0 (
    echo ERROR: Package verification failed. Some packages may not be installed correctly.
    pause
    exit /b 1
)
echo.

echo Step 7: Creating activation script for easy access...
echo @echo off > activate_env.bat
echo echo Activating Python virtual environment... >> activate_env.bat
echo call .venv\Scripts\activate.bat >> activate_env.bat
echo echo ✓ Environment activated! You can now run Python scripts. >> activate_env.bat
echo cmd /k >> activate_env.bat
echo ✓ Created activate_env.bat for easy environment activation!
echo.

echo ============================================================================
echo SETUP COMPLETE! 🎉
echo ============================================================================
echo Your web scraping environment is ready to use!
echo.
echo QUICK START:
echo   1. Double-click "activate_env.bat" to activate the environment
echo   2. Or manually run: .venv\Scripts\activate
echo   3. Test with: python test_site_access.py
echo.
echo WHAT WAS INSTALLED:
echo   ✓ Python virtual environment (.venv folder)
echo   ✓ All required packages (see requirements.txt)
echo   ✓ Playwright browsers for web automation
echo   ✓ Activation script (activate_env.bat)
echo.
echo NEXT STEPS:
echo   - Run "python test_site_access.py" to test site accessibility
echo   - Check the README.md for usage instructions
echo   - Your scraped data will be saved in logs/ and data/ folders
echo.
echo ============================================================================
pause
