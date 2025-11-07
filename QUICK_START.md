# 🚀 Démarrage rapide - GitHub Configuration

## Configuration en 3 étapes

### 1️⃣ Vérifier la configuration Git
```bash
git remote -v
```
✅ Devrait afficher : `origin  https://github.com/kyfun93/rer-a-pk.git`

### 2️⃣ S'authentifier sur GitHub

**Option rapide (HTTPS avec token)** :
1. Créez un token : https://github.com/settings/tokens
2. Sélectionnez `repo` dans les permissions
3. Copiez le token

**Option sécurisée (SSH)** :
```bash
# Générer une clé SSH (si pas déjà fait)
ssh-keygen -t ed25519 -C "votre.email@example.com"

# Copier la clé publique
cat ~/.ssh/id_ed25519.pub

# Ajouter sur GitHub : https://github.com/settings/keys

# Changer l'URL en SSH
git remote set-url origin git@github.com:kyfun93/rer-a-pk.git
```

### 3️⃣ Premier push
```bash
# Ajouter tous les fichiers
git add .

# Faire un commit
git commit -m "Initial commit: PK Assistant RER A avec corrections"

# Récupérer l'historique GitHub (si le repo existe déjà)
git pull origin main --allow-unrelated-histories

# Pousser vers GitHub
git push -u origin main
```

## 🎯 Dans Cursor

1. **Recharger la fenêtre** : `Cmd+Shift+P` → "Reload Window"
2. **Ouvrir le panneau Git** : Cliquez sur l'icône Git dans la barre latérale
3. **Voir les changements** : Les fichiers modifiés apparaissent automatiquement
4. **Commit & Push** : Utilisez l'interface graphique ou le terminal

## 📖 Documentation complète

Voir `CONFIGURATION_GITHUB.md` pour plus de détails.

