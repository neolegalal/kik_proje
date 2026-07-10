@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running Validation Benchmark Platform v19.0...
python ".py\2050_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 2050 Validation Benchmark Platform FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v19.0: Validation Benchmark Platform"
git push
git tag v19.0-validation-benchmark-platform
git push origin v19.0-validation-benchmark-platform

pause
