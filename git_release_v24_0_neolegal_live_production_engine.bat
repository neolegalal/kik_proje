@echo off
cd /d C:\Users\MSI\Desktop\kik_proje
python ".py\2411_2421_Run_All.py" --target 10 --batch-size 10 --workers 4
IF ERRORLEVEL 1 (
 echo RELEASE BLOCKED
 pause
 exit /b 1
)
git status
git add .
git commit -m "Release v24.0: NeoLegal Live Production Engine"
git push origin main
git tag -a v24.0-neolegal-live-production-engine -m "NeoLegal Live Production Engine v24.0"
git push origin v24.0-neolegal-live-production-engine
pause