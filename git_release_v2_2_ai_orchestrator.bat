@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

git status
git add .
git commit -m "Release v2.2: AI orchestrator layer architecture"
git push
git tag v2.2-ai-orchestrator-layer
git push origin v2.2-ai-orchestrator-layer

pause
