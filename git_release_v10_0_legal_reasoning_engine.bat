@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running Legal Reasoning Engine v10.0...
python ".py\1500_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 1500 Legal Reasoning Engine FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v10.0: Legal Reasoning Engine"
git push
git tag v10.0-legal-reasoning-engine
git push origin v10.0-legal-reasoning-engine

pause
