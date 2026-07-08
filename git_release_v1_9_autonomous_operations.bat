@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

git status
git add .
git commit -m "Release v1.9: Autonomous operations layer architecture"
git push
git tag v1.9-autonomous-operations-layer
git push origin v1.9-autonomous-operations-layer

pause
