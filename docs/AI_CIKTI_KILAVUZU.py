"""
AI MODELLERİ İÇİN PPT ÇIKTI HAZIRLAMA KILAVUZU
===============================================

Bu dosya, oluşturulan farklı çıktıları hangi AI'ya vermeli olduğunuzu açıklar.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# SEÇENEK 1: METADATA.JSON (EN İYİ - YAPILANDI.RILMIŞ VERİ)
# ═══════════════════════════════════════════════════════════════════════════════

"""
DOSYA: çıktılar/metadata.json
BOYUT: ~1.5 MB
FORMAT: JSON (yapılandırılmış)

NEDİR:
  • 1946 metin parçasının tümü
  • Her parçanın metni, kaynak dosyası, slayt numarası
  • Model bilgisi (hangi embedding kullanıldığı)

KİME VER:
  ✓ Claude (Anthropic)
  ✓ ChatGPT (OpenAI)
  ✓ Gemini (Google)
  ✓ LLaMA (Meta)
  ✓ Herhangi bir LLM
  ✓ Herhangi bir vektör veritabanı
  ✓ RAG (Retrieval-Augmented Generation) sistemleri

NASIL KULLANSİN:
  1. metadata.json dosyasını aç
  2. "chunks" dizisini oku
  3. Her chunk'ın "metin" alanı AI'ın işleyeceği veri

PYTHON ÖRNEK:
  import json
  with open('çıktılar/metadata.json', 'r', encoding='utf-8') as f:
      data = json.load(f)
      for chunk in data['chunks']:
          print(chunk['metin'])
          print(f"Kaynak: {chunk['dosya']} - Slayt {chunk['slayt_no']}")

AVANTAJLARI:
  ✓ Tüm bilgi bir dosyada
  ✓ Yapılandırılmış (JSON)
  ✓ Dosya + slayt referans bilgisi kaybılmaz
  ✓ İndekslenmiş (ID'ler 0'dan başlayarak sıralanmış)
  ✓ Vektörlerle eşleştirilebilir
  ✓ En az 90% bilgi kaybı yok

TAVSİYE: ⭐⭐⭐⭐⭐ BUNU VER!
"""

# ═══════════════════════════════════════════════════════════════════════════════
# SEÇENEK 2: TXT ÇIKTILAR (İNSAN TARAFINDAN OKUNABILIR)
# ═══════════════════════════════════════════════════════════════════════════════

"""
DOSYA: txt çıktılar/*.txt (8 adet dosya)
TOPLAM BOYUT: ~5 MB
FORMAT: Düz metin (UTF-8)

NEDİR:
  • Her PPTX dosyası = bir TXT dosyası
  • Slaytlar "── Slayt N" ile ayrılmış
  • İnsan tarafından direkt okunabilir

KİME VER:
  ✓ Metin analiz araçları
  ✓ Kelime frekansı contabaran
  ✓ Doğal dil işleme (NLP)
  ✓ Herhangi bir AI (hızlı, basit)

AVANTAJLARI:
  ✓ İnsan tarafından okunabilir
  ✓ Editlenebilir
  ✓ Slayt sırası korunmuş
  ✓ Basit, anlaşılır format

DESAVANTAJLARİ:
  ✗ Metin parçalı değil, slayt bazlı
  ✗ Yapı bilgisi (ID, dosya adı metadata) yok
  ✗ Vektörlerle eşleştirilemez
  ✗ 8 dosya, tekil değil

KULLANIM:
  • Tüm TXT dosyalarını birleştir:
    type "txt çıktılar\*.txt" > tum_pptler.txt
  • Sonra tum_pptler.txt'yi AI'a ver

PYTHON ÖRNEK:
  from pathlib import Path
  txt_dir = Path('txt çıktılar')
  all_text = ""
  for txt_file in sorted(txt_dir.glob('*.txt')):
      with open(txt_file, 'r', encoding='utf-8') as f:
          all_text += f.read() + "\n\n"
  # all_text'i AI'a gönder

TAVSİYE: ⭐⭐⭐ BASIT OKUMA İÇİN OKAYDİR
"""

# ═══════════════════════════════════════════════════════════════════════════════
# SEÇENEK 3: VECTORS.NPY (VEKTÖRLER - SADECE ARAŞTIRMA İÇİN)
# ═══════════════════════════════════════════════════════════════════════════════

"""
DOSYA: çıktılar/vectors.npy
BOYUT: ~3 MB
FORMAT: NumPy binary (float32)

NEDİR:
  • 1946 metin parçasının vektörize edilmiş hali
  • Her satır = bir parçanın 384 boyutlu vektörü
  • Binary format (okunması zor)

KİME VER:
  ✓ Vektör araması yapan sistemlere
  ✓ Machine learning modelleri
  ✓ Similarity search sistemleri
  ✓ Başka embedding modellerine

NASIL KULLANSİN:
  import numpy as np
  vectors = np.load('çıktılar/vectors.npy')
  print(vectors.shape)  # (1946, 384)
  
  # Benzer parçaları bul
  from sklearn.metrics.pairwise import cosine_similarity
  similarity = cosine_similarity([vectors[0]], vectors)[0]

AVANTAJI:
  ✓ Hızlı vektör araması
  ✓ Benzerlik karşılaştırması
  ✓ Clustering yapılabilir
  ✓ Kompakt format

DESAVANTAJLARİ:
  ✗ Metni içermez (metadata.json'la eşleştirme gerekli)
  ✗ Binary format (editlenemez)
  ✗ Hangı metinin hangı vektör olduğu bilinmez

⚠️ ÖNEMLİ: vectors.npy'i MUTLAKA metadata.json ile birlikte ver!

TAVSİYE: ⭐⭐ Sadece vektör tabanlı arama sistemleri için
"""

# ═══════════════════════════════════════════════════════════════════════════════
# SEÇENEK 4: EXTRACTED_CHUNKS.JSON (HAM METİN)
# ═══════════════════════════════════════════════════════════════════════════════

"""
DOSYA: çıktılar/extracted_chunks.json
BOYUT: ~500 KB
FORMAT: JSON (yapılandırılmış)

NEDİR:
  • metadata.json'ın bir alt kümesi
  • SADECE metin parçaları, metadata olmadan
  • metadata.json'dan daha hafif

KİME VER:
  ✓ Hafif metin işleme için
  ✓ metadata.json çok ağır gelirse
  ✓ Vektörlerin gerekli olmadığı sistemler

DEĞERLENDİRME:
  ✗ Nadiren kullanılır
  ✗ metadata.json tercih edilir (daha eleştirel)

TAVSİYE: ⭐ metadata.json'ı kullan
"""

# ═══════════════════════════════════════════════════════════════════════════════
# ÖZETİ: HANGI ÇIKTI HANGİ AI'YA?
# ═══════════════════════════════════════════════════════════════════════════════

"""
┌─────────────────────────────────────────────────────────────────┐
│                  ÇIKTI SEÇİM KARAR AĞACI                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Başka bir AI'a veri vermek istiyorum                           │
│  ↓                                                              │
│  Yapılandırılmış metin gerekli mi?                             │
│  │                                                              │
│  ├─ EVET → metadata.json ⭐⭐⭐⭐⭐ (EN İYİ)                     │
│  │  Neden: Tüm bilgi, JSON formatı, başka platformlar tarafı   │
│  │         doğrudan kullanılabilir                             │
│  │                                                              │
│  └─ HAYIR → txt çıktılar/ ⭐⭐⭐ (İYİ)                           │
│     Neden: Basit, okunabilir, email'le gönderilebilir          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

PRATIKTE:
  • ChatGPT'ye gönder       → metadata.json
  • Claude'a gönder         → metadata.json
  • Bir vektör DB'ye koy    → metadata.json + vectors.npy
  • Email'le bildir         → tum_pptler.txt (txt'leri birleştir)
  • Dosya deposuna koy      → tüm çıktılar/ klasörü
  • Yedekleme               → tüm çıktılar/ klasörü

UNIVERSAL ÇÖZÜM:
  → metadata.json
  
  Taşınabilir, standarttır, tüm AI'lar okuyabilir.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# METADATA.JSON STRUKTÜRÜnün AÇIKLAMASI
# ═══════════════════════════════════════════════════════════════════════════════

"""
{
  "model": "paraphrase-multilingual-MiniLM-L12-v2",
  "vektor_boyutu": 384,
  "toplam_parca": 1946,
  "chunks": [
    {
      "id": 0,                              # Benzersiz parça ID'si
      "dosya": "2- KVKK Sertifika Programı.pptx",  # Hangi dosyadan geldi
      "slayt_no": 1,                        # Hangi slayt numarası
      "parca_no": 1,                        # Slayt içindeki kaçıncı parça
      "metin": "KVKK Sertifika Programı..." # ASIL METİN (AI bunu okuyor)
    },
    {
      "id": 1,
      "dosya": "2- KVKK Sertifika Programı.pptx",
      "slayt_no": 1,
      "parca_no": 2,
      "metin": "Kanunun Amacı..."
    },
    ...
  ]
}

AI'ya verirken:
  • Chunks dizisinden tüm metin parçalarını al
  • Sırayla AI'ya besleme
  • Gerekirse dosya/slayt bilgisini context olarak ekle
"""

# ═══════════════════════════════════════════════════════════════════════════════
# SONUÇ
# ═══════════════════════════════════════════════════════════════════════════════

"""
🎯 EN NET CEVAP:

Başka bir AI'a single-shot (tek çıkardı) vermeleceksin?

  ▶ DİCID: çıktılar/metadata.json

Neden?
  1. Yapılandırılmış (JSON)
  2. Tüm bilgi bir dosyada
  3. Dosya + slayt referansları korunmuş
  4. Tüm AI'lar (LLM, vektör DB, vb.) okuyabilir
  5. Taşınabilir, platform-agnostik
  6. İnsan tarafından da okunabilir
  7. Diğer araçlarla işlenebilir

Alt seçenek (metin yeterli):
  ▶ txt çıktılar/*.txt (birleştirilmiş)

Ama "en iyi" → metadata.json
"""
