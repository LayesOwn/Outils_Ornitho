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

:: Chercher Python 3.14 en priorité, puis fallback sur python du PATH
set "PYTHON_EXE="
if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Python\bin\python.exe"
) else (
    python --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_EXE=python"
)
if "%PYTHON_EXE%"=="" (
    echo  [ERREUR] Python introuvable. Installez Python 3.10+ et reessayez.
    pause
    exit /b 1
)

:: Vérifier Streamlit
"%PYTHON_EXE%" -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo  [ERREUR] Streamlit non installe. Executez : pip install streamlit
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

:: Lancer Streamlit dans un processus détaché (survit à la fermeture de cette fenêtre)
start "" /MIN "%PYTHON_EXE%" -m streamlit run app\main.py ^
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
