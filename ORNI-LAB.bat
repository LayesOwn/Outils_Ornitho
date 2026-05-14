@echo off
chcp 65001 >nul
title ORNI-LAB — Lancement
cd /d "%~dp0"

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║       ORNI-LAB — Laboratoire Ornithologique         ║
echo  ║         Développé par Abdoulaye Diop — 2026         ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERREUR] Python introuvable. Installez Python 3.10+ et réessayez.
    pause
    exit /b 1
)

:: Vérifier Streamlit
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo  [ERREUR] Streamlit non installé. Exécutez : pip install streamlit
    pause
    exit /b 1
)

:: Libérer le port 8501 si occupé
echo  Libération du port 8501...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8501 "') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo  Démarrage de l'application...
echo.

:: Lancer Streamlit en arrière-plan
start /B "" python -m streamlit run app\main.py ^
    --server.port 8501 ^
    --server.headless true ^
    --browser.gatherUsageStats false ^
    --server.fileWatcherType none

:: Attendre que le serveur soit prêt
set /a tries=0
:wait_loop
timeout /t 1 /nobreak >nul
set /a tries+=1
curl -s http://localhost:8501 >nul 2>&1
if not errorlevel 1 goto ready
if %tries% lss 15 goto wait_loop

:ready
echo  ┌─────────────────────────────────────────────────────┐
echo  │  ✓ Application prête sur http://localhost:8501      │
echo  │    Fermer cette fenêtre pour arrêter l'application  │
echo  └─────────────────────────────────────────────────────┘
echo.

:: Ouvrir le navigateur
start "" http://localhost:8501

:: Maintenir le processus actif
:keep_alive
timeout /t 5 /nobreak >nul
goto keep_alive
