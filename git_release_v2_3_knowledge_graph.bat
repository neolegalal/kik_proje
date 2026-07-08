@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

git status
git add .
git commit -m "Release v2.3: Knowledge Graph layer architecture"
git push
git tag v2.3-knowledge-graph-layer
git push origin v2.3-knowledge-graph-layer

pause
