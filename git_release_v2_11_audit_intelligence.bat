@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running 304 validation...
python ".py\304_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: validation FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v2.11: Audit Intelligence layer architecture"
git push
git tag v2.11-audit-intelligence-layer
git push origin v2.11-audit-intelligence-layer

pause
