@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running 303 validation...
python ".py\303_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: validation FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v2.10: Security Governance layer architecture"
git push
git tag v2.10-security-governance-layer
git push origin v2.10-security-governance-layer

pause
