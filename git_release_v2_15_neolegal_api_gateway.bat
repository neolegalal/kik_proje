@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running 308 validation...
python ".py\308_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: validation FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v2.15: NeoLegal API Gateway layer architecture"
git push
git tag v2.15-neolegal-api-gateway-layer
git push origin v2.15-neolegal-api-gateway-layer

pause
