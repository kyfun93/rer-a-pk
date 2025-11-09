#!/bin/bash

# Script de configuration de l'authentification GitHub
# Usage: ./setup-github-auth.sh

echo "🔐 Configuration de l'authentification GitHub"
echo "=============================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Vérifier si Git est installé
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git n'est pas installé${NC}"
    exit 1
fi

# Vérifier si on est dans un repo Git
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Ce dossier n'est pas un repository Git${NC}"
    exit 1
fi

echo "Choisissez votre méthode d'authentification :"
echo ""
echo "1) HTTPS avec token d'accès personnel (recommandé pour débutants)"
echo "2) SSH avec clé (plus sécurisé, recommandé)"
echo "3) GitHub CLI (gh) - si installé"
echo ""
read -p "Votre choix (1/2/3) : " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}📝 Configuration HTTPS avec token${NC}"
        echo ""
        echo "Pour créer un token GitHub :"
        echo "1. Allez sur : https://github.com/settings/tokens"
        echo "2. Cliquez sur 'Generate new token' → 'Generate new token (classic)'"
        echo "3. Donnez un nom (ex: 'Cursor - rer-a-pk')"
        echo "4. Sélectionnez la permission : repo (accès complet aux repositories)"
        echo "5. Cliquez sur 'Generate token'"
        echo "6. COPIEZ LE TOKEN (vous ne pourrez plus le voir après)"
        echo ""
        read -p "Appuyez sur Entrée quand vous avez créé le token..."
        
        echo ""
        echo "Configuration du credential helper..."
        git config --global credential.helper store
        
        echo ""
        echo -e "${GREEN}✅ Configuration terminée${NC}"
        echo ""
        echo "Lors de votre premier push, Git vous demandera :"
        echo "  - Username : kyfun93"
        echo "  - Password : collez votre TOKEN (pas votre mot de passe GitHub)"
        echo ""
        echo "Testez avec : git push origin main"
        ;;
        
    2)
        echo ""
        echo -e "${BLUE}🔑 Configuration SSH${NC}"
        echo ""
        
        # Vérifier si une clé SSH existe déjà
        if [ -f ~/.ssh/id_ed25519.pub ] || [ -f ~/.ssh/id_rsa.pub ]; then
            echo -e "${YELLOW}⚠️  Une clé SSH existe déjà${NC}"
            read -p "Voulez-vous en créer une nouvelle ? (o/n) : " new_key
            if [ "$new_key" != "o" ] && [ "$new_key" != "O" ]; then
                USE_EXISTING=true
            fi
        fi
        
        if [ "$USE_EXISTING" != "true" ]; then
            echo "Génération d'une nouvelle clé SSH..."
            read -p "Entrez votre email GitHub : " email
            
            if [ -z "$email" ]; then
                email="kyfun93@users.noreply.github.com"
                echo "Utilisation de l'email par défaut : $email"
            fi
            
            ssh-keygen -t ed25519 -C "$email" -f ~/.ssh/id_ed25519 -N ""
            
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Clé SSH générée${NC}"
            else
                echo -e "${RED}❌ Erreur lors de la génération de la clé${NC}"
                exit 1
            fi
        fi
        
        # Démarrer l'agent SSH
        echo ""
        echo "Démarrage de l'agent SSH..."
        eval "$(ssh-agent -s)"
        
        # Ajouter la clé à l'agent
        if [ -f ~/.ssh/id_ed25519 ]; then
            ssh-add ~/.ssh/id_ed25519
        elif [ -f ~/.ssh/id_rsa ]; then
            ssh-add ~/.ssh/id_rsa
        fi
        
        # Afficher la clé publique
        echo ""
        echo -e "${BLUE}📋 Votre clé publique SSH :${NC}"
        echo "=========================================="
        if [ -f ~/.ssh/id_ed25519.pub ]; then
            cat ~/.ssh/id_ed25519.pub
        elif [ -f ~/.ssh/id_rsa.pub ]; then
            cat ~/.ssh/id_rsa.pub
        fi
        echo "=========================================="
        echo ""
        echo "Pour ajouter cette clé sur GitHub :"
        echo "1. Allez sur : https://github.com/settings/keys"
        echo "2. Cliquez sur 'New SSH key'"
        echo "3. Donnez un titre (ex: 'MacBook - Cursor')"
        echo "4. Collez la clé ci-dessus dans le champ 'Key'"
        echo "5. Cliquez sur 'Add SSH key'"
        echo ""
        read -p "Appuyez sur Entrée quand vous avez ajouté la clé sur GitHub..."
        
        # Changer l'URL du remote en SSH
        echo ""
        echo "Changement de l'URL du remote en SSH..."
        git remote set-url origin git@github.com:kyfun93/rer-a-pk.git
        
        # Tester la connexion
        echo ""
        echo "Test de la connexion SSH..."
        ssh -T git@github.com 2>&1 | head -1
        
        echo ""
        echo -e "${GREEN}✅ Configuration SSH terminée${NC}"
        echo ""
        echo "Testez avec : git push origin main"
        ;;
        
    3)
        echo ""
        echo -e "${BLUE}🛠️  Configuration GitHub CLI${NC}"
        echo ""
        
        # Vérifier si gh est installé
        if ! command -v gh &> /dev/null; then
            echo -e "${YELLOW}⚠️  GitHub CLI (gh) n'est pas installé${NC}"
            echo ""
            echo "Pour installer sur macOS :"
            echo "  brew install gh"
            echo ""
            echo "Ou téléchargez depuis : https://cli.github.com"
            exit 1
        fi
        
        echo "Authentification avec GitHub CLI..."
        gh auth login
        
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}✅ Authentification réussie${NC}"
            echo ""
            echo "Testez avec : git push origin main"
        else
            echo -e "${RED}❌ Erreur lors de l'authentification${NC}"
            exit 1
        fi
        ;;
        
    *)
        echo -e "${RED}❌ Choix invalide${NC}"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Configuration terminée !${NC}"
echo ""
echo "Vérifiez la configuration avec :"
echo "  git remote -v"
echo ""
echo "Testez la connexion avec :"
echo "  git push origin main"
echo ""











