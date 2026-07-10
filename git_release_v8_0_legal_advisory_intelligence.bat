@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running Legal Advisory Intelligence v8.0...
python ".py\1300_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 1300 Legal Advisory Intelligence FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v8.0: Legal Advisory Intelligence"
git push
git tag v8.0-legal-advisory-intelligence
git push origin v8.0-legal-advisory-intelligence

pause
