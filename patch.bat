@echo off
echo =========================================
echo Applying SQLite DB Patch: manifest_input_date
echo =========================================

call myenv\Scripts\activate

python patch_db.py

echo.
echo Patch completed.
pause
