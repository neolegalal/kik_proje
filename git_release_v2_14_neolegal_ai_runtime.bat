@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running 307 validation...
python ".py\307_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: validation FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v2.14: NeoLegal AI Runtime layer architecture"
git push
git tag v2.14-neolegal-ai-runtime-layer
git push origin v2.14-neolegal-ai-runtime-layer

pause
