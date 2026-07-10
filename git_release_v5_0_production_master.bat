@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running Production Master v5.0...
python ".py\900_Run_All.py" --target 100000 --batch-size 10

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 900 Production Master FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v5.0: Production Master"
git push
git tag v5.0-production-master
git push origin v5.0-production-master

pause
