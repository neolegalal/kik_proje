# -*- coding: utf-8 -*-
from pathlib import Path
import py_compile

BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PY = BASE / ".py"
SUMMARY_DIR = BASE / "production_state" / "platform_summary"

LAYERS = [('213', 'Knowledge Graph', '213_Run_All.py', '213_Knowledge_Graph_SDK.py', ['213_1_GraphBuilder.py', '213_2_RelationExtractor.py', '213_3_EntityResolver.py', '213_4_KnowledgeStore.py', '213_5_SemanticSearch.py', '213_6_ContextBuilder.py', '213_7_GraphDashboard.py', '213_8_GraphDecisionEngine.py', '213_9_GraphAuditor.py', '213_10_GraphOptimizer.py']), ('214', 'Continuous Improvement', '214_Run_All.py', '214_Continuous_Improvement_SDK.py', ['214_1_ImprovementCollector.py', '214_2_FeedbackAnalyzer.py', '214_3_QualityLoopEngine.py', '214_4_OptimizationPlanner.py', '214_5_ImprovementPrioritizer.py', '214_6_ExperimentManager.py', '214_7_ImprovementDashboard.py', '214_8_ImprovementDecisionEngine.py', '214_9_ImprovementAuditor.py', '214_10_ImprovementRoadmapEngine.py']), ('215', 'Enterprise Platform', '215_Run_All.py', '215_Enterprise_Platform_SDK.py', ['215_1_EnterpriseController.py', '215_2_TenantManager.py', '215_3_AccessGovernance.py', '215_4_PolicyRegistry.py', '215_5_ServiceCatalog.py', '215_6_ComplianceManager.py', '215_7_EnterpriseDashboard.py', '215_8_EnterpriseDecisionEngine.py', '215_9_EnterpriseAuditor.py', '215_10_EnterpriseReleaseManager.py']), ('216', 'Production Cluster', '216_Run_All.py', '216_Production_Cluster_SDK.py', ['216_1_ClusterController.py', '216_2_NodeRegistry.py', '216_3_WorkerPoolManager.py', '216_4_LoadBalancer.py', '216_5_ClusterHealthMonitor.py', '216_6_ScalingPlanner.py', '216_7_ClusterDashboard.py', '216_8_ClusterDecisionEngine.py', '216_9_ClusterAuditor.py', '216_10_ClusterRecoveryManager.py']), ('217', 'Large Scale Production', '217_Run_All.py', '217_Large_Scale_Production_SDK.py', ['217_1_MassProductionController.py', '217_2_BatchExpansionEngine.py', '217_3_ThroughputPlanner.py', '217_4_CapacityGovernor.py', '217_5_QualityGateManager.py', '217_6_ProductionRolloutEngine.py', '217_7_LargeScaleDashboard.py', '217_8_LargeScaleDecisionEngine.py', '217_9_LargeScaleAuditor.py', '217_10_ProductionCompletionManager.py']), ('218', 'NeoLegal AI Runtime', '218_Run_All.py', '218_NeoLegal_AI_Runtime_SDK.py', ['218_1_RuntimeController.py', '218_2_RagRuntimeEngine.py', '218_3_QueryUnderstanding.py', '218_4_LegalAnswerEngine.py', '218_5_CitationEngine.py', '218_6_HallucinationGuard.py', '218_7_RuntimeDashboard.py', '218_8_RuntimeDecisionEngine.py', '218_9_RuntimeAuditor.py', '218_10_PublicApiGateway.py'])]
TAGS = ['v2.3-knowledge-graph-layer', 'v2.4-continuous-improvement-layer', 'v2.5-enterprise-platform-layer', 'v2.6-production-cluster-layer', 'v2.7-large-scale-production-layer', 'v2.8-neolegal-ai-runtime-layer']

def write_file(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if path.suffix == ".py":
        py_compile.compile(str(path), doraise=True)

def layer_run_all_code(layer):
    layer_id, layer_name, run_all, sdk_bridge, modules = layer
    commands = [sdk_bridge] + modules
    command_lines = []
    for file_name in commands:
        mode = "--test" if file_name.endswith("_SDK.py") else "--run"
        command_lines.append("    (" + repr(file_name) + ", [sys.executable, str(BASE / \".py\" / " + repr(file_name) + "), " + repr(mode) + "]),")
    template = r"""# -*- coding: utf-8 -*-
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

LAYER_ID = __LAYER_ID__
LAYER_NAME = __LAYER_NAME__

COMMANDS = [
__COMMANDS__
]

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    print("=" * 80)
    print(str(LAYER_ID) + " " + LAYER_NAME.upper() + " RUN ALL BASLADI")
    print("=" * 80)
    passed = 0
    failed = 0
    failed_modules = []
    for module_name, cmd in COMMANDS:
        print("\n>>> " + " ".join(cmd))
        result = subprocess.run(cmd, cwd=str(BASE))
        if result.returncode == 0:
            passed += 1
        else:
            failed += 1
            failed_modules.append(module_name)
    total = len(COMMANDS)
    score = round((passed / total) * 100, 2) if total else 0
    decision = "PASS" if failed == 0 else "FAIL"
    ready = "YES" if failed == 0 else "NO"
    summary = {"created_at": now_text(), "layer_id": LAYER_ID, "layer_name": LAYER_NAME, "modules": total, "passed": passed, "failed": failed, "failed_modules": failed_modules, "production_score": score, "final_decision": decision, "production_ready": ready}
    summary_path = SUMMARY_DIR / (str(LAYER_ID) + "_production_summary.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + "=" * 80)
    print("FINAL PRODUCTION SUMMARY")
    print("=" * 80)
    print("Layer             : " + str(LAYER_ID) + " " + LAYER_NAME)
    print("Modules           : " + str(total))
    print("Passed            : " + str(passed))
    print("Failed            : " + str(failed))
    print("Production Score  : " + str(score) + " / 100")
    print("FINAL DECISION    : " + decision)
    print("Production Ready  : " + ready)
    if failed_modules:
        print("")
        print("Failed Modules")
        for item in failed_modules:
            print("- " + item)
    print("")
    print("Summary JSON:")
    print(summary_path)
    print("=" * 80)
    sys.exit(0 if decision == "PASS" else 1)

if __name__ == "__main__":
    main()
"""
    return template.replace("__LAYER_ID__", repr(layer_id)).replace("__LAYER_NAME__", repr(layer_name)).replace("__COMMANDS__", "\n".join(command_lines))

def mega_run_all_code():
    command_lines = []
    for layer_id, layer_name, run_all, sdk_bridge, modules in LAYERS:
        command_lines.append("    (" + repr(layer_id) + ", " + repr(layer_name) + ", [sys.executable, str(BASE / \".py\" / " + repr(run_all) + ")]),")
    template = r"""# -*- coding: utf-8 -*-
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

COMMANDS = [
__COMMANDS__
]

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    print("=" * 80)
    print("213-218 MEGA PLATFORM RUN ALL BASLADI")
    print("=" * 80)
    layer_results = []
    passed = 0
    failed = 0
    for layer_id, layer_name, cmd in COMMANDS:
        print("\n>>> " + " ".join(cmd))
        result = subprocess.run(cmd, cwd=str(BASE))
        summary_path = SUMMARY_DIR / (str(layer_id) + "_production_summary.json")
        if summary_path.exists():
            try:
                data = json.loads(summary_path.read_text(encoding="utf-8"))
            except Exception:
                data = {}
        else:
            data = {}
        decision = data.get("final_decision")
        if result.returncode == 0 and decision == "PASS":
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1
        layer_results.append({"layer_id": layer_id, "layer_name": layer_name, "status": status, "returncode": result.returncode, "summary": data})
    total = len(COMMANDS)
    score = round((passed / total) * 100, 2) if total else 0
    decision = "PASS" if failed == 0 else "FAIL"
    ready = "YES" if failed == 0 else "NO"
    platform_summary = {"created_at": now_text(), "layers_total": total, "layers_passed": passed, "layers_failed": failed, "platform_score": score, "final_decision": decision, "platform_ready": ready, "layers": layer_results}
    platform_summary_path = SUMMARY_DIR / "213_218_platform_summary.json"
    platform_summary_path.write_text(json.dumps(platform_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + "=" * 80)
    print("NEOLEGAL PLATFORM SUMMARY")
    print("=" * 80)
    for item in layer_results:
        print("Layer " + str(item["layer_id"]) + " " + item["layer_name"].ljust(32) + " " + item["status"])
    print("-" * 80)
    print("Layers Passed     : " + str(passed) + " / " + str(total))
    print("Layers Failed     : " + str(failed))
    print("Platform Score    : " + str(score) + " / 100")
    print("FINAL RESULT      : " + decision)
    print("Platform Ready    : " + ready)
    print("")
    print("Summary JSON:")
    print(platform_summary_path)
    print("=" * 80)
    sys.exit(0 if decision == "PASS" else 1)

if __name__ == "__main__":
    main()
"""
    return template.replace("__COMMANDS__", "\n".join(command_lines))

def safe_git_bat_code():
    tag_lines = []
    for tag in TAGS:
        tag_lines.append("git tag " + tag)
        tag_lines.append("git push origin " + tag)
    return "@echo off\ncd /d C:\\Users\\MSI\\Desktop\\kik_proje\n\necho Running 213-218 Mega Platform validation...\npython \".py\\213_218_Mega_Run_All.py\"\n\nIF ERRORLEVEL 1 (\n    echo.\n    echo ================================================================\n    echo RELEASE BLOCKED: Mega Platform validation FAILED.\n    echo Git commit/tag/push islemi yapilmadi.\n    echo ================================================================\n    pause\n    exit /b 1\n)\n\necho.\necho ================================================================\necho VALIDATION PASS: Git release islemi baslatiliyor.\necho ================================================================\n\ngit status\ngit add .\ngit commit -m \"Release v2.3-v2.8: Complete platform layers 213-218\"\ngit push\n\n" + "\n".join(tag_lines) + "\n\necho.\necho ================================================================\necho RELEASE COMPLETED: v2.3-v2.8 tags pushed.\necho ================================================================\npause\n"

def main():
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    for layer in LAYERS:
        layer_id, layer_name, run_all, sdk_bridge, modules = layer
        write_file(PY / run_all, layer_run_all_code(layer))
    write_file(PY / "213_218_Mega_Run_All.py", mega_run_all_code())
    bat_path = BASE / "git_release_v2_3_to_v2_8_layers.bat"
    bat_path.write_text(safe_git_bat_code(), encoding="utf-8")
    print("=" * 80)
    print("300 PLATFORM LAYER GENERATOR v2 SUMMARY UPGRADE TAMAMLANDI")
    print("=" * 80)
    print("Guncellenen Run All dosyalari:")
    for layer in LAYERS:
        print(PY / layer[2])
    print(PY / "213_218_Mega_Run_All.py")
    print("")
    print("Guvenli Git BAT:")
    print(bat_path)
    print("")
    print("Simdi calistir:")
    print(r'python ".py\213_218_Mega_Run_All.py"')
    print("")
    print("Sonda FINAL RESULT: PASS gorunurse Git icin:")
    print(str(bat_path))

if __name__ == "__main__":
    main()
