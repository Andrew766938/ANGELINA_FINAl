#!/bin/bash

# 🚀 Скрипт для автоматической настройки проекта (Mac/Linux)
# Automatic setup script for project (Mac/Linux)

set -e  # Выход при ошибке / Exit on error

echo ""
echo "╭─────────────────────────────────────────────────────────────────╮"
echo "│   🚀 Krylya Online - Automatic Setup Script               │"
echo "╰─────────────────────────────────────────────────────────────────╯"
echo ""

# Проверка Python версии / Check Python version
echo "🔍 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $PYTHON_VERSION"

# Проверка наличия uv / Check if uv is available
echo ""
echo "📦 Installing dependencies..."
if command -v uv &> /dev/null; then
    echo "✅ Using uv (faster)"
    uv sync
else
    echo "ℹ️  uv not found, using pip"
    pip install -r requirements.txt
fi

# Копирование .env / Copy .env
echo ""
echo "⚙️  Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env file created from .env.example"
else
    echo "ℹ️  .env file already exists"
fi

# Очистка кэша / Clean cache
echo ""
echo "🧹 Cleaning Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✅ Cache cleaned"

# Проверка БД / Check database
echo ""
echo "🗄️  Checking database..."
if [ -f test.db ]; then
    echo "ℹ️  Database already exists"
else
    echo "ℹ️  Database will be created on first run"
fi

# Готово / Done
echo ""
echo "╭─────────────────────────────────────────────────────────────────╮"
echo "│   ✅ Setup Complete!                                     │"
echo "╰─────────────────────────────────────────────────────────────────╯"
echo ""
echo "🚀 To start the API, run:"
echo "   uvicorn main:app --reload"
echo ""
echo "🌐 Then open: http://localhost:8000"
echo ""
