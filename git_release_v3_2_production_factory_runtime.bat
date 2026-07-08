@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running Production Factory Runtime v3.2...
python ".py\550_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 550 Production Factory Runtime FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v3.2: Production Factory Runtime"
git push
git tag v3.2-production-factory-runtime
git push origin v3.2-production-factory-runtime

pause
