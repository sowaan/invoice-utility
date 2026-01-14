@echo off
echo =========================================
echo Invoice Utility - Setup & Patch
echo =========================================

REM Check Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is not installed or not in PATH.
    pause
    exit /b 1
)

REM Create virtual environment if missing
IF NOT EXIST myenv\Scripts\activate.bat (
    echo Creating virtual environment (myenv)...
    python -m venv myenv
)

REM Activate virtual environment
call myenv\Scripts\activate

REM Install dependencies (only once)
IF EXIST requirements.txt (
    IF NOT EXIST myenv\.deps_installed (
        echo Installing dependencies...
        pip install -r requirements.txt
        echo done > myenv\.deps_installed
    )
)

REM Apply SQLite DB patch
echo Applying database patch...
python patch_db.py

echo =========================================
echo Setup & Patch completed successfully
echo =========================================
pause
