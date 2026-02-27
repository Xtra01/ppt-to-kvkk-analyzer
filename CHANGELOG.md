# Değişiklik Günlüğü / Changelog

Bu proje [Anlamsal Sürümleme (Semantic Versioning)](https://semver.org/) kullanır.

---

## [1.2.0] – 2025-02-28

### Eklendi
- **PPT'den otomatik değişiklik notasyonu çıkarıcı**: `(Değişik:...)`, `(Mülga:...)`, `(Ek:...)` notasyonları
  PPT slaytlarından makine tarafından otomatik tespit edilip raporlanıyor
- **Madde 6 değişikliği**: 7499/33 md. ile Fıkra 2 mülga, Fıkra 3 yeniden düzenlendi (veritabanına eklendi)
- **Geçici Madde 3**: 7499/36 md. ek bilgisi raporlara yansıtıldı
- **PPT kanıtı alanı**: Her değişik madde kartında slayt numarası referansı
- `kvkk_rapor.py`: 6 adım pipeline (önceki 5 adım)

### Değiştirildi
- Proje klasör yapısı yeniden düzenlendi: `kodlar/` → `src/`, `belgeler/` → `docs/`
- `requirements.txt` kök dizine taşındı
- 7499 sayılı Kanunun etkilediği maddeler güncellendi: `[9, 18]` → `[6, 9, 18]`

### Düzeltildi
- Rapor HTML'indeki PPT kaynak dağılımı pasta grafiğinde dosya adı kısaltması

---

## [1.1.0] – 2025-02-27

### Eklendi
- **KVKK Değişiklik Analiz Raporu** (`src/kvkk_rapor.py`):
  - Bootstrap 5 + Plotly self-contained HTML raporu
  - Madde bazlı atıf sıklığı çubuk grafiği
  - Kaynak PPT dağılımı pasta grafiği
  - Değişiklik sinyal çubuğu
  - CSS zaman çizelgesi
  - Eski/yeni hal karşılaştırma kartları (Madde 9, 18)
  - Resmi kaynak linkleri (mevzuat.gov.tr, resmigazete.gov.tr, kvkk.gov.tr)
  - İsteğe bağlı online mevzuat çekicisi (`--online`)
- `RAPOR_OLUSTUR.bat` – Tek tıkla KVKK raporu

### Değiştirildi
- Klasör yapısı yeniden organize edildi:
  - `çıktılar/vektorler/` – vektörler ve metadata
  - `çıktılar/txt/` – metin dışa aktarımları
  - `çıktılar/raporlar/` – HTML raporlar

---

## [1.0.1] – 2025-02-25

### Düzeltildi
- Windows konsolunda Türkçe karakter hatası: `UnicodeEncodeError` giderildi
  (`sys.stdout = io.TextIOWrapper(..., encoding="utf-8")`)
- BAT dosyalarında `chcp 65001` eklendi

---

## [1.0.0] – 2025-02-24

### İlk Sürüm
- **PPT → Vektör Pipeline**: `python-pptx` + `sentence-transformers` (multilingual MiniLM)
- **TXT Dışa Aktarım**: Slayt numaralı temiz metin çıkarımı
- **Semantik Arama**: Kosinüs benzerliği ile `--search` komutu
- **Toplu İşlem**: `--all` ile tüm PPT'leri tek komutta işle
- `CALISTIR.bat` + `ARA.bat` – Kodlama bilmeyenler için
- Desteklenen format: `.pptx` (python-pptx 1.0+)
