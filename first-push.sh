#!/bin/bash

# Script pour faire le premier push vers GitHub
# Usage: ./first-push.sh

echo "🚀 Premier push vers GitHub"
echo "============================"
echo ""

# Vérifier si on est dans un repo Git
if [ ! -d ".git" ]; then
    echo "❌ Ce dossier n'est pas un repository Git"
    exit 1
fi

# Vérifier le remote
if ! git remote -v | grep -q "kyfun93/rer-a-pk"; then
    echo "❌ Remote GitHub non configuré"
    exit 1
fi

echo "✅ Remote GitHub configuré"
echo ""

# Vérifier s'il y a des changements à commiter
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Fichiers modifiés détectés"
    read -p "Voulez-vous les ajouter et commiter ? (o/n) : " add_files
    
    if [ "$add_files" = "o" ] || [ "$add_files" = "O" ]; then
        git add .
        read -p "Message de commit (ou Entrée pour message par défaut) : " commit_msg
        if [ -z "$commit_msg" ]; then
            commit_msg="Mise à jour: modifications locales"
        fi
        git commit -m "$commit_msg"
        echo "✅ Fichiers committés"
    fi
fi

# Vérifier s'il y a des commits à pousser
if ! git log origin/main..HEAD --oneline 2>/dev/null | grep -q .; then
    echo "ℹ️  Aucun nouveau commit à pousser"
    echo "   (Tous les commits locaux sont déjà sur GitHub)"
    exit 0
fi

echo ""
echo "📤 Prêt à pousser vers GitHub"
echo ""
echo "⚠️  IMPORTANT : Lorsque Git vous demande :"
echo "   - Username : kyfun93"
echo "   - Password : Collez votre TOKEN GitHub (pas votre mot de passe)"
echo ""
read -p "Appuyez sur Entrée pour continuer..."

# Faire le push
echo ""
echo "🔄 Push en cours..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Push réussi !"
    echo ""
    echo "🎉 Votre code est maintenant sur GitHub :"
    echo "   https://github.com/kyfun93/rer-a-pk"
else
    echo ""
    echo "❌ Erreur lors du push"
    echo ""
    echo "Vérifiez :"
    echo "1. Que vous avez créé un token GitHub"
    echo "2. Que vous avez utilisé le token (pas votre mot de passe)"
    echo "3. Que vous avez les droits d'accès au repository"
    echo ""
    echo "Pour créer un token : https://github.com/settings/tokens"
fi

