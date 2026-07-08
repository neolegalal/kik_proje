@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

git status
git add .
git commit -m "Release v2.7: Large Scale Production layer architecture"
git push
git tag v2.7-large-scale-production-layer
git push origin v2.7-large-scale-production-layer

pause
