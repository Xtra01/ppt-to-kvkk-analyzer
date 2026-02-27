@echo off
chcp 65001 >nul
title PPT Dönüştürücü
color 0A

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║       PPT → VEKTÖR + TXT  DÖNÜŞTÜRÜCÜ          ║
echo  ╠══════════════════════════════════════════════════╣
echo  ║                                                  ║
echo  ║  "kaynaklar" klasörüne PPT dosyalarınızı        ║
echo  ║  koyun ve bu dosyaya çift tıklayın.             ║
echo  ║                                                  ║
echo  ║  Ne yapar:                                       ║
echo  ║  1. PPT'lerdeki metinleri çıkarır               ║
echo  ║  2. AI vektörlerine dönüştürür                   ║
echo  ║  3. TXT dosyalarına aktarır                      ║
echo  ║                                                  ║
echo  ║  Çıktılar:                                       ║
echo  ║  • "çıktılar\vektorler" → vektörler + metadata  ║
echo  ║  • "çıktılar\txt"       → metin dosyaları       ║
echo  ║  • "çıktılar\raporlar"  → HTML raporlar         ║
echo  ║                                                  ║
echo  ╚══════════════════════════════════════════════════╝
echo.

echo  [1/3] PPT dosyaları okunuyor ve metin çıkarılıyor...
echo  [2/3] AI vektörlerine dönüştürülüyor (biraz sürebilir)...
echo  [3/3] TXT dosyalarına aktarılıyor...
echo.

python "%~dp0src\ppt_to_vectors.py" --all --txt

echo.
if %ERRORLEVEL% EQU 0 (
    color 0A
    echo  ✓ İŞLEM BAŞARIYLA TAMAMLANDI!
    echo.
    echo  Sonuçlar için şu klasörlere bakın:
    echo    • çıktılar\vektorler\  → vektörler, metadata, rapor
    echo    • çıktılar\txt\        → metin dosyaları
) else (
    color 0C
    echo  ✗ HATA OLUŞTU! Lütfen yukarıdaki mesajları kontrol edin.
)

echo.
echo  Kapatmak için bir tuşa basın...
pause >nul
