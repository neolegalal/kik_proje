@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running Unified Decision Processor v18.5...
python ".py\1950_Run_All.py" --batch-size 10

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 1950 Unified Decision Processor FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v18.5: Unified Decision Processor"
git push
git tag v18.5-unified-decision-processor
git push origin v18.5-unified-decision-processor

pause
