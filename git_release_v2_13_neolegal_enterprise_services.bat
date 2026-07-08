@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running 306 validation...
python ".py\306_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: validation FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v2.13: NeoLegal Enterprise Services layer architecture"
git push
git tag v2.13-neolegal-enterprise-services-layer
git push origin v2.13-neolegal-enterprise-services-layer

pause
