@echo off
cd /d C:\Users\MSI\Desktop\kik_proje
python ".py\2300_Run_All.py"
IF ERRORLEVEL 1 (
 echo RELEASE BLOCKED
 pause
 exit /b 1
)
git status
git add .
git commit -m "Release v22.0: NeoLegal Platform Governance"
git push
git tag v22.0-neolegal-platform-governance
git push origin v22.0-neolegal-platform-governance
pause