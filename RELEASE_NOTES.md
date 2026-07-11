# NeoLegal Legal Relationship Engine v1.0.0

## Production Release

Bu sürüm, KİK kararları ile İdare Mahkemesi kararları arasındaki doğrulanmış ilişkileri web sitesi, API ve veri tabanı katmanlarında kullanıma hazır hale getirir.

## Release Özeti

- Kaynak ilişki satırı: **9,560**
- Yayınlanan ilişki satırı: **9,560**
- Benzersiz KİK kararı: **5,557**
- Benzersiz mahkeme kararı: **6,296**
- Doğrulama: **PASS**
- Eşleşme yöntemi: **Exact filename-key**
- Güven skoru: **100**
- Fuzzy/tahmini ilişki: **Yok**
- Kaynak SHA-256: `c01098a062f1270872611e14d3a6e58ea41246d79aea993e55c215c2000cfb88`

## Üretilen Bileşenler

- Web için KİK-bazlı `by_kik/*.json`
- Toplu JSON / JSONL / CSV
- SQLite ilişki veritabanı
- SQL şeması
- Admin yerel-yol eşleme paketi
- Release manifesti
- Doğrulama raporu

## Web Kullanımı

KİK karar sayfasında ilgili mahkeme kararlarını göstermek için:

```text
public/by_kik/{kik_slug}.json
```

Önerilen API:

```text
GET /api/kik/{kik_slug}/mahkeme-kararlari
```

## Sürüm Politikası

Bu sürüm üretim için dondurulmuştur.

Bundan sonra:

- Yeni özellik bu sürüme eklenmez.
- Yalnız hata düzeltmeleri `v1.0.x` olarak yayımlanır.
- Yeni yetenekler sonraki minor/major sürümlerde geliştirilir.
- Kaynak veri değişirse yeni manifest ve SHA-256 üretilir.

## Sonraki Aşama

251 Real Execute Pilot:

```text
10 gerçek karar → 50 → 100 → 500
```
