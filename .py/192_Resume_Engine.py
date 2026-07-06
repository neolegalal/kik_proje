# -*- coding: utf-8 -*-
"""
192 - RESUME ENGINE
NeoLegal / KİK Production Platform

Amaç:
- Uzun production batch çalışmalarında elektrik kesintisi, Python kapanması,
  API timeout, internet kopması veya Windows restart sonrası kaldığı yerden
  devam edebilmek için güvenli checkpoint/state altyapısı sağlar.

Bu dosya tek başına production zincirini çalıştırmaz.
181_v14 Final Master Controller içine entegre edilmek üzere yardımcı modüldür.

Standart kullanım:
    from _192_Resume_Engine import ResumeEngine

    resume = ResumeEngine(project_root=PROJECT_ROOT, run_id=RUN_ID, batch_limit=limit)
    resume.start_run(metadata={...})

    if resume.is_step_done("168"):
        output_168 = resume.get_step_output("168")
    else:
        # step çalıştır
        resume.mark_step_done("168", output_path=output_168, detail="...")

    resume.finish_run(final_ready=True)
"""

from __future__ import annotations

import json
import os
import time
import traceback
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _safe_mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
    """State dosyasını yarım yazılmaya karşı atomik yazar."""
    _safe_mkdir(path.parent)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(path))


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        corrupt = path.with_suffix(path.suffix + f".corrupt_{int(time.time())}")
        try:
            path.rename(corrupt)
        except Exception:
            pass
        return {}


@dataclass
class ResumeStep:
    step: str
    status: str = "PENDING"  # PENDING / RUNNING / DONE / FAIL / SKIPPED
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    output_path: Optional[str] = None
    detail: Optional[str] = None
    error: Optional[str] = None
    elapsed_seconds: Optional[float] = None


class ResumeEngine:
    """
    181 controller için güvenli resume/checkpoint yöneticisi.

    Temel prensip:
    - Her adım başlamadan önce RUNNING yazılır.
    - Her adım başarıyla bitince DONE yazılır.
    - Elektrik kesilirse son DONE adım korunur.
    - Controller yeniden çalıştığında DONE adımlar atlanabilir.
    """

    VERSION = "192_v1"

    def __init__(
        self,
        project_root: str | Path,
        run_id: str,
        batch_limit: int,
        state_dir: str | Path = "production_state",
    ) -> None:
        self.project_root = Path(project_root)
        self.run_id = str(run_id)
        self.batch_limit = int(batch_limit)
        self.state_dir = self.project_root / state_dir
        self.state_path = self.state_dir / f"192_resume_state_{self.run_id}.json"
        self.event_log_path = self.state_dir / f"192_resume_events_{self.run_id}.jsonl"
        _safe_mkdir(self.state_dir)

        self.state: Dict[str, Any] = _read_json(self.state_path)
        if not self.state:
            self.state = self._new_state()

    def _new_state(self) -> Dict[str, Any]:
        return {
            "engine": self.VERSION,
            "run_id": self.run_id,
            "batch_limit": self.batch_limit,
            "created_at": _now(),
            "updated_at": _now(),
            "status": "CREATED",
            "metadata": {},
            "steps": {},
            "last_done_step": None,
            "final_ready": False,
            "resume_count": 0,
            "events_path": str(self.event_log_path),
        }

    def save(self) -> None:
        self.state["updated_at"] = _now()
        _atomic_write_json(self.state_path, self.state)

    def event(self, event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
        row = {
            "time": _now(),
            "run_id": self.run_id,
            "event": event_type,
            "payload": payload or {},
        }
        with self.event_log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def start_run(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        if self.state.get("status") in {"RUNNING", "INTERRUPTED", "CREATED"}:
            if self.state.get("status") == "RUNNING":
                self.state["resume_count"] = int(self.state.get("resume_count", 0)) + 1
                self.event("RESUME_DETECTED", {"resume_count": self.state["resume_count"]})
            self.state["status"] = "RUNNING"
            if metadata:
                self.state["metadata"].update(metadata)
            self.save()
            self.event("RUN_STARTED", {"metadata": metadata or {}})

    def finish_run(self, final_ready: bool, detail: str = "") -> None:
        self.state["status"] = "FINISHED"
        self.state["final_ready"] = bool(final_ready)
        self.state["finished_at"] = _now()
        self.state["finish_detail"] = detail
        self.save()
        self.event("RUN_FINISHED", {"final_ready": final_ready, "detail": detail})

    def fail_run(self, error: str) -> None:
        self.state["status"] = "FAILED"
        self.state["error"] = error
        self.state["failed_at"] = _now()
        self.save()
        self.event("RUN_FAILED", {"error": error})

    def interrupt_marker(self, reason: str = "manual_or_unexpected_stop") -> None:
        self.state["status"] = "INTERRUPTED"
        self.state["interrupted_at"] = _now()
        self.state["interrupt_reason"] = reason
        self.save()
        self.event("RUN_INTERRUPTED", {"reason": reason})

    def start_step(self, step: str, detail: str = "") -> None:
        step = str(step)
        item = ResumeStep(step=step, status="RUNNING", started_at=_now(), detail=detail)
        self.state["steps"][step] = asdict(item)
        self.save()
        self.event("STEP_STARTED", {"step": step, "detail": detail})

    def mark_step_done(
        self,
        step: str,
        output_path: Optional[str] = None,
        detail: str = "",
        elapsed_seconds: Optional[float] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        step = str(step)
        item = self.state["steps"].get(step, {})
        started_at = item.get("started_at")
        done = ResumeStep(
            step=step,
            status="DONE",
            started_at=started_at,
            finished_at=_now(),
            output_path=output_path,
            detail=detail,
            elapsed_seconds=elapsed_seconds,
        )
        data = asdict(done)
        if extra:
            data["extra"] = extra
        self.state["steps"][step] = data
        self.state["last_done_step"] = step
        self.save()
        self.event("STEP_DONE", {"step": step, "output_path": output_path, "detail": detail})

    def mark_step_fail(self, step: str, error: str, detail: str = "") -> None:
        step = str(step)
        item = self.state["steps"].get(step, {})
        item.update({
            "step": step,
            "status": "FAIL",
            "finished_at": _now(),
            "error": error,
            "detail": detail,
        })
        self.state["steps"][step] = item
        self.save()
        self.event("STEP_FAIL", {"step": step, "error": error, "detail": detail})

    def is_step_done(self, step: str) -> bool:
        item = self.state.get("steps", {}).get(str(step), {})
        return item.get("status") == "DONE"

    def get_step_output(self, step: str) -> Optional[str]:
        item = self.state.get("steps", {}).get(str(step), {})
        return item.get("output_path")

    def get_step_detail(self, step: str) -> Optional[str]:
        item = self.state.get("steps", {}).get(str(step), {})
        return item.get("detail")

    def summary(self) -> Dict[str, Any]:
        steps = self.state.get("steps", {})
        return {
            "run_id": self.run_id,
            "batch_limit": self.batch_limit,
            "status": self.state.get("status"),
            "final_ready": self.state.get("final_ready"),
            "last_done_step": self.state.get("last_done_step"),
            "resume_count": self.state.get("resume_count", 0),
            "done_steps": [k for k, v in steps.items() if v.get("status") == "DONE"],
            "running_steps": [k for k, v in steps.items() if v.get("status") == "RUNNING"],
            "failed_steps": [k for k, v in steps.items() if v.get("status") == "FAIL"],
            "state_path": str(self.state_path),
            "event_log_path": str(self.event_log_path),
        }

    def write_summary_report(self, report_path: str | Path) -> None:
        report_path = Path(report_path)
        _safe_mkdir(report_path.parent)
        s = self.summary()
        lines = [
            "192 RESUME ENGINE RAPORU",
            "=" * 80,
            f"Run ID        : {s['run_id']}",
            f"Batch Limit   : {s['batch_limit']}",
            f"Status        : {s['status']}",
            f"Final Ready   : {s['final_ready']}",
            f"Last Done Step: {s['last_done_step']}",
            f"Resume Count  : {s['resume_count']}",
            "",
            "DONE STEPS",
            "-" * 80,
        ]
        lines.extend([f"- {x}" for x in s["done_steps"]] or ["Yok"])
        lines += ["", "FAILED STEPS", "-" * 80]
        lines.extend([f"- {x}" for x in s["failed_steps"]] or ["Yok"])
        lines += [
            "",
            "DOSYALAR",
            "-" * 80,
            f"State : {s['state_path']}",
            f"Events: {s['event_log_path']}",
        ]
        report_path.write_text("\n".join(lines), encoding="utf-8")


def guarded_step(resume: ResumeEngine, step: str, func, *args, **kwargs):
    """
    Basit entegrasyon yardımcısı.
    step DONE ise func çalıştırılmaz, kayıtlı output döner.
    step DONE değilse func çalışır ve hata olursa state'e yazılır.

    func dönüşü:
      - str ise output_path kabul edilir
      - dict ise output_path/detail anahtarları aranır
      - diğer durumlarda detail olarak saklanır
    """
    if resume.is_step_done(step):
        return {
            "resumed": True,
            "step": step,
            "output_path": resume.get_step_output(step),
            "detail": resume.get_step_detail(step),
        }

    start = time.time()
    resume.start_step(step)
    try:
        result = func(*args, **kwargs)
        elapsed = round(time.time() - start, 2)

        output_path = None
        detail = ""
        extra = None

        if isinstance(result, str):
            output_path = result
            detail = "function_returned_output_path"
        elif isinstance(result, dict):
            output_path = result.get("output_path")
            detail = result.get("detail", "")
            extra = result
        else:
            detail = repr(result)

        resume.mark_step_done(
            step=step,
            output_path=output_path,
            detail=detail,
            elapsed_seconds=elapsed,
            extra=extra,
        )
        return result
    except Exception as exc:
        err = "".join(traceback.format_exception_only(type(exc), exc)).strip()
        resume.mark_step_fail(step, error=err, detail=traceback.format_exc())
        raise


if __name__ == "__main__":
    # Basit manuel test:
    root = Path.cwd()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    engine = ResumeEngine(project_root=root, run_id=run_id, batch_limit=10)
    engine.start_run({"manual_test": True})
    engine.start_step("TEST")
    engine.mark_step_done("TEST", detail="Resume Engine manuel test başarılı.")
    engine.finish_run(final_ready=True, detail="Manual test completed.")
    report = root / "raporlar" / f"192_resume_engine_test_{run_id}.txt"
    engine.write_summary_report(report)
    print("192 Resume Engine manuel test tamamlandı.")
    print("State :", engine.state_path)
    print("Rapor :", report)
