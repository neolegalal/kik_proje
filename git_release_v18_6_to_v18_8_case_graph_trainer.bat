@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running Case Graph Trainer v18.6-v18.8...
python ".py\1970_1990_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 1970-1990 Case Graph Trainer FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v18.6-v18.8: Case Graph Trainer"
git push
git tag v18.6-v18.8-case-graph-trainer
git push origin v18.6-v18.8-case-graph-trainer

pause
