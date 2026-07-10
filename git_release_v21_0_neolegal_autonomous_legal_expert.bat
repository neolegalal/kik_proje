@echo off
cd /d C:\Users\MSI\Desktop\kik_proje
python ".py\2200_Run_All.py"
IF ERRORLEVEL 1 (
 echo RELEASE BLOCKED
 pause
 exit /b 1
)
git status
git add .
git commit -m "Release v21.0: NeoLegal Autonomous Legal Expert"
git push
git tag v21.0-neolegal-autonomous-legal-expert
git push origin v21.0-neolegal-autonomous-legal-expert
pause