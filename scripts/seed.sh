#!/bin/bash
# ========================================
# Field Booker — Seed Script
# ========================================
# Populates the database with initial sports data

set -e

echo "🌱 Seeding database with initial data..."

# Wait for services to be ready
echo "⏳ Waiting for Fields service..."
until curl -s http://localhost/api/fields/health > /dev/null 2>&1; do
    sleep 2
done

echo "✅ Fields service is ready!"

# Seed sports
echo "⚽ Adding sports..."

declare -A SPORTS
SPORTS["Calcio"]='{"name":"Calcio","icon":"⚽","color":"#4CAF50"}'
SPORTS["Tennis"]='{"name":"Tennis","icon":"🎾","color":"#FFC107"}'
SPORTS["Basket"]='{"name":"Basket","icon":"🏀","color":"#FF5722"}'
SPORTS["Padel"]='{"name":"Padel","icon":"🏸","color":"#2196F3"}'
SPORTS["Pallavolo"]='{"name":"Pallavolo","icon":"🏐","color":"#9C27B0"}'

for sport in "${!SPORTS[@]}"; do
    echo "  Adding $sport..."
    curl -s -X POST http://localhost/api/fields/sports/ \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
        -d "${SPORTS[$sport]}" > /dev/null 2>&1 || echo "  ⚠️  $sport may already exist or requires admin token"
done

echo ""
echo "✅ Seeding complete!"
echo "ℹ️  Note: You need a valid admin JWT token to seed sports."
echo "   Login as admin first, then replace YOUR_ADMIN_TOKEN in this script."
