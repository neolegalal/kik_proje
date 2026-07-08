@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running 219 validation...
python ".py\219_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: validation FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v2.9: Cloud Platform layer architecture"
git push
git tag v2.9-cloud-platform-layer
git push origin v2.9-cloud-platform-layer

pause
