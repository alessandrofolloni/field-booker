#!/bin/bash
# ========================================
# Field Booker — RUNNER LOCAL (No Docker)
# ========================================

# 1. Pulizia processi precedenti
echo "🧹 Pulizia processi esistenti..."
pkill -f uvicorn || true
pkill -f vite || true
lsof -ti:8001,8002,8003,5173 | xargs kill -9 2>/dev/null || true

# Funzione per fermare tutto all'uscita
cleanup() {
    echo ""
    echo "🛑 Spegnimento di tutti i servizi..."
    kill $(jobs -p) 2>/dev/null
    exit
}
trap cleanup SIGINT SIGTERM

set -e

echo "🏟️  Field Booker — Avvio in corso..."
echo "=================================="

# Verifica venv
if [ ! -d "venv" ]; then
    echo "❌ venv non trovato. Esegui prima ./scripts/setup_local.sh"
    exit 1
fi

source venv/bin/activate

# 2. Copia .env nel frontend (necessario per Vite)
echo "📋 Copio .env nel frontend..."
cp .env services/frontend/.env

# 3. Correzione automatica .env per local-dev
# In locale senza Docker (Nginx), il frontend deve puntare alla sua stessa porta per il proxy
if grep -q "VITE_API_BASE_URL=http://localhost/api" .env; then
    echo "🔧 Aggiorno VITE_API_BASE_URL nel file .env..."
    sed -i '' 's/localhost\/api/localhost:5173\/api/g' .env 2>/dev/null || sed -i 's/localhost\/api/localhost:5173\/api/g' .env
fi

# 3. Avvio Microservizi
echo "🔐 [1/5] Starting Auth Service (8001)..."
(cd services/auth && export PYTHONPATH=$PYTHONPATH:$(pwd)/.. && uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload) > auth.log 2>&1 &

echo "⚽ [2/5] Starting Fields Service (8002)..."
(cd services/fields && export PYTHONPATH=$PYTHONPATH:$(pwd)/.. && uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload) > fields.log 2>&1 &

echo "📝 [3/5] Starting Submissions Service (8003)..."
(cd services/submissions && export PYTHONPATH=$PYTHONPATH:$(pwd)/.. && uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload) > submissions.log 2>&1 &

echo "🤖 [4/5] Starting AI Assistant (8004)..."
(cd services/ai_assistant && export PYTHONPATH=$PYTHONPATH:$(pwd)/.. && uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload) > ai_assistant.log 2>&1 &

echo "🎨 [5/5] Starting Frontend (5173)..."
cd services/frontend && npm run dev -- --port 5173 > ../../frontend.log 2>&1 &

echo ""
echo "🚀 TUTTO AVVIATO!"
echo "----------------"
echo "🌐 Frontend: http://localhost:5173"
echo "📊 Logs backend salvati in: auth.log, fields.log, submissions.log"
echo ""
echo "Premi CTRL+C per fermare tutti i servizi."

# Resta in attesa per catturare il CTRL+C
wait
