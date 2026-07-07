# -*- coding: utf-8 -*-
class IntelligenceRecommendation:
    def recommend(self, normalized, score, risk_level):
        queue = normalized.get("queue", {})
        workers = normalized.get("workers", {})
        db_count = normalized.get("system", {}).get("db_count", 0)

        if risk_level == "HIGH":
            return "Yeni production batch başlatmadan önce hata kaynakları incelenmelidir."

        if queue.get("failed", 0):
            return "Failed job bulundu; önce queue recovery veya retry planı çalıştırılmalıdır."

        if workers.get("idle", 0) == workers.get("total", 0) and workers.get("total", 0) > 0:
            return "Worker'lar boşta görünüyor; kontrollü yeni batch başlatılabilir."

        if db_count and db_count < 100000:
            return "Production platform sağlıklı; 100.000 karar hedefine yönelik kontrollü üretim sürdürülebilir."

        return "Sistem normal görünmektedir; mevcut plan korunabilir."
