@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running 305 validation...
python ".py\305_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: validation FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v2.12: NeoLegal Kernel layer architecture"
git push
git tag v2.12-neolegal-kernel-layer
git push origin v2.12-neolegal-kernel-layer

pause
