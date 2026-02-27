#!/bin/bash
# ========================================
# Field Booker — Stop Script
# ========================================

set -e

echo "🛑 Field Booker — Stopping all services..."

docker compose down

echo "✅ All services stopped."
