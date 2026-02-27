# 🎯 NET VE HIZLI CEVAPLAR

## ❓ Soru 1: "Bu Proje Ne Yapar?"

**Basit:** PowerPoint'ten metinleri çıkarıp, AI'ların anlayabileceği vektörlere çeviriyor.

**Detaylı:**
1. 8 PPTX dosyasını oku
2. 1519 slayttan metinleri çıkar
3. 1946 parçaya böl
4. Her parçayı 384 boyutlu vektöre dönüştür
5. Aranabilir hale getir
6. Düz metin (TXT) halinde de vermiş

**Faydası:** PPT'lerde semantik arama yapabiliyorsun.

---

## ❓ Soru 2: "Başka AI'a PPT'leri Okutmalı mı?"

**CEVAP:** Hayır. Bu proje **çıkardığı veri**'leri ver.

**Hangisini ver?** → **`çıktılar/metadata.json`**

**Neden?**
- ✅ 1946 metin parçası
- ✅ JSON formatı (yapılandırılmış)
- ✅ Dosya + slayt bilgisi korunmuş
- ✅ Tüm AI'lar (ChatGPT, Claude, vb.) okuyabilir
- ✅ Vektörlerle eşleştirilmiş
- ✅ Taşınabilir, portable

**Alternatifleri:**
- `txt çıktılar/*.txt` → Metin yeterli ise, insan okunabilir
- `vectors.npy` → Sadece vektör tabanlı araştırma için (nadir)

---

## ❓ Soru 3: "metadata.json İçinde Ne Var?"

```json
{
  "model": "paraphrase-multilingual-MiniLM-L12-v2",
  "vektor_boyutu": 384,
  "toplam_parca": 1946,
  "chunks": [
    {
      "id": 0,
      "dosya": "1- KVKK Sertifika Programı.pptx",
      "slayt_no": 1,
      "parca_no": 1,
      "metin": "KVKK Kavram, Teori ve Güncel GeliĢmeler..."
    },
    ...
  ]
}
```

**Önemli:** Her chunk'ın `"metin"` alanı AI'ın okuyacağı veri.

---

## ❓ Soru 4: "Dosya Boyutları Ne?"

| Dosya | Boyut | Kullanım |
|-------|-------|----------|
| metadata.json | 1.5 MB | ⭐⭐⭐⭐⭐ BU'NUN VER |
| vectors.npy | 3 MB | Vektör araması |
| txt çıktılar/ | 5 MB | Okuma alışkanlığı |
| extracted_chunks.json | 500 KB | Fazla (metadata kafi) |

---

## ❓ Soru 5: "Başında Yapmalı Mı?"

### Eğer vektör araması yapacaksa:
✅ `vectors.npy` + `metadata.json` (ikisini birlikte)

### Eğer sadece metni analiz edecekse:
✅ `metadata.json` (yeterli)

### Eğer insan format isterirse:
✅ `txt çıktılar/` klasörü (8 dosya)

### Eğer tüm dosyayı tek dosyaya koyamıyorsa:
✅ TXT dosyalarını birleştir:
```bash
type "txt çıktılar\*.txt" > tum_pptler.txt
```

---

## ⭐ SONUÇ

```
Başka AI'a vermek isterse?
        ↓
       metadata.json
        ↓
    Bitti. İşi oldu.
```

**Daha detay ister mi?**
- README.md → Proje tamamı
- AI_CIKTI_KILAVUZU.py → Tüm seçenekler

---

## 🚀 Hızlı İşlem Sırası

1. `kaynaklar/` içine PPT koy
2. `CALISTIR.bat` çift tıkla
3. İşlem bitmesini bekle (~60-120s)
4. `çıktılar/metadata.json`'ı AI'ya ver
5. AI işler, sonuç al

**Seç - Çalıştır - Verisi Al**

---

## 📊 Proje İstatistikleri

| Metrik | Sayı |
|--------|------|
| Input PPTX | 8 |
| Slayt | 1519 |
| Metin Parçası | 1946 |
| Vektör | 1946 × 384 |
| Çıktı Dosyası | 5 tip |
| İşlem Süresi | 60-120 sn |

---

**Hazırlık:** Yeni başladı? → README.md oku  
**Detay lazım?** → AI_CIKTI_KILAVUZU.py oku  
**Hızlı cevap?** → Bu dosya yeterli
