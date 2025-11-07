#!/bin/bash

# Script de vérification de la configuration Git/GitHub
# Usage: ./check-git-config.sh

echo "🔍 Vérification de la configuration Git/GitHub"
echo "=============================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier si Git est installé
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git n'est pas installé${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Git est installé${NC}"
fi

# Vérifier si on est dans un repo Git
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Ce dossier n'est pas un repository Git${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Repository Git détecté${NC}"
fi

# Vérifier le remote
echo ""
echo "📡 Configuration du remote :"
if git remote -v | grep -q "kyfun93/rer-a-pk"; then
    echo -e "${GREEN}✅ Remote GitHub configuré${NC}"
    git remote -v
else
    echo -e "${RED}❌ Remote GitHub non configuré${NC}"
    echo "   Exécutez : git remote add origin https://github.com/kyfun93/rer-a-pk.git"
fi

# Vérifier la branche
echo ""
echo "🌿 Branche actuelle :"
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
if [ -n "$CURRENT_BRANCH" ]; then
    echo -e "${GREEN}✅ Branche : $CURRENT_BRANCH${NC}"
else
    echo -e "${YELLOW}⚠️  Branche non détectée${NC}"
fi

# Vérifier l'état
echo ""
echo "📊 État du repository :"
git status --short 2>/dev/null | head -10
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ État vérifié${NC}"
else
    echo -e "${YELLOW}⚠️  Impossible de vérifier l'état${NC}"
fi

# Vérifier la connexion GitHub
echo ""
echo "🌐 Test de connexion à GitHub :"
if git ls-remote --heads origin main &>/dev/null; then
    echo -e "${GREEN}✅ Connexion à GitHub réussie${NC}"
else
    echo -e "${YELLOW}⚠️  Impossible de se connecter à GitHub${NC}"
    echo "   Vérifiez votre authentification (token SSH ou HTTPS)"
fi

# Résumé
echo ""
echo "=============================================="
echo "📋 Résumé :"
echo ""
echo "Repository : https://github.com/kyfun93/rer-a-pk"
echo "Branche    : $CURRENT_BRANCH"
echo ""
echo "Pour plus d'informations, consultez :"
echo "  - QUICK_START.md"
echo "  - CONFIGURATION_GITHUB.md"
echo ""

