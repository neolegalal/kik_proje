@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running Real Production Engine v4.2...
python ".py\800_Run_All.py" --batch-size 10

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 800 Real Production Engine FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v4.2: Real Production Engine"
git push
git tag v4.2-real-production-engine
git push origin v4.2-real-production-engine

pause
