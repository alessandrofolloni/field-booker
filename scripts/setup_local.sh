#!/bin/bash
# ========================================
# Field Booker — Local Setup (No Docker)
# ========================================

set -e

echo "🏟️  Field Booker — Local Setup"
echo "=============================="

# 1. Python Venv
echo "🐍 Creating Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements-all.txt

# 2. Frontend
echo "🎨 Installing Frontend dependencies..."
cd services/frontend
npm install
cd ../..

# 3. Environment Config
if [ ! -f .env ]; then
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  NOTE: Remember to edit .env with your Google credentials."
fi

# 4. Check for Database URL
if grep -q "@db:5432" .env; then
    echo "🔧 Adjusting DATABASE_URL for local execution (db -> localhost)..."
    sed -i '' 's/@db:5432/@localhost:5432/g' .env 2>/dev/null || sed -i 's/@db:5432/@localhost:5432/g' .env
fi

echo ""
echo "✅ Setup completato!"
echo "-------------------"
echo "Per avviare l'app:"
echo "1. Assicurati che PostgreSQL/PostGIS sia attivo (brew services start postgresql@16)"
echo "2. Esegui: ./scripts/run_local.sh"
