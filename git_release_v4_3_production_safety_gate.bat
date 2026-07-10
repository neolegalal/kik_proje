@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running Production Safety Gate v4.3...
python ".py\801_Run_All.py" --batch-size 10

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 801 Production Safety Gate FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v4.3: Production Safety Gate"
git push
git tag v4.3-production-safety-gate
git push origin v4.3-production-safety-gate

pause
