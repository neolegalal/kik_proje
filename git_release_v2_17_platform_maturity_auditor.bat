@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running 310 Platform Maturity Auditor...
python ".py\310_Platform_Maturity_Integration_Auditor.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 310 auditor FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v2.17: Platform maturity and integration auditor"
git push
git tag v2.17-platform-maturity-auditor
git push origin v2.17-platform-maturity-auditor

pause
