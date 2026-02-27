# 📋 PPT → VEKTÖR + TXT DÖNÜŞTÜRÜCÜ PROJESİ

## 📌 Proje Özeti

Bu proje **PowerPoint dosyalarını yapılandırılmış metin ve AI vektörlerine dönüştüren** bir otomasyondur.

**Ana hedef:** KVKK (Kişisel Verilerin Korunması Kanunu) sertifika sunumlarından metinleri çıkarıp, AI modellerinin anlayabileceği **semantik vektörlere** dönüştürmek ve aranabilir hale getirmek.

---

## 🏗️ Proje Yapısı

```
ppt to text/
├── kaynaklar/                    ← PPT dosyalarını BU klasöre koy
│   ├── 1- KVKK Sertifika Programı.pptx
│   ├── 2- KVKK Sertifika Programı.pptx
│   └── ... (8 dosya toplamı)
│
├── çıktılar/                     ← Vektör + metadata çıkışı
│   ├── vectors.npy               ← Vektör matrisi (1946×384)
│   ├── metadata.json             ← Tüm metin parçaları + bilgi
│   ├── extracted_chunks.json     ← Ham metin parçaları
│   └── ozet_rapor.txt            ← İnsan tarafından okunabilir rapor
│
├── txt çıktılar/                 ← TXT dışa aktarma
│   ├── 1- KVKK Sertifika Programı.txt
│   ├── 2- KVKK Sertifika Programı.txt
│   └── ... (8 dosya toplamı)
│
├── kodlar/
│   ├── ppt_to_vectors.py         ← Ana uygulama (474 satır)
│   └── requirements.txt           ← Python bağımlılıkları
│
├── CALISTIR.bat                  ← Tüm pipeline'ı çalıştır (çift tıkla)
├── ARA.bat                        ← Semantik arama yap (çift tıkla)
└── README.md                      ← Bu dosya
```

---

## ⚙️ İşlem Akışı (Pipeline)

### 1️⃣ **METİN ÇIKARMA** (Extract)
```
PPT Dosyaları → Slaytlar → Shape Parsing → Ham Metin
```

**Ne yapılır:**
- 8 PPTX dosyası taranır
- Her slayt, metin çerçeveleri ve tablolardan metin çıkarılır
- İç içe şekiller (grup şekilleri) da işlenir
- Sonuç: **1519 slayt = 1946 metin parçası**

**Çıktı:** `extracted_chunks.json`
```json
[
  {
    "id": 0,
    "dosya": "2- KVKK Sertifika Programı.pptx",
    "slayt_no": 1,
    "parca_no": 1,
    "metin": "KVKK Sertifika Programı..."
  },
  ...
]
```

---

### 2️⃣ **PARÇALAMA** (Chunking)
```
Uzun Metinler → Semantik Parçalar (max 500 karakter)
```

**Neden?**
- AI modelleri çok uzun metinleri daha az iyi işler
- Aramalarda daha spesifik sonuçlar elde etmek

**Yöntem:**
- Paragraf sınırlarına uyarak böl
- Paragraf çok uzunsa kelime bazlı böl
- 20 karakterden kısa parçaları sil

**Parametre:**
- `CHUNK_MAX_CHARS = 500` — bir parçanın max uzunluğu
- `MIN_CHUNK_CHARS = 20` — minimum uzunluk filtresi

---

### 3️⃣ **VEKTÖRLEŞTİRME** (Embedding)
```
Metin Parçaları → Semantik Vektörler (1946×384)
```

**Model:** `paraphrase-multilingual-MiniLM-L12-v2`
- 50+ dili destekler (Türkçe dahil ✓)
- Hafif (471 MB) ama etkili
- Normalize edilmiş vektörler (cosine similarity için)
- Boyut: **384**

**Proses:**
```
1946 metin → SentenceTransformer → [384 boyutlu vektör] × 1946 parça
```

**Çıktı:** `vectors.npy` (NumPy matris + `metadata.json`)

---

### 4️⃣ **TXT DI ŞA AKTARMA** (Export)
```
PPT Dosyaları → Düzenli TXT Metinleri
```

**Her dosya için:**
- Dosya adı başlık olarak yazılır
- Slaytlar `── Slayt N` ile ayrılır
- Tüm metinler sırayla yazılır

**İnsan Tarafından Okunabilir Format:**
```
════════════════════════════════════════════════════════
  1- KVKK Sertifika Programı
════════════════════════════════════════════════════════

── Slayt 1 ────────────────────────────────────────────
KVKK Sertifika Programı
KVKK Kanunu Giriş

── Slayt 2 ────────────────────────────────────────────
...
```

**Çıktı:** `txt çıktılar/` klasöründe 8 adet `.txt` dosyası

---

### 5️⃣ **SEMANTİK ARAMA** (Search)
```
"kişisel verilerin korunması" → Vektör Dönüştür → Cosine Similarity → Top-5 Sonuç
```

**Nasıl çalışır:**
1. Sorgu metni vektöre dönüştürülür
2. Tüm metin parçası vektörleriyle karşılaştırılır
3. En benzer 5 parça bulunur (**cosine similarity** ile)
4. Dosya + Slayt + İlgililik skoru gösterilir

**Örnek:**
```
ARAMA: "kişisel verilerin korunması"

  #1  Benzerlik: 0.8486
  Dosya : 7- KVKK Sertifika Programı.pptx  |  Slayt: 22
  Kişisel Verilerin Hukuken Korunması

  #2  Benzerlik: 0.8439
  Dosya : 4- KVKK Sertifika Programı.pptx  |  Slayt: 20
  Kişisel Verilerin Korunmasına Yönelik Gelişmeler
```

---

## 📂 ÇIKTI DOSYALARI DETAYLI

### 📊 `çıktılar/vectors.npy`
- **Format:** NumPy binary
- **Boyut:** 1946 × 384 (çift hassasiyet float)
- **Boyut (disk):** ~3 MB
- **İçerik:** Vektör matrisi
- **Kullanım:** AI arama / benzerlik karşılaştırmalı

### 📄 `çıktılar/metadata.json`
- **Format:** Yapılandırılmış JSON
- **İçerik:**
  - Model adı ve vektör boyutu
  - Tüm 1946 metin parçası + metadata
  - Dosya adı, slayt numarası, parça numarası
- **Boyut:** ~1.5 MB
- **Kullanım:** `vectors.npy` ile eşleştirme (hangi vektör hangi metne ait)

### 📋 `çıktılar/extracted_chunks.json`
- **Format:** JSON (metadata.json'ın bir alt kümesi)
- **İçerik:** Sadece çıkarılan metin parçaları (metadata olmadan)
- **Boyut:** ~500 KB
- **Kullanım:** Vektörsüz metin analizi

### 📊 `çıktılar/ozet_rapor.txt`
- **Format:** İnsan tarafından okunabilir metin
- **İçerik:**
  - Model bilgisi
  - Vektör boyutu (384)
  - Toplam parça (1946)
  - Dosya başına parça dağılımı
  - Çıktı dosyası açıklamaları
- **Boyut:** ~1 KB

### 📝 `txt çıktılar/*.txt` (8 dosya)
- **Format:** UTF-8 metin
- **İçerik:** Her PPTX dosyasının tüm metni, slayt bazında düzenlenmiş
- **Toplam:** ~5 MB
- **Kullanım:** Doğrudan sırada okuma veya başka araçlarla işleme

---

## 🔧 Teknik Parametreler

| Parameter | Değer | Açıklama |
|-----------|-------|----------|
| **MODEL_NAME** | `paraphrase-multilingual-MiniLM-L12-v2` | Embedding modeli |
| **CHUNK_MAX_CHARS** | 500 | Maksimum parça boyutu |
| **MIN_CHUNK_CHARS** | 20 | Minimum parça boyutu |
| **Batch Size (Encode)** | 32 | Vektör oluşturma batch'i |
| **Normalize Embeddings** | True | Cosine similarity için |
| **Vektör Boyutu** | 384 | Model çıktısı |
| **Toplam Parça** | 1946 | Çıkartılan metin sayısı |

---

## 💻 Kullanım Şekilleri

### 🖱️ **Grafik (Non-Teknik Kullanıcılar)**

1. **CALISTIR.bat**'a çift tıkla
   - Tüm PPT'leri otomatik işler
   - Vektörler + TXT oluşturur

2. **ARA.bat**'a çift tıkla
   - Sorgu gir
   - Sonuç al

### 🖥️ **Komut Satırı (Teknik Kullanıcılar)**

```bash
# Tüm işlem (çıkarma + vektörleştirme + TXT)
python kodlar/ppt_to_vectors.py --all --txt

# Sadece metin çıkarma
python kodlar/ppt_to_vectors.py --extract

# Sadece vektörleştirme (extracted_chunks.json gerekli)
python kodlar/ppt_to_vectors.py --vectorize

# Sadece TXT aktarma
python kodlar/ppt_to_vectors.py --txt

# Semantik arama
python kodlar/ppt_to_vectors.py --search "KVKK yaptırımları"
python kodlar/ppt_to_vectors.py --search "veri sahibi" --top-k 10
```

---

## 🤖 BAŞKA BİR AI'A PPT'LERİ OKUTMAK İÇİN HANGI ÇIKTI?

### **OPSIYON 1: Metin Parçaları (Tavsiye Edilen) ❌ YANLŞ**

❌ **`metadata.json` → Metin Parçaları**
```json
{
  "chunks": [
    {"id": 0, "dosya": "...", "slayt_no": 1, "metin": "..."},
    {"id": 1, "dosya": "...", "slayt_no": 1, "metin": "..."},
    ...
  ]
}
```

**Avantajları:**
- Yapılandırılmış, tam bilgi içerir
- Metin formatı (llmler direkt okuyabilir)
- Dosya/slayt referans bilgisi var
- Kontekst kaybı yok

**Kullanım:**
```python
import json
with open('çıktılar/metadata.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    chunks = data['chunks']  # 1946 metin parçası
```

---

### **OPSIYON 2: TXT Dosyaları → Birleştir (En Basit)**

```bash
# Tüm TXT'leri bir dosyaya birleştir
type "txt çıktılar\*.txt" > tum_metinler.txt
```

**Avantajları:**
- İnsan tarafından okunabilir
- Slayt sırası korunur
- Dosya sınırlaması yok

**Dezavantajları:**
- Metin parçaları değil, slaytlar olarak gelir
- Vektör bilgisi yok

---

### **OPSIYON 3: Direkt PPT → AI (Opsiyonel)**

Bazı AI'lar (Claude, GPT-4V) PPT'leri direkt okuyabilir, ama **bu projede çıkarılan metinler daha kontrollü çünkü:**
- Tablo hücreleri ve metin çerçeveleri açık şekilde çıkarılmış
- Slayt numaraları biliniyor
- Arama yapılabiliyor

---

## ✅ SONUÇ: Hangi Dosyayı Verdim?

| AI Tipi | Verin |
|---------|-------|
| **LLM tabanlı (GPT, Claude, Gemini)** | `çıktılar/metadata.json` **veya** `txt çıktılar/*.txt` (birleştirilmiş) |
| **Diğer Vektör Sistemleri** | `çıktılar/vectors.npy` + `çıktılar/metadata.json` |
| **Tam Otomatik İşlem** | Tüm dosyalar: `çıktılar/` + `txt çıktılar/` |
| **Basit Okuma/Tarama** | `txt çıktılar/` klasörü |

---

## 📊 Proje Sonuçları

| Metrik | Değer |
|--------|-------|
| **İnput** | 8 PPTX dosyası |
| **Toplam Slayt** | 1519 |
| **Çıkarılan Parça** | 1946 |
| **Vektör Matrisi** | 1946 × 384 |
| **Model** | paraphrase-multilingual-MiniLM-L12-v2 |
| **Toplam Çıktı Boyutu** | ~10 MB |
| **İşlem Süresi** | ~60 saniye |

---

## 🔍 Başa Dönüş Kontrol Listesi

- [ ] `kaynaklar/` içinde PPTX dosyaları var mı?
- [ ] `CALISTIR.bat` dosyası var mı?
- [ ] Python 3.10+ yüklü mü? (`python --version`)
- [ ] Gerekli paketler yüklü mü? (`pip list | findstr "sentence-transformers"`)
- [ ] İlk çalıştırma 60-120 saniye sürebilir (model cache)
- [ ] `çıktılar/` ve `txt çıktılar/` klasörleri oluştu mu?

---

## 📞 Hızlı Destek

| Problem | Çözüm |
|---------|-------|
| **"Python bulunamadı"** | Python yükleyin (python.org) |
| **"ModuleNotFoundError"** | `pip install -r kodlar/requirements.txt` |
| **Başında yavaş** | Model ilk kez indiriliyordur (internet bağlantısı gerekli) |
| **Türkçe karakterler görünmüyor** | Metin editörünü UTF-8'de açın |
| **Arama sonucu yok** | Önce `CALISTIR.bat` ile vektör oluşturun |

---

**Hazırlayan:** GitHub Copilot  
**Tarih:** 27 Şubat 2026  
**Versiyon:** 1.0
