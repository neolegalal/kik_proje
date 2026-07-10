@echo off
cd /d C:\Users\MSI\Desktop\kik_proje
python ".py\2100_Run_All.py"
IF ERRORLEVEL 1 (
 echo RELEASE BLOCKED
 pause
 exit /b 1
)
git status
git add .
git commit -m "Release v20.0: NeoLegal Legal Brain"
git push
git tag v20.0-neolegal-legal-brain
git push origin v20.0-neolegal-legal-brain
pause