@echo off
chcp 65001 >nul
title PPT Dönüştürücü
color 0A

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║       PPT → VEKTÖR + TXT  DÖNÜŞTÜRÜCÜ          ║
echo  ╠══════════════════════════════════════════════════╣
echo  ║                                                  ║
echo  ║  "input" klasörüne PPT dosyalarınızı            ║
echo  ║  koyun ve bu dosyaya çift tıklayın.             ║
echo  ║                                                  ║
echo  ║  Ne yapar:                                       ║
echo  ║  1. PPT lerdeki metinleri çıkarır               ║
echo  ║  2. AI vektörlerine dönüştürür                   ║
echo  ║  3. TXT dosyalarına aktarır                      ║
echo  ║                                                  ║
echo  ║  Çıktılar:                                       ║
echo  ║  • "output\vectors" → vektörler + metadata      ║
echo  ║  • "output\txt"     → metin dosyaları           ║
echo  ║  • "output\reports" → HTML raporlar             ║
echo  ║                                                  ║
echo  ╚══════════════════════════════════════════════════╝
echo.

echo  [1/3] PPT dosyaları okunuyor ve metin çıkarılıyor...
echo  [2/3] AI vektörlerine dönüştürülüyor (biraz sürebilir)...
echo  [3/3] TXT dosyalarına aktarılıyor...
echo.

python "%~dp0..\src\ppt_to_vectors.py" --all --txt

echo.
if %ERRORLEVEL% EQU 0 (
    color 0A
    echo  ISLEM BASARIYLA TAMAMLANDI!
    echo.
    echo  Sonuclar icin su klasorlere bakin:
    echo    output\vectors\  - vektorler, metadata, rapor
    echo    output\txt\      - metin dosyaları
) else (
    color 0C
    echo  HATA OLUSTU! Lutfen yukardaki mesajlari kontrol edin.
)

echo.
echo  Kapatmak icin bir tusa basin...
pause >nul
