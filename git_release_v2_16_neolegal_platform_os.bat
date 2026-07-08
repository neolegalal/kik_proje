@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running 309 validation...
python ".py\309_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: validation FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v2.16: NeoLegal Platform OS layer architecture"
git push
git tag v2.16-neolegal-platform-os-layer
git push origin v2.16-neolegal-platform-os-layer

pause
