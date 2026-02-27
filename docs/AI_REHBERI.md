# 🤖 AI Modelleri için Çıktı Hazırlama Rehberi

Bu kılavuz, üretilen çıktı dosyalarından hangi AI'ya hangisini, nasıl vermeniz gerektiğini açıklar.

---

## Seçenek 1: output/vectors/metadata.json — Önerilen

**Boyut:** ~1.5 MB | **Format:** JSON (yapılandırılmış)

### Nedir?
- 1946 metin parçası (chunk)
- Her parçanın metni, kaynak dosyası ve slayt numarası
- Model bilgisi (hangi embedding kullanıldığı)

### Kime Ver?
- ✅ Claude (Anthropic)
- ✅ ChatGPT (OpenAI)
- ✅ Gemini (Google)
- ✅ LLaMA (Meta)
- ✅ Herhangi bir LLM veya RAG sistemi

### Python ile nasıl okunur?

```python
import json

with open('output/vectors/metadata.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for chunk in data['chunks']:
    print(chunk['metin'])
    print(f"Kaynak: {chunk['dosya']} - Slayt {chunk['slayt_no']}")
```

### Avantajları
- Tüm bilgi tek dosyada
- Yapılandırılmış (JSON)
- Dosya + slayt referans bilgisi kaybolmaz
- Vektörlerle eşleştirilebilir

---

## Seçenek 2: output/vectors/vectors.npy — Vektör Aramaları

**Boyut:** ~3 MB | **Format:** NumPy binary

### Nedir?
1946 × 384 boyutlu float32 matris. Her satır, bir metin parçasına karşılık gelen anlam vektörüdür.

### Kime Ver?
- ✅ FAISS, Chroma, Weaviate, Pinecone (vektör veritabanları)
- ✅ LangChain, LlamaIndex (RAG framework'leri)
- ✅ Scikit-learn (clustering, analiz)

### Python ile nasıl okunur?

```python
import numpy as np
import json

vektorler = np.load('output/vectors/vectors.npy')   # shape: (1946, 384)

with open('output/vectors/metadata.json', 'r', encoding='utf-8') as f:
    meta = json.load(f)

chunks = meta['chunks']
# Örnek: 0. chunk vektörü
print(vektorler[0])
print(chunks[0]['metin'])
```

---

## Seçenek 3: output/txt/*.txt — Ham Metin

**Boyut:** ~5 MB toplam | **Format:** Düz metin, slayt numaralı

### Nedir?
Her PPT dosyası için ayrı bir TXT dosyası. Slayt aramalar, hızlı okuma ve basit LLM besleme için idealdir.

### Kime Ver?
- ✅ Uzun bağlam penceresi olan modeller (GPT-4 Turbo, Claude 3.5 vb.)
- ✅ NotebookLM, Perplexity gibi belge tabanlı AI'lar
- ✅ Basit grep ve metin arama araçları

### Örnek içerik

```
── Slayt 1 ──────────────────────────────────
KVKK Sertifika Programı

── Slayt 2 ──────────────────────────────────
MADDE 6- (1) Kişilerin ırkı, etnik kökeni...
```

---

## Seçenek 4: output/reports/KVKK_Analiz_Raporu.html — İnsan Okuma

**Boyut:** ~98 KB | **Format:** Tarayıcıda açılır HTML

### Nedir?
KVKK kanun maddelerini, değişiklikleri (6698 + 7499) ve PPT atıf istatistiklerini görsel olarak sunar.

### Kime Ver?
- 🔍 İnsanlar — tarayıcıda açın, paylaşın
- ❌ AI modellerine çevirme (HTML gürültüsü bilgiyi kirletir)

---

## Özet Tablo

| Kullanım Amacı | Kullanılacak Dosya |
|---|---|
| LLM'e tüm içeriği ver | metadata.json |
| Vektör DB'ye yükle | ectors.npy + metadata.json |
| RAG sistemi kur | ectors.npy + metadata.json |
| Hızlı metin okuma | output/txt/*.txt |
| İnsan raporlama | output/reports/*.html |
| Semantik arama | python src/ppt_to_vectors.py --search "sorgu" |