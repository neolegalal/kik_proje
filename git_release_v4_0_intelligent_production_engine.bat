@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running Intelligent Production Engine v4.0...
python ".py\600_670_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 600-670 Intelligent Production Engine FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v4.0: Intelligent Production Engine"
git push
git tag v4.0-intelligent-production-engine
git push origin v4.0-intelligent-production-engine

pause
