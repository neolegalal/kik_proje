# NeoLegal Legal Relationship Engine v1.0.0

Bu release KİK kararları ile İdare Mahkemesi kararları arasındaki
doğrulanmış exact-match ilişkileri içerir.

## Web kullanımı

KİK karar sayfasında:

`public/by_kik/{kik_slug}.json`

Önerilen API:

`GET /api/kik/{kik_slug}/mahkeme-kararlari`

## Dosyalar

- `public/kik_index.json`
- `public/court_index.json`
- `public/kik_court_relationships.json`
- `public/kik_court_relationships.jsonl`
- `public/kik_court_relationships.csv`
- `public/neolegal_relationships.sqlite`
- `public/by_kik/*.json`
- `public/schema.sql`

## Güvenlik

Public klasöründe yerel Windows dosya yolları bulunmaz.
Yerel yollar yalnız admin klasöründe tutulur.

## Kesinlik

Bu release yalnız exact filename-key ilişkilerini içerir.
Fuzzy/tahmini ilişki yoktur.
Confidence = 100.
