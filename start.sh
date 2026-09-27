#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "======================================"
echo "  Annuaire des Artisans"
echo "======================================"

# Trouver l'environnement virtuel
if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
    VENV="$PROJECT_DIR/venv/bin/activate"
elif [ -f "$PROJECT_DIR/backend/venv/bin/activate" ]; then
    VENV="$PROJECT_DIR/backend/venv/bin/activate"
else
    echo "❌ Environnement virtuel introuvable."
    exit 1
fi

echo "🐍 Activation de l'environnement virtuel..."
source "$VENV"

cleanup() {
    echo ""
    echo "🛑 Arrêt des serveurs..."
    kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo "🚀 Démarrage du backend Django..."
cd "$PROJECT_DIR/backend"
python3 manage.py runserver &
BACKEND_PID=$!

echo "⚛️  Démarrage du frontend React..."
cd "$PROJECT_DIR/frontend"
npm start &
FRONTEND_PID=$!

echo ""
echo "✅ Backend  : http://127.0.0.1:8000"
echo "✅ Frontend : http://localhost:3000"
echo ""
echo "Appuie sur Ctrl+C pour tout arrêter."
echo ""

wait
