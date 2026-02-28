# KVKK Belge Görselleştiricisi

> **ppt-to-kvkk-analyzer** projesinin alt modülü — Resmi KVKK PDF belgelerini interaktif tek sayfalık HTML dashboard'a dönüştürür.

---

## 📄 Kaynak Belgeler

| Dosya | İçerik | Sayfa |
|---|---|---|
| `kvkk 1.5.6698.pdf` | 6698 Sayılı KVKK Kanun Metni | 21 |
| `sorularla-verbis.pdf` | Sorularla VERBİS | 61 |
| `veri-sorumlulari-sicil-bilgi-sistemi-kilavuzu.pdf` | VERBİS Kayıt Kılavuzu | 98 |

PDF dosyaları proje kökündeki `KVKK/` klasöründe bulunmalıdır.

---

## 🗂️ Proje Yapısı

```
kvkk-visualizer/
├── src/
│   ├── __init__.py
│   ├── pdf_extractor.py       ← PDF → JSON önbellek
│   ├── law_parser.py          ← 6698 madde ayrıştırıcı
│   ├── verbis_parser.py       ← VERBİS veri modeli
│   └── dashboard_builder.py  ← HTML dashboard üretici
├── output/
│   ├── cache/                 ← Önbelleklenmiş JSON (otomatik)
│   └── dashboard/
│       └── KVKK_Dashboard.html  ← Üretilen dashboard
├── tests/
│   └── test_parsers.py        ← 28 birim + entegrasyon testi
├── BUILD.bat                  ← Windows çalıştırıcı
├── pyproject.toml
└── README.md
```

---

## 🚀 Kullanım

### Windows (en kolay)
```bat
kvkk-visualizer\BUILD.bat
```

### Python (manuel)
```bash
# e:\Programming\ppt to text dizininde
.venv\Scripts\python.exe kvkk-visualizer\src\dashboard_builder.py

# Önbelleği sıfırlamak için:
.venv\Scripts\python.exe kvkk-visualizer\src\dashboard_builder.py --force
```

---

## 🎯 Dashboard Özellikleri

### 📜 Kanun Metni Sekmesi
- **32 maddenin tam metni** — Madde bazında aç/kapat kartlar
- **7 bölüm navigasyonu** — Sol kenar çubuğuyla hızlı atlama
- **⭐ Önemli maddeler** vurgulanmış (6, 9, 10, 11, 12, 16, 18)
- **⚡ Değişiklik rozetleri** — 7499 sayılı Kanun ile değiştirilen maddeler
- **Canlı metin araması** — Madde no veya başlıkta anlık filtre
- Koyu mod + yazdırma desteği

### 🗄️ VERBİS Rehberi Sekmesi
- **6 adımlı kayıt yol haritası** — Süre ve gereksinimlerle birlikte
- **İdari para cezaları tablosu** — Alt/üst sınır (Madde 18, 2024 güncel)
- verbis.kvkk.gov.tr bağlantıları

### 💬 S&S Sekmesi
- **10 resmi soru & cevap** (Kapsam, Başvuru, Envanter, Güncelleme, Yaptırımlar)
- Kategori filtresi + metin arama
- Önemli sorular ⭐ ile vurgulanmış

### 📊 İstatistikler Sekmesi
- Bölümlere göre metin yoğunluğu (Chart.js çubuk)
- VERBİS kayıtlarında işleme hacmi (doughnut)
- Hukuki dayanak dağılımı (pie)
- Madde önem görünümü

### 🔄 Değişiklikler Sekmesi
- 7499 sayılı Kanun tüm değişiklikleri tablosu
- 2016–2024 arası **interaktif zaman çizelgesi**
- GDPR uyumluluk notu

---

## 🧪 Testler

```bash
# Ana proje kökünden:
.venv\Scripts\python.exe -m pytest kvkk-visualizer\tests\ -v
```

**28 test** — PDF olmadan 23'ü çalışır, PDF varsa tümü:

| Kategori | Test |
|---|---|
| Import sağlığı | 5 |
| Kanun parser | 10 |
| VERBİS parser | 9 |
| Dashboard builder | 10 |
| PDF entegrasyon | 5 (skipif PDF yok) |

---

## ⚙️ Bağımlılıklar

Ana projenin `requirements.txt`'ine eklenmiştir:
```
pdfplumber>=0.10.0
```

*Bootstrap 5 ve Chart.js CDN üzerinden yüklenir (internet bağlantısı gerekir).*

---

## 📝 Lisans

Bu alt proje, ana proje lisansına (CC BY-NC 4.0) tabidir.
