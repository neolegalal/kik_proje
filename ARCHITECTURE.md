# ARCHITECTURE

## Genel Mimari

KİK Production Platform, Kamu İhale Kurulu kararlarını yapılandırılmış hukuki kartlara dönüştüren çok katmanlı bir üretim sistemidir.

Ana katmanlar:

1. Production Generation
2. Auto Cleaning
3. AI Quality
4. Legal Accuracy
5. Self-Healing
6. Merge / Optimization
7. DB Import
8. WEB / RAG Export
9. Drift Analysis
10. Sampling QA
11. Dashboard
12. Supervisor

## Final Controller

181 v13 Final Master Production Controller, tüm production zincirini tek komutla yönetir.

## Self-Healing

Sistem, kalite veya hukuki doğruluk hatalarını sadece raporlamakla kalmaz; mümkünse otomatik düzeltir veya karantinaya alır.

## Production Ready Kriteri

Bir batch için production ready sonucu şu koşullarla değerlendirilir:

- Üretim hatasız tamamlanmalı.
- AI kalite fail kalmamalı.
- Hukuki doğruluk fail kalmamalı.
- Self-healing başarılıysa ara fail kayıtları blok sayılmamalı.
- Drift WARNING sonucu non-blocking değerlendirilmelidir.
- DB import ve WEB/RAG export başarılı olmalıdır.
