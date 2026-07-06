\# ADR-001: GitHub Versioning and Milestone Policy



Tarih: 06.07.2026



\## Karar



NeoLegal projesinde GitHub yalnızca kod deposu değil, resmi sürüm ve milestone hafızası olarak kullanılacaktır.



\## Branch Yapısı



\- main: Stabil ve doğrulanmış production sürümleri.

\- develop: Yeni geliştirmeler, testler ve deneysel çalışmalar.



\## Tag Politikası



Her büyük production başarısı tag ile sabitlenecektir.



Örnekler:



\- v1.0-production-250-pass

\- v1.1-production-500-pass

\- v1.2-resume-engine

\- v2.0-production-1000-pass



\## Rapor Politikası



Geçici loglar, state dosyaları ve üretim çıktıları GitHub'a gönderilmeyecektir.



Ancak milestone raporları docs/releases altında saklanacaktır.



\## Gerekçe



Bu yaklaşım depoyu temiz tutar, geri dönüş noktalarını korur ve projenin tarihsel gelişimini izlenebilir hale getirir.

