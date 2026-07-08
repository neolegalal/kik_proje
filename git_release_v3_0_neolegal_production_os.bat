@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running NeoLegal Production OS v3.0...
python ".py\400_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 400 Production OS FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v3.0: NeoLegal Production OS"
git push
git tag v3.0-neolegal-production-os
git push origin v3.0-neolegal-production-os

pause
