@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running Decision Processing Pipeline v7.0...
python ".py\1100_Run_All.py" --batch-size 10

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 1100 Decision Processing Pipeline FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v7.0: Decision Processing Pipeline"
git push
git tag v7.0-decision-processing-pipeline
git push origin v7.0-decision-processing-pipeline

pause
