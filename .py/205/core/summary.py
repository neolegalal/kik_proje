# -*- coding: utf-8 -*-
class IntelligenceSummary:
    def build(self, normalized, score, risk_level, recommendation):
        db_count = normalized.get("system", {}).get("db_count")
        queue = normalized.get("queue", {})
        workers = normalized.get("workers", {})
        events = normalized.get("events", {})
        logs = normalized.get("logs", {})

        return (
            f"NeoLegal Intelligence değerlendirmesine göre platform stabilite skoru {score}/100 seviyesindedir. "
            f"Risk seviyesi {risk_level} olarak hesaplanmıştır. "
            f"Veritabanında {db_count} kart bulunmaktadır. "
            f"Queue toplam {queue.get('total')} iş, {queue.get('finished')} tamamlanan iş ve {queue.get('failed')} failed iş içermektedir. "
            f"{workers.get('total')} worker tanımlıdır; {workers.get('idle')} worker idle durumdadır. "
            f"Event Bus toplam {events.get('total')} olay, Logger toplam {logs.get('total')} log kaydı içermektedir. "
            f"Öneri: {recommendation}"
        )
