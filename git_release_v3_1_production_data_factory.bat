@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running Production Data Factory v3.1...
python ".py\500_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 500 Production Data Factory FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v3.1: Production Data Factory"
git push
git tag v3.1-production-data-factory
git push origin v3.1-production-data-factory

pause
