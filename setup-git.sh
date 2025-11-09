#!/bin/bash

# Script de configuration Git pour PK Assistant RER A
# Usage: ./setup-git.sh

echo "🚀 Configuration du repository Git pour PK Assistant RER A"
echo ""

# Vérifier si git est installé
if ! command -v git &> /dev/null; then
    echo "❌ Git n'est pas installé. Veuillez installer Git d'abord."
    exit 1
fi

# Initialiser le repo si nécessaire
if [ ! -d ".git" ]; then
    echo "📦 Initialisation du repository Git..."
    git init
    echo "✅ Repository initialisé"
else
    echo "ℹ️  Repository Git déjà initialisé"
fi

# Configurer le remote
echo ""
echo "🔗 Configuration du remote GitHub..."
git remote remove origin 2>/dev/null
git remote add origin https://github.com/kyfun93/rer-a-pk.git
echo "✅ Remote configuré: https://github.com/kyfun93/rer-a-pk.git"

# Vérifier la configuration
echo ""
echo "📋 Configuration actuelle:"
git remote -v

# Ajouter tous les fichiers
echo ""
echo "📝 Ajout des fichiers..."
git add .

# Faire le commit initial
echo ""
echo "💾 Création du commit initial..."
git commit -m "Initial commit: PK Assistant RER A avec corrections des anomalies" 2>/dev/null || echo "ℹ️  Aucun changement à commiter"

# Configurer la branche principale
echo ""
echo "🌿 Configuration de la branche principale..."
git branch -M main 2>/dev/null || echo "ℹ️  Branche main déjà configurée"

echo ""
echo "✅ Configuration terminée!"
echo ""
echo "📤 Pour pousser vers GitHub, exécutez:"
echo "   git push -u origin main"
echo ""
echo "⚠️  Si le repo existe déjà sur GitHub, vous devrez peut-être faire:"
echo "   git pull origin main --allow-unrelated-histories"
echo "   (puis résoudre les conflits si nécessaire)"
echo "   git push -u origin main"












