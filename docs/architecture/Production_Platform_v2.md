# NeoLegal Production Platform v2.0 Architecture

**Tarih:** 07.07.2026  
**Durum:** Architecture Freeze Candidate  
**Proje:** KİK / Kamu İhale Hukuku Production Platformu  

---

## 1. Amaç

NeoLegal Production Platform, kamu ihale hukuku alanındaki yüksek hacimli hukuki verilerin yapay zekâ destekli olarak üretilmesi, temizlenmesi, doğrulanması, optimize edilmesi, veritabanına aktarılması ve web/RAG sistemlerine uygun şekilde dışa aktarılması için geliştirilen kurumsal production platformudur.

Bu belge, v2.0 mimarisinin temel teknik referansıdır.

---

## 2. Kapsam

Bu mimari belge aşağıdaki katmanları kapsar:

- Core Platform katmanı
- Production Pipeline katmanı
- Resume ve kesintiden devam mimarisi
- Guardian ön kontrol mimarisi
- Smart Resume Validation mimarisi
- Quality Assurance katmanı
- Self-Healing akışı
- GitHub release ve branch politikası
- 1000 / 5000 / 100000 batch hedeflerine hazırlık

---

## 3. Proje Evrimi

### v1.0 - 250 PASS

- İlk doğrulanmış production milestone.
- GitHub tag: `v1.0-production-250-pass`

### v1.1 - 500 PASS

- 500 batch production validation tamamlandı.
- Self-Healing mekanizması gerçek üretimde doğrulandı.
- GitHub tag: `v1.1-production-500-pass`

### v1.2 - Resume Engine Validation

- 192 Resume Engine geliştirildi.
- 181 v14 Resume destekli controller oluşturuldu.
- Ctrl+C ile kesinti simülasyonu yapıldı.
- Aynı Run ID ile devam testi başarıyla geçti.
- GitHub tag: `v1.2-resume-engine-validation`

### v2.0 - Production Platform

- Core / Pipeline ayrımı resmileştirilecek.
- 195 Runtime Monitor eklenecek.
- 100 / 500 / 1000 batch ölçek testleri yapılacak.

---

## 4. Genel Mimari

```text
NeoLegal Production Platform

    194 Production Guardian
              |
              v
    181 Master Production Controller
              |
              v
    192 Resume Engine
              |
              v
    193 Smart Resume Validation
              |
              v
    Production Pipeline
              |
              v
    190 Supervisor / 184 Dashboard
```

---

## 5. Katmanlı Mimari

### 5.1 Infrastructure Layer

Bu katman fiziksel ve sistemsel altyapıyı ifade eder.

- Windows 11
- Python 3.14
- SQLite
- Git / GitHub
- APC Easy UPS BVG2200I-GR
- NVMe SSD altyapısı
- OpenAI/API tabanlı üretim bileşenleri

### 5.2 Core Platform Layer

Platformun üretimi yöneten çekirdek katmanıdır.

| Modül | Görev |
|------|------|
| 181 | Master Production Controller |
| 192 | Resume Engine |
| 193 | Smart Resume Validation |
| 194 | Production Guardian |
| 195 | Runtime Monitor |
| 196 | Analytics Engine |
| 197 | Recovery Manager |
| 198 | Distributed Processing |
| 199 | Production Manager |
| 200 | Platform Core |

### 5.3 Production Pipeline Layer

Hukuki kart üretim hattıdır.

```text
168 -> 188 -> 172 -> 175 -> 176 -> 177 -> 185 -> 178 -> 179 -> 180 -> 169 -> 170 -> 173 -> 182 -> 183 -> 184 -> 190
```

### 5.4 Export / Consumption Layer

Üretilen verinin kullanılacağı sistemler:

- Web sitesi
- RAG altyapısı
- AI danışmanlık asistanı
- Telegram bot
- Dashboard
- Arama ve sınıflandırma sistemleri

---

## 6. Core Modüller

### 6.1 181 Master Production Controller

Görevi production zincirini uçtan uca yönetmektir.

Sorumlulukları:

- Batch limitini almak
- Pipeline adımlarını sırasıyla çalıştırmak
- Her adımı kontrol etmek
- Resume Engine ile checkpoint bırakmak
- Final state ve rapor üretmek
- Non-blocking uyarıları ayırmak
- Production ready kararını üretmek

### 6.2 192 Resume Engine

Görevi uzun üretimlerde kesinti sonrası kaldığı yerden devam etmeyi sağlamaktır.

Çözdüğü problemler:

- Elektrik kesintisi
- Python kapanması
- Ctrl+C
- Windows restart
- API timeout sonrası manuel devam
- İnternet kopması sonrası devam

Temel state mantığı:

```json
{
  "run_id": "...",
  "status": "RUNNING",
  "last_done_step": "172",
  "steps": {
    "168": {"status": "DONE"},
    "188": {"status": "DONE"},
    "172": {"status": "DONE"},
    "175": {"status": "RUNNING"}
  }
}
```

### 6.3 193 Smart Resume Validation

Görevi Resume Engine'in DONE dediği adımları teknik olarak doğrulamaktır.

Kontroller:

- output_path var mı?
- dosya boş mu?
- JSONL okunabilir mi?
- RUNNING adım var mı?
- FAIL adım var mı?
- resume güvenli mi?

Karar türleri:

- PASS
- WARNING
- FAIL

### 6.4 194 Production Guardian

Üretim başlamadan önce ortamı kontrol eder.

Kontroller:

- Gerekli klasörler var mı?
- Klasörler yazılabilir mi?
- Disk alanı yeterli mi?
- Kritik scriptler var mı?
- DB dosyası mevcut mu?
- Resume state okunabilir mi?
- Secret dosyası riski var mı?
- .gitignore doğru mu?

### 6.5 195 Runtime Monitor

Henüz geliştirilecek modüldür.

Hedef kontroller:

- RAM kullanımı
- Disk kullanımı
- Üretim hızı
- Ortalama kalite skoru
- Resume count
- Self-Healing count
- Auto-cleaner count
- Tahmini bitiş zamanı

---

## 7. Production Yaşam Döngüsü

Standart production akışı:

```text
Guardian
   |
   v
Controller
   |
   v
Resume Start
   |
   v
Production Generation
   |
   v
Auto Cleaning
   |
   v
AI QA
   |
   v
Coverage QA
   |
   v
Priority QA
   |
   v
Legal Accuracy QA
   |
   v
Self-Healing
   |
   v
Merge
   |
   v
Optimization
   |
   v
Complexity Analysis
   |
   v
DB Import
   |
   v
Export
   |
   v
Acceptance
   |
   v
Drift
   |
   v
Sampling
   |
   v
Dashboard
   |
   v
Supervisor
   |
   v
Finish
```

---

## 8. Resume Akışı

Kesinti senaryosu:

```text
168 DONE
188 DONE
172 DONE
175 RUNNING
   |
   X Kesinti
   |
   v
Program yeniden başlatılır
   |
   v
--resume=RUN_ID
   |
   v
168 RESUME OK
188 RESUME OK
172 RESUME OK
175 yeniden çalışır
```

Resume için temel kural:

- DONE adım tekrar çalıştırılmaz.
- RUNNING adım tamamlanmış sayılmaz.
- FAIL adım manuel inceleme gerektirir.
- Kritik output dosyası yoksa resume güvenli kabul edilmez.

---

## 9. Veri Akışı

Genel veri akışı:

```text
Kaynak karar / PDF / metin
        |
        v
168 Production Output
        |
        v
188 Clean Output
        |
        v
172 AI Quality
        |
        v
175 Coverage
        |
        v
176 Priority
        |
        v
177 Legal Accuracy
        |
        v
185 Self-Healing
        |
        v
178 Merge
        |
        v
179 Optimized Output
        |
        v
169 DB Import
        |
        v
170 Web + RAG Export
```

---

## 10. Kalite Güvence Katmanı

Kalite güvence modülleri:

| Modül | Kontrol |
|------|---------|
| 172 | AI kalite |
| 175 | Hukuki kapsam |
| 176 | Önceliklendirme |
| 177 | Hukuki doğruluk |
| 180 | Karmaşıklık / planlama |
| 173 | Final acceptance |
| 182 | Drift |
| 183 | Sampling QA |
| 184 | Dashboard |
| 190 | Supervisor |

---

## 11. Self-Healing Mimarisi

Temel akış:

```text
177 Legal Accuracy FAIL
        |
        v
185 Correction
        |
        v
177 Recheck
        |
        v
PASS_AFTER_185
```

Gerekirse ikinci katman:

```text
177 Recheck FAIL
        |
        v
185 v2 Quarantine
        |
        v
177 Final Recheck
        |
        v
PASS_AFTER_185V2
```

---

## 12. Guardian Politikası

Production başlamadan önce 194 çalıştırılmalıdır.

Örnek:

```bat
python ".py\194_Production_Guardian.py" 1000
```

Karar:

- PASS: üretim başlayabilir.
- WARNING: üretim başlayabilir ama uyarılar incelenmelidir.
- FAIL: üretim başlamamalıdır.

---

## 13. Runtime Monitor Hedefi

195 Runtime Monitor geliştirildiğinde üretim sırasında şu metrikleri takip edecektir:

- Batch ilerlemesi
- RAM
- Disk
- Resume count
- Self-healing count
- Ortalama AI kalite
- Ortalama hukuki doğruluk
- Ortalama kapsam
- Tahmini bitiş zamanı

Örnek dashboard:

```text
PRODUCTION RUNTIME

Batch              : 125 / 1000
RAM                : 42%
Disk Free          : 618 GB
Resume Count       : 1
Self-Healing       : 3
Auto Cleaner       : 5
Average AI         : 92.4
Average Legal      : 93.6
Estimated Finish   : 03:15
```

---

## 14. GitHub Sürüm Politikası

### Branch Yapısı

| Branch | Amaç |
|--------|------|
| main | En güncel doğrulanmış production |
| develop | Yeni geliştirmeler ve testler |

### Tag Politikası

Her büyük milestone tag ile sabitlenir.

Örnekler:

- v1.0-production-250-pass
- v1.1-production-500-pass
- v1.2-resume-engine-validation
- v2.0-production-platform-stable

### Release Notes

Her milestone için:

```text
docs/releases/
```

altında Markdown dosyası oluşturulur.

---

## 15. Dokümantasyon Politikası

Önemli belgeler:

```text
docs/
  architecture/
  decisions/
  releases/
  runbooks/
```

Yeni büyük teknik kararlar ADR olarak saklanacaktır.

Örnek:

```text
docs/decisions/ADR-001-github-versioning-and-milestones.md
```

---

## 16. Production Kuralları

1. PASS almayan modül production'a alınmaz.
2. Stable dosyalara doğrudan müdahale edilmez.
3. Yeni geliştirme yeni versiyonda yapılır.
4. Büyük üretim öncesi Guardian çalıştırılır.
5. Resume destekli üretimde RUN_ID saklanır.
6. Release notu olmayan milestone tamamlanmış sayılmaz.
7. GitHub'a secret, DB, log, export ve production output yüklenmez.
8. main yalnızca doğrulanmış sürüm içermelidir.
9. develop aktif geliştirme alanıdır.
10. Her büyük değişiklik için tag oluşturulur.

---

## 17. Riskler

| Risk | Önlem |
|------|-------|
| Elektrik kesintisi | UPS + Resume |
| Output dosyası kaybı | Smart Resume Validation |
| Disk dolması | Guardian |
| Hatalı kart üretimi | QA + Self-Healing |
| DB bozulması | Import kontrollü yapılmalı |
| GitHub'a secret gitmesi | .gitignore + kontrol |
| Uzun üretimde takip zorluğu | Runtime Monitor |

---

## 18. v2.0 Yol Haritası

### Kısa Vadeli

- 195 Runtime Monitor
- 100 batch test
- 500 batch resume stress test
- 1000 batch validation

### Orta Vadeli

- 196 Analytics Engine
- 197 Recovery Manager
- 198 Distributed Processing
- 199 Production Manager
- 200 Platform Core

### Uzun Vadeli

- 10.000 batch pilot
- 100.000 karar üretimi
- Web/RAG entegrasyonu
- NeoLegal AI danışmanlık asistanı

---

## 19. v2.0 Stabil Olma Kriterleri

v2.0 Stable için aşağıdaki kriterler aranacaktır:

- 194 Guardian PASS/WARNING
- 181 v14 veya v15 production PASS
- 192 Resume PASS
- 193 Smart Resume PASS/WARNING
- 195 Runtime Monitor çalışır durumda
- 100 batch PASS
- 500 batch resume stress PASS
- 1000 batch validation PASS
- GitHub release notes hazır
- Tag oluşturulmuş

---

## 20. Sonuç

NeoLegal Production Platform v2.0, kamu ihale hukuku alanında yüksek hacimli karar verisinin yapay zekâ destekli, kalite kontrollü, kesintiye dayanıklı ve sürüm kontrollü biçimde üretilmesini sağlayan kurumsal production mimarisidir.

Bu belge, bundan sonraki geliştirmeler için ana mimari referans olarak kabul edilir.
