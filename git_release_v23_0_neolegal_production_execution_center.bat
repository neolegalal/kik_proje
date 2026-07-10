@echo off
cd /d C:\Users\MSI\Desktop\kik_proje
python ".py\2400_Run_All.py" --target 100000 --batch-size 100 --workers 4
IF ERRORLEVEL 1 (
 echo RELEASE BLOCKED
 pause
 exit /b 1
)
git status
git add .
git commit -m "Release v23.0: NeoLegal Production Execution Center"
git push
git tag v23.0-neolegal-production-execution-center
git push origin v23.0-neolegal-production-execution-center
pause