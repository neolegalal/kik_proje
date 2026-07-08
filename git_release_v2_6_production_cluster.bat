@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

git status
git add .
git commit -m "Release v2.6: Production Cluster layer architecture"
git push
git tag v2.6-production-cluster-layer
git push origin v2.6-production-cluster-layer

pause
