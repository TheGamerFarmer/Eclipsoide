#!/bin/bash

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Début du nettoyage ==="

# Suppression de l'environnement virtuel
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Suppression de l'environnement virtuel (.venv)..."
if [ -d ".venv" ]; then
    rm -rf .venv
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] .venv supprimé."
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] .venv absent, ignoré."
fi

# Suppression des artefacts de build
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Suppression des artefacts de build (build/, dist/, *.egg-info)..."
rm -rf build dist
for dir in *.egg-info; do
    if [ -d "$dir" ]; then
        rm -rf "$dir"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Supprimé : $dir"
    fi
done
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Artefacts de build supprimés."

# Suppression des répertoires __pycache__
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Recherche et suppression des répertoires __pycache__..."
PYCACHE_COUNT=$(find . -type d -name "__pycache__" | wc -l)
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo "[$(date '+%Y-%m-%d %H:%M:%S')] $PYCACHE_COUNT répertoire(s) __pycache__ supprimé(s)."

# Suppression des fichiers .pyc
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Recherche et suppression des fichiers .pyc..."
PYC_COUNT=$(find . -type f -name "*.pyc" | wc -l)
find . -type f -name "*.pyc" -delete
echo "[$(date '+%Y-%m-%d %H:%M:%S')] $PYC_COUNT fichier(s) .pyc supprimé(s)."


echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Nettoyage terminé. ==="