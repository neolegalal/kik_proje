@echo off
cd /d C:\Users\MSI\Desktop\kik_proje

echo Running 213-218 Mega Platform validation...
python ".py\213_218_Mega_Run_All.py"

IF ERRORLEVEL 1 (
    echo.
    echo ================================================================
    echo RELEASE BLOCKED: Mega Platform validation FAILED.
    echo Git commit/tag/push islemi yapilmadi.
    echo ================================================================
    pause
    exit /b 1
)

echo.
echo ================================================================
echo VALIDATION PASS: Git release islemi baslatiliyor.
echo ================================================================

git status
git add .
git commit -m "Release v2.3-v2.8: Complete platform layers 213-218"
git push

git tag v2.3-knowledge-graph-layer
git push origin v2.3-knowledge-graph-layer
git tag v2.4-continuous-improvement-layer
git push origin v2.4-continuous-improvement-layer
git tag v2.5-enterprise-platform-layer
git push origin v2.5-enterprise-platform-layer
git tag v2.6-production-cluster-layer
git push origin v2.6-production-cluster-layer
git tag v2.7-large-scale-production-layer
git push origin v2.7-large-scale-production-layer
git tag v2.8-neolegal-ai-runtime-layer
git push origin v2.8-neolegal-ai-runtime-layer

echo.
echo ================================================================
echo RELEASE COMPLETED: v2.3-v2.8 tags pushed.
echo ================================================================
pause
