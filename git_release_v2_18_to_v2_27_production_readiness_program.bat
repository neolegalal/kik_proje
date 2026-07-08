@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running 311-320 Production Readiness Program...
python ".py\311_320_Production_Readiness_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 311-320 readiness program FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v2.18-v2.27: Production readiness program"
git push
git tag v2.18-v2.27-production-readiness-program
git push origin v2.18-v2.27-production-readiness-program

pause
