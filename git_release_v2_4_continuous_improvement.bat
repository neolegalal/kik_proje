@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

git status
git add .
git commit -m "Release v2.4: Continuous Improvement layer architecture"
git push
git tag v2.4-continuous-improvement-layer
git push origin v2.4-continuous-improvement-layer

pause
