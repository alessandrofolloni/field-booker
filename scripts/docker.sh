#!/bin/bash
# ========================================
# Field Booker — Docker Commands
# ========================================
# Usage: ./scripts/docker.sh [setup|start|stop|logs]

set -e

case "${1:-start}" in
  setup)
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed."; exit 1
    fi
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "⚠️  Created .env — edit it with your credentials, then re-run."
        exit 0
    fi
    docker compose up -d --build
    echo "✅ Setup complete! → http://localhost"
    ;;

  start)
    docker compose up -d --build
    echo "✅ Started! → http://localhost"
    ;;

  stop)
    docker compose down
    echo "✅ Stopped."
    ;;

  logs)
    docker compose logs -f "${2:-}"
    ;;

  *)
    echo "Usage: $0 [setup|start|stop|logs]"
    exit 1
    ;;
esac
