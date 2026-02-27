#!/bin/bash
# Script per committare e pushare velocemente le modifiche su GitHub

set -e

REPO_URL="https://github.com/alessandrofolloni/field-booker"

echo "📤 Preparazione commit..."

# Aggiunge tutto
git add .

# Chiede il messaggio o ne usa uno di default
MSG=${1:-"Update: AI Assistant integration, Field Corrections and Address Search UI"}

git commit -m "$MSG"

# Assicura che il remote sia corretto
git remote set-url origin $REPO_URL 2>/dev/null || git remote add origin $REPO_URL

# Push sulla branch principale (main o master)
BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "🚀 Invio modifiche su $BRANCH..."
git push origin $BRANCH

echo "✅ Fatto!"
