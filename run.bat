@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 run.py
) else (
    python run.py
)
if errorlevel 1 (
    echo.
    echo The app could not start. Check the error message above.
    pause
)
