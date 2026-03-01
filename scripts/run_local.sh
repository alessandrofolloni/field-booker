#!/bin/bash
# ========================================
# Field Booker — Local Runner (No Docker)
# ========================================

# Kill leftover processes from previous runs
echo "🧹 Cleaning up previous processes..."
pkill -f uvicorn || true
pkill -f vite || true
lsof -ti:8001,8002,8003,8004,5173 | xargs kill -9 2>/dev/null || true

cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $(jobs -p) 2>/dev/null
    exit
}
trap cleanup SIGINT SIGTERM

set -e

echo "🏟️  Field Booker — Starting..."
echo "=============================="

if [ ! -d "venv" ]; then
    echo "❌ venv not found. Run ./scripts/setup_local.sh first"
    exit 1
fi

source venv/bin/activate

# Copy .env to frontend (Vite needs it)
cp .env services/frontend/.env

# Auto-fix API URL for local dev (no Nginx, Vite proxies instead)
if grep -q "VITE_API_BASE_URL=http://localhost/api" .env; then
    echo "🔧 Fixing VITE_API_BASE_URL for local dev..."
    sed -i '' 's|localhost/api|localhost:5173/api|g' .env 2>/dev/null || \
    sed -i  's|localhost/api|localhost:5173/api|g' .env
fi

# Start microservices
echo "🔐 [1/5] Auth Service (8001)..."
(cd services/auth && PYTHONPATH=$(pwd)/.. uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload) > auth.log 2>&1 &

echo "⚽ [2/5] Fields Service (8002)..."
(cd services/fields && PYTHONPATH=$(pwd)/.. uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload) > fields.log 2>&1 &

echo "📝 [3/5] Submissions Service (8003)..."
(cd services/submissions && PYTHONPATH=$(pwd)/.. uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload) > submissions.log 2>&1 &

echo "🤖 [4/5] AI Assistant (8004)..."
(cd services/ai_assistant && PYTHONPATH=$(pwd)/.. uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload) > ai_assistant.log 2>&1 &

echo "🎨 [5/5] Frontend (5173)..."
(cd services/frontend && npm run dev -- --port 5173) > frontend.log 2>&1 &

echo ""
echo "🚀 All services started!"
echo "------------------------"
echo "🌐 Frontend:  http://localhost:5173"
echo "📊 Logs:      auth.log, fields.log, submissions.log, ai_assistant.log, frontend.log"
echo ""
echo "Press CTRL+C to stop all services."

wait
