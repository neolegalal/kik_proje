# ADR-200 — Platform Core Mimari Kararı

## Durum

NeoLegal Production Platform v2.0 kapsamında 181–199 arası temel üretim, kalite, recovery, queue, worker ve platform yönetim katmanları doğrulanmıştır.

Son doğrulanan durum:

- 196B Dynamic Certification: CERTIFIED
- 197 Recovery Manager: RECOVERY CLEAN
- 198 Queue / Worker / Controlled Execution: CERTIFIED
- 199 Package Manager: REGISTRY READY + PLATFORM READY

Bu aşamadan sonra platformun tek giriş noktası ve çekirdek işletim katmanı tanımlanmalıdır.

---

## Karar

200 Platform Core, NeoLegal Production Platform'un üst çekirdek katmanı olacaktır.

200'ün temel görevi:

- 199 Package Manager'ı çağırmak
- Platform health sonucunu okumak
- Sistemin çalışma modunu belirlemek
- Production Manager için merkezi entrypoint sağlamak
- Gelecekte Web, RAG ve NeoLegal AI tarafından çağrılabilecek stabil çekirdek arayüz oluşturmak

---

## 199 ile 200 arasındaki sınır

### 199 Production Manager

199 operasyonel yönetim katmanıdır.

Görevleri:

- Service Registry
- Platform Health
- Orchestration
- Queue / Worker koordinasyonu
- Production Manager davranışları

### 200 Platform Core

200 üst çekirdek katmandır.

Görevleri:

- Platformu tek komutla başlatmak
- 199'u çağırmak
- Core health kararını almak
- Run mode seçmek
- Gelecekte API / Web / RAG servislerine stabil çekirdek arayüz sunmak

---

## Kullanıcı komut standardı

Gelecekte ana komut:

```bat
python ".py\200_Platform_Core.py"
```

olacaktır.

199 bağımsız olarak kullanılmaya devam edecektir; ancak normal kullanıcı için ana giriş noktası 200 olacaktır.

---

## Çalışma modları

200 başlangıçta şu modları destekleyecektir:

- `--status`
- `--health`
- `--registry`
- `--plan`

Daha sonra:

- `--run`
- `--execute`
- `--worker`
- `--batch`
- `--production`

modları eklenecektir.

---

## İlk sürüm kapsamı

200 v1 yalnızca güvenli çekirdek başlangıç sürümü olacaktır.

Production çalıştırmayacaktır.

Yapacağı işler:

1. 199 Package Manager dosyasını kontrol eder.
2. 199 paket klasörünü kontrol eder.
3. Service Registry ve Health raporlarını tetikler.
4. Core kararını verir:
   - CORE READY
   - CORE REVIEW
   - CORE BLOCKED
5. Rapor üretir.

---

## Sonuç

Bu karar ile NeoLegal Production Platform artık yalnızca modül koleksiyonu olmaktan çıkarak çekirdek katmanı olan bir platform mimarisine dönüşmektedir.

200 Platform Core, Hedef 1'in tamamlanmasına giden son ana çekirdek katmanı olacaktır.
