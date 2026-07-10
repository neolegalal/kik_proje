@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running NeoLegal Expert Workspace v11.0-v12.0...
python ".py\1600_1700_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 1600-1700 NeoLegal Expert Workspace FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v11.0-v12.0: NeoLegal Expert Orchestrator and Workspace Memory"
git push
git tag v11.0-neolegal-expert-orchestrator
git tag v12.0-client-workspace-knowledge-memory
git push origin v11.0-neolegal-expert-orchestrator
git push origin v12.0-client-workspace-knowledge-memory

pause
