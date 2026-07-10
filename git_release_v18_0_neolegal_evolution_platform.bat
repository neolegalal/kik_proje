@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running NeoLegal Evolution Platform v18.0...
python ".py\1900_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 1900 NeoLegal Evolution Platform FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v18.0: NeoLegal Evolution Platform"
git push
git tag v18.0-neolegal-evolution-platform
git push origin v18.0-neolegal-evolution-platform

pause
