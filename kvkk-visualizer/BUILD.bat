@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

cd /d "%~dp0.."
echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║   KVKK Belge Görselleştiricisi — Dashboard   ║
echo  ╚══════════════════════════════════════════════╝
echo.

:: Python sanal ortam kontrolü
set "PYTHON=%~dp0..\.venv\Scripts\python.exe"
if not exist "%PYTHON%" (
    echo  [HATA] .venv bulunamadi. Ana dizinde:
    echo         python -m venv .venv ^& .venv\Scripts\pip install -r requirements.txt
    pause & exit /b 1
)

:: PDF klasör kontrolü
if not exist "%~dp0..\KVKK\kvkk 1.5.6698.pdf" (
    echo  [HATA] KVKK klasoru veya PDF dosyalari eksik.
    echo         Lutfen asagidaki PDF'leri KVKK\ klasorune koyun:
    echo           - kvkk 1.5.6698.pdf
    echo           - sorularla-verbis.pdf
    echo           - veri-sorumlulari-sicil-bilgi-sistemi-kilavuzu.pdf
    pause & exit /b 1
)

:: Dashboard oluştur
set PYTHONUTF8=1
echo  [1/1] Dashboard olusturuluyor...
"%PYTHON%" "%~dp0src\dashboard_builder.py" %*
if errorlevel 1 (
    echo.
    echo  [HATA] Dashboard olusturulamadi.
    pause & exit /b 1
)

:: Tarayıcıda aç
set "HTML=%~dp0output\dashboard\KVKK_Dashboard.html"
if exist "%HTML%" (
    echo.
    echo  ════════════════════════════════════════════════
    echo   Dashboard hazir! Tarayicida aciliyor...
    echo  ════════════════════════════════════════════════
    echo.
    start "" "%HTML%"
) else (
    echo  [UYARI] HTML dosyasi bulunamadi: %HTML%
)

pause
