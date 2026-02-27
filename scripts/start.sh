#!/bin/bash
# ========================================
# Field Booker — Start Script
# ========================================

set -e

echo "🏟️  Field Booker — Starting..."

docker compose up -d --build

echo ""
echo "✅ All services started!"
echo ""
echo "🌐 Frontend:      http://localhost"
echo "🔐 Auth API:       http://localhost/api/auth/docs"
echo "⚽ Fields API:     http://localhost/api/fields/docs"
echo "📝 Submissions API: http://localhost/api/submissions/docs"
echo ""
echo "📊 View logs: docker compose logs -f"
echo "🛑 Stop:      ./scripts/stop.sh"
