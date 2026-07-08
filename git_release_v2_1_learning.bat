@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

git status
git add .
git commit -m "Release v2.1: Learning layer architecture"
git push
git tag v2.1-learning-layer
git push origin v2.1-learning-layer

pause
