@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

git status
git add .
git commit -m "Release v2.0: Self-healing layer architecture"
git push
git tag v2.0-self-healing-layer
git push origin v2.0-self-healing-layer

pause
