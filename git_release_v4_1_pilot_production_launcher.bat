@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running Pilot Production Launcher v4.1...
python ".py\700_Run_All.py" --batch-size 10

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 700 Pilot Production Launcher FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v4.1: Pilot Production Launcher"
git push
git tag v4.1-pilot-production-launcher
git push origin v4.1-pilot-production-launcher

pause
