# CHANGELOG

Bu dosya NeoLegal Production Platform'un sürüm geçmişini içerir.

---

# v1.4 – Platform Core Services

**Tarih:** 07.07.2026

## Yeni Modüller

### 199 – Production Manager

- Service Registry
- Platform Health Manager
- Orchestrator
- Package Manager

### 200 – Platform Core

- Platform Core
- Configuration Manager
- Package yapısı
- Core servis katmanı

### 201 – Event Bus

- Event Bus
- Event Publisher
- Event Bus Viewer / Auditor
- JSONL event log

### 202 – Platform Scheduler

- Scheduler Registry
- Scheduler Engine
- Execution Plan
- Scheduler History

### 203 – Central Logger

- Merkezi Logger
- Logger Test
- Logger Auditor
- JSONL tabanlı log altyapısı

## Mimari Kazanımlar

Bu sürüm ile platform:

- Katmanlı mimariye geçmiştir.
- Servis tabanlı yapıya taşınmıştır.
- Platform Core katmanı oluşturulmuştur.
- Merkezi Event Bus altyapısı kurulmuştur.
- Merkezi Scheduler altyapısı oluşturulmuştur.
- Merkezi Logger altyapısı oluşturulmuştur.
- Paket mimarisi standart hale getirilmiştir.

## Production Durumu

| Bileşen | Durum |
|---|:---:|
| Production Certification | PASS |
| Recovery | PASS |
| Queue | PASS |
| Worker | PASS |
| Platform Core | PASS |
| Event Bus | PASS |
| Scheduler | PASS |
| Logger | PASS |

## Sonraki Hedef

204 Metrics & Monitoring
