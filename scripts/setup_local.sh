#!/bin/bash
# ========================================
# Field Booker — Local Setup (No Docker)
# ========================================

set -e

echo "🏟️  Field Booker — Local Setup"
echo "=============================="

# 1. Python venv
echo "🐍 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
for svc in auth fields submissions ai_assistant; do
    pip install -r "services/$svc/requirements.txt"
done

# 2. Frontend
echo "🎨 Installing frontend dependencies..."
(cd services/frontend && npm install)

# 3. Environment
if [ ! -f .env ]; then
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Edit .env with your Google credentials before running."
fi

# 4. Fix DATABASE_URL for local (Docker uses @db:5432)
if grep -q "@db:5432" .env; then
    echo "🔧 Adjusting DATABASE_URL for localhost..."
    sed -i '' 's/@db:5432/@localhost:5432/g' .env 2>/dev/null || \
    sed -i  's/@db:5432/@localhost:5432/g' .env
fi

echo ""
echo "✅ Setup complete!"
echo "------------------"
echo "Next steps:"
echo "1. Make sure PostgreSQL/PostGIS is running (brew services start postgresql@16)"
echo "2. Run: ./scripts/run_local.sh"
