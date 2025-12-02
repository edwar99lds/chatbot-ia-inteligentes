@echo off
setlocal enabledelayedexpansion

echo === Activando entorno (si existe) ===
if exist ".\venv\Scripts\activate.bat" (
  call ".\venv\Scripts\activate.bat"
) else (
  echo (No se encontro .\venv\Scripts\activate.bat, continuando con Python del sistema)
)

echo.
echo === Paso 1/3: EVALUATE ===
python --version
python evaluate.py
if errorlevel 1 (
  echo [ERROR] evaluate.py fallo
  exit /b 1
)

echo.
echo === Paso 2/3: ENRICH ===
python enrich_results.py
if errorlevel 1 (
  echo [ERROR] enrich_results.py fallo
  exit /b 1
)

echo.
echo === Paso 3/3: SUMMARIZE ===
python summarize_results.py
if errorlevel 1 (
  echo [ERROR] summarize_results.py fallo
  exit /b 1
)

echo.
echo === ✅ Flujo completado. Revisa la carpeta logs/ ===
endlocal
