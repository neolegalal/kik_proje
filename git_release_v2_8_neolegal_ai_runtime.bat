@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

git status
git add .
git commit -m "Release v2.8: NeoLegal AI Runtime layer architecture"
git push
git tag v2.8-neolegal-ai-runtime-layer
git push origin v2.8-neolegal-ai-runtime-layer

pause
