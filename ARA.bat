@echo off
chcp 65001 >nul
title PPT'lerde Arama
color 0B

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║       PPT İÇERİKLERİNDE SEMANTİK ARAMA         ║
echo  ╠══════════════════════════════════════════════════╣
echo  ║                                                  ║
echo  ║  Önce CALISTIR.bat ile dönüştürme yapılmalı!    ║
echo  ║  Sonra bu dosya ile arama yapabilirsiniz.       ║
echo  ║                                                  ║
echo  ╚══════════════════════════════════════════════════╝
echo.

set /p SORGU="  Aramak istediğiniz konuyu yazın: "

echo.
echo  Aranıyor: "%SORGU%"
echo  Lütfen bekleyin...
echo.

python "%~dp0src\ppt_to_vectors.py" --search "%SORGU%" --top-k 5

echo.
echo  Yeni arama yapmak için tekrar çalıştırın.
echo  Kapatmak için bir tuşa basın...
pause >nul
