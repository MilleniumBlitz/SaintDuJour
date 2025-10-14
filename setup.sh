#!/bin/bash

# Si le dossier venv n'existe pas, on le crée
if [ ! -d "venv" ]; then
    echo "🪄 Création de l'environnement virtuel..."
    python -m venv venv
fi

echo "🚀 Activation de l'environnement..."
source venv/Scripts/activate

echo "📦 Installation des dépendances..."
pip install -r requirements.txt

echo "✅ Installation terminée."