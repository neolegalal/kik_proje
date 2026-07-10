@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running Next Generation NeoLegal AI v13-v17...
python ".py\1800_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 1800 Next Generation NeoLegal AI FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v13-v17: Next Generation NeoLegal AI"
git push
git tag v13-v17-next-generation-neolegal-ai
git push origin v13-v17-next-generation-neolegal-ai

pause
