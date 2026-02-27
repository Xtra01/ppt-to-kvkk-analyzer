@echo off
chcp 65001 >nul
title KVKK Rapor Oluşturucu
color 0B

echo.
echo  ╔═════════════════════════════════════════════════════╗
echo  ║     KVKK DEĞİŞİKLİK ANALİZ RAPORU                ║
echo  ╠═════════════════════════════════════════════════════╣
echo  ║                                                     ║
echo  ║  PPT verilerini analiz eder ve KVKK kanun         ║
echo  ║  maddelerindeki değişiklikleri karşılaştırır.     ║
echo  ║                                                     ║
echo  ║  Çıktı:                                            ║
echo  ║  • çıktılar\raporlar\KVKK_Analiz_Raporu.html     ║
echo  ║  (Tarayıcıda açın)                                 ║
echo  ║                                                     ║
echo  ╚═════════════════════════════════════════════════════╝
echo.

set /p ONLINE="  İnternet üzerinden mevzuat.gov.tr verisi çekilsin mi? (e/h): "

echo.
if /i "%ONLINE%"=="e" (
    echo  [→] Rapor oluşturuluyor (resmi kaynak dahil)...
    python "%~dp0..\src\kvkk_rapor.py" --online
) else (
    echo  [→] Rapor oluşturuluyor (yerel veri)...
    python "%~dp0..\src\kvkk_rapor.py"
)

echo.
if %ERRORLEVEL% EQU 0 (
    color 0A
    echo  ✓ RAPOR OLUŞTURULDU!
    echo.
    echo  Dosyayı açmak için:
    echo    çıktılar\raporlar\KVKK_Analiz_Raporu.html
    echo.
    echo  Raporu tarayıcıda açıyor...
    timeout /t 2 /nobreak >nul
    start "" "%~dp0..\output\reports\KVKK_Analiz_Raporu.html"
) else (
    color 0C
    echo  ✗ HATA OLUŞTU! Önce CALISTIR.bat ile vektörleri oluşturun.
)

echo.
echo  Kapatmak için bir tuşa basın...
pause >nul
