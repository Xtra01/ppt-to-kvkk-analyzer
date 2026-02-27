<div align="center">

# 🛡️ PPT → KVKK Analyzer

**PPT dosyalarını AI vektörlerine dönüştürün · KVKK değişikliklerini otomatik analiz edin**

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![sentence-transformers](https://img.shields.io/badge/sentence--transformers-multilingual-orange)](https://www.sbert.net/)
[![KVKK](https://img.shields.io/badge/KVKK-6698%20%2B%207499-red)](https://kvkk.gov.tr)

[🇹🇷 Türkçe](#-türkçe) · [🇬🇧 English](#-english)

</div>

---

## 🇹🇷 Türkçe

### Nedir?

**PPT → KVKK Analyzer**, PowerPoint sunumlarını üç farklı biçimde işleyen açık kaynaklı bir araçtır:

| Özellik | Açıklama |
|---|---|
| 🧠 **AI Vektörleştirme** | Slayt metinlerini semantik arama yapılabilir 384 boyutlu vektörlere dönüştürür |
| 📄 **TXT Dışa Aktarım** | Her PPT dosyasını slayt numaralı, temiz metin olarak kaydeder |
| ⚖️ **KVKK Değişiklik Raporu** | 6698 ve 7499 sayılı kanun değişikliklerini PPT metinlerinden otomatik tespit eder, eski/yeni hal karşılaştırması içeren zengin HTML rapor üretir |

### ⚡ Hızlı Başlangıç

```bash
# 1. Repoyu klonla
git clone https://github.com/Xtra01/ppt-to-kvkk-analyzer.git
cd ppt-to-kvkk-analyzer

# 2. Sanal ortam oluştur ve bağımlılıkları yükle
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt

# 3. PPT dosyalarını kaynaklar/ klasörüne koy

# 4. Çalıştır
python src/ppt_to_vectors.py --all --txt   # Vektörleştir + TXT dışa aktar
python src/kvkk_rapor.py                   # KVKK HTML raporu oluştur
```

> **Kodlama bilmiyorsanız:** `CALISTIR.bat` → `RAPOR_OLUSTUR.bat` sırasıyla çift tıklayın.

### 📁 Proje Yapısı

```
ppt-to-kvkk-analyzer/
├── src/                    # Python kaynak kodları
│   ├── ppt_to_vectors.py   # PPT → vektör + TXT pipeline
│   └── kvkk_rapor.py       # KVKK analiz & HTML rapor
├── docs/                   # Detaylı belgeler
├── kaynaklar/              # PPT dosyalarınızı buraya koyun
├── çıktılar/
│   ├── vektorler/          # vectors.npy, metadata.json
│   ├── txt/                # Metin dışa aktarımları
│   └── raporlar/           # HTML raporlar
├── CALISTIR.bat            # Tek tıkla çalıştır (Windows)
├── ARA.bat                 # Semantik arama (Windows)
├── RAPOR_OLUSTUR.bat       # KVKK raporu (Windows)
├── config.toml             # Yapılandırma ayarları
└── requirements.txt
```

### 🖥️ Komut Satırı Kullanımı

```bash
# Tüm pipeline (çıkarma + vektörleştirme + TXT)
python src/ppt_to_vectors.py --all --txt

# Yalnızca metin çıkar
python src/ppt_to_vectors.py --extract

# Yalnızca vektörleştir
python src/ppt_to_vectors.py --vectorize

# Semantik arama (top-5)
python src/ppt_to_vectors.py --search "kişisel veri işleme şartları" --top-k 5

# KVKK raporu (yerel veri)
python src/kvkk_rapor.py

# KVKK raporu (mevzuat.gov.tr canlı veri)
python src/kvkk_rapor.py --online

# Özel çıktı adı
python src/kvkk_rapor.py --cikti ozet_rapor.html
```

### 📊 Teknik Detaylar

| Bileşen | Teknoloji |
|---|---|
| Embedding Modeli | `paraphrase-multilingual-MiniLM-L12-v2` (Türkçe destekli) |
| Vektör Boyutu | 384 |
| Benzerlik Metriği | Kosinüs benzerliği (normalize_embeddings=True) |
| Rapor Formatı | Bootstrap 5 + Plotly (self-contained HTML) |
| Desteklenen Format | `.pptx` |

### ⚙️ Yapılandırma

`config.toml` ile varsayılanları değiştirebilirsiniz:

```toml
[model]
name = "paraphrase-multilingual-MiniLM-L12-v2"

[chunking]
min_chars = 40
max_chars = 800

[search]
default_top_k = 5
```

---

## 🇬🇧 English

### What is it?

**PPT → KVKK Analyzer** is an open-source toolkit that processes PowerPoint presentations in three ways:

- **AI Vectorization**: Converts slide text into 384-dimensional semantic vectors for similarity search
- **TXT Export**: Exports each PPT as a clean, slide-numbered text file
- **KVKK Change Report**: Auto-detects Law No. 6698 and 7499 amendments from PPT text, generates a rich HTML report with side-by-side old/new comparisons

> **KVKK** = Turkey's Personal Data Protection Law (equivalent to GDPR)

### Quick Start

```bash
git clone https://github.com/Xtra01/ppt-to-kvkk-analyzer.git
cd ppt-to-kvkk-analyzer
pip install -r requirements.txt

# Place your PPTX files in kaynaklar/
python src/ppt_to_vectors.py --all --txt
python src/kvkk_rapor.py
```

### License

This project is licensed under [CC BY-NC 4.0](LICENSE) — free for personal and educational use, **not for commercial use**. For commercial licensing, contact [ekremregister@gmail.com](mailto:ekremregister@gmail.com).

---

<div align="center">
Made with ❤️ by <a href="https://github.com/Xtra01">Xtra01</a> · 2025
</div>
