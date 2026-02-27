#!/bin/bash
# ========================================
# Field Booker — Setup Script
# ========================================
# First-time setup: copies .env, builds and starts all services

set -e

echo "🏟️  Field Booker — Setup"
echo "========================"

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Copy .env if not exists
if [ ! -f .env ]; then
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your actual credentials before running start.sh"
    echo "   Required: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, ADMIN_EMAILS"
    exit 0
fi

# Build all services
echo "🔨 Building all services..."
docker compose build

# Start everything
echo "🚀 Starting all services..."
docker compose up -d

# Wait for database
echo "⏳ Waiting for database to be ready..."
sleep 5

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Frontend:      http://localhost"
echo "🔐 Auth API:       http://localhost/api/auth/docs"
echo "⚽ Fields API:     http://localhost/api/fields/docs"
echo "📝 Submissions API: http://localhost/api/submissions/docs"
echo "🗄️  Database:       localhost:5432"
echo ""
echo "📊 View logs: docker compose logs -f"
echo "🛑 Stop:      ./scripts/stop.sh"
