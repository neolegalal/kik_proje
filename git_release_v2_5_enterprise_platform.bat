@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

git status
git add .
git commit -m "Release v2.5: Enterprise Platform layer architecture"
git push
git tag v2.5-enterprise-platform-layer
git push origin v2.5-enterprise-platform-layer

pause
