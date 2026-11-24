@echo off
cd /d "%~dp0"

if not exist "%~dp0.venv\Scripts\pythonw.exe" (
    echo [ERROR] Python tidak ditemukan di %~dp0.venv
    pause
    exit /b 1
)

echo Membuka Epic Seven Penguin ^& Stigma Farmer sebagai Administrator...
powershell -NoProfile -Command "Start-Process '%~dp0.venv\Scripts\pythonw.exe' -ArgumentList '\"%~dp0E7PenguinFarmer.py\"' -WorkingDirectory '%~dp0' -Verb RunAs"
