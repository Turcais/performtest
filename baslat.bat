@echo off
chcp 65001 >nul
title PerformTest Platformu (Next.js + Python API)
echo ============================================================================
echo   PerformTest Studio Dağıtım & Geliştirme Ortamı Başlatılıyor...
echo   - Next.js Web Frontend : http://localhost:3000/
echo   - Backend REST API     : http://localhost:8000/api/v1/health
echo   - Admin & KVKK Paneli  : http://localhost:3000/admin
echo ============================================================================

cd /d "%~dp0"

echo [1/2] Python REST API motoru arka planda başlatılıyor...
start "PerformTest API (Port 8000)" py -3.14 -m api.main

echo [2/2] Next.js Web Frontend başlatılıyor...
cd frontend
npm run start

pause
