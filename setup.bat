@echo off
REM 🚀 Скрипт для автоматической настройки проекта (Windows)
REM Automatic setup script for project (Windows)

setlocal enabledelayedexpansion

echo.
echo ╭─────────────────────────────────────────────────────────╮
echo │   🚀 Krylya Online - Automatic Setup Script          │
echo ╰─────────────────────────────────────────────────────────╯
echo.

REM Проверка Python / Check Python
echo 🔍 Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.10+
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python version: %PYTHON_VERSION%

REM Она зависимостей / Install dependencies
echo.
echo 📦 Installing dependencies...
where uv >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Using uv (faster)
    call uv sync
) else (
    echo ℹ️  uv not found, using pip
    python -m pip install -r requirements.txt
)

if %errorlevel% neq 0 (
    echo ❌ Error installing dependencies!
    pause
    exit /b 1
)

REM Копирование .env / Copy .env
echo.
echo ⚙️  Setting up environment...
if not exist .env (
    copy .env.example .env >nul
    echo ✅ .env file created from .env.example
) else (
    echo ℹ️  .env file already exists
)

REM Очистка кэша / Clean cache
echo.
echo 🧹 Cleaning Python cache...
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        rd /s /q "%%d" 2>nul
    )
)
del /s /q *.pyc >nul 2>&1
echo ✅ Cache cleaned

REM Проверка БД / Check database
echo.
echo 🗄️  Checking database...
if exist test.db (
    echo ℹ️  Database already exists
) else (
    echo ℹ️  Database will be created on first run
)

REM Готово / Done
echo.
echo ╭─────────────────────────────────────────────────────────╮
echo │   ✅ Setup Complete!                                 │
echo ╰─────────────────────────────────────────────────────────╯
echo.
echo 🚀 To start the API, run:
echo    uvicorn main:app --reload
echo.
echo 🌐 Then open: http://localhost:8000
echo.
pause
