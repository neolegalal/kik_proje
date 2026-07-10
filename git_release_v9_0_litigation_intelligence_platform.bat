@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running Litigation Intelligence Platform v9.0...
python ".py\1400_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 1400 Litigation Intelligence Platform FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v9.0: Litigation Intelligence Platform"
git push
git tag v9.0-litigation-intelligence-platform
git push origin v9.0-litigation-intelligence-platform

pause
