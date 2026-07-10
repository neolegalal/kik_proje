@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running Production Operations v6.0...
python ".py\1000_Run_All.py" --target 100000 --batch-size 10

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 1000 Production Operations FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v6.0: Production Operations"
git push
git tag v6.0-production-operations
git push origin v6.0-production-operations

pause
