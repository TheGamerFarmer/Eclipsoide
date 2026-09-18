#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Lancement du jeu ==="

# Vérification de l'environnement virtuel
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Vérification de l'environnement virtuel..."
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERREUR : environnement virtuel introuvable. Lancez d'abord ./install.sh"
    exit 1
fi
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Environnement virtuel détecté."

# Vérification du point d'entrée
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Vérification de Eclipsoide/main.py..."
if [ ! -f "$SCRIPT_DIR/Eclipsoide/main.py" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERREUR : Eclipsoide/main.py introuvable."
    exit 1
fi
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Eclipsoide/main.py trouvé."

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Démarrage de Eclipsoide..."

cd "$SCRIPT_DIR/Eclipsoide"

PYTHONPATH="$SCRIPT_DIR:$SCRIPT_DIR/Eclipsoide${PYTHONPATH:+:$PYTHONPATH}" \
"$SCRIPT_DIR/.venv/bin/python" main.py

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Jeu terminé. ==="
