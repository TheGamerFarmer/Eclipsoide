#!/bin/bash
set -e

LOG_FILE="install.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Début de l'installation ==="

# Vérification de Python 3.12
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Vérification de la version Python..."
if ! command -v python3 &> /dev/null; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERREUR : python3 introuvable. Installez Python 3.12."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -ne 3 ] || [ "$PYTHON_MINOR" -ne 12 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERREUR : Python 3.12 requis (détecté : $PYTHON_VERSION)."
    exit 1
fi
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Python $PYTHON_VERSION détecté."

# Vérification du fichier de dépendances
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Vérification de pyproject.toml..."
if [ ! -f "pyproject.toml" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERREUR : pyproject.toml introuvable."
    exit 1
fi
echo "[$(date '+%Y-%m-%d %H:%M:%S')] pyproject.toml trouvé."

# Création de l'environnement virtuel
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Création de l'environnement virtuel (.venv)..."
python3 -m venv .venv
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Environnement virtuel créé."

# Mise à jour de pip
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Mise à jour de pip..."
.venv/bin/pip install --upgrade pip
echo "[$(date '+%Y-%m-%d %H:%M:%S')] pip mis à jour."

# Installation des dépendances depuis pyproject.toml
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installation des dépendances depuis pyproject.toml..."
.venv/bin/pip install -e .
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Dépendances installées avec succès."

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Installation terminée. Lancez ./run.sh pour démarrer le jeu. ==="