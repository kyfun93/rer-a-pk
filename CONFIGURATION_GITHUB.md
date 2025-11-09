# Configuration GitHub pour travailler sur rer-a-pk

## ✅ Configuration actuelle

Le repository Git est déjà configuré pour pointer vers :
**https://github.com/kyfun93/rer-a-pk.git**

## 🔐 Authentification GitHub

Pour pouvoir push/pull vers GitHub, vous devez vous authentifier. Voici les options :

### Option 1 : Token d'accès personnel (recommandé)

1. **Créer un token GitHub** :
   - Allez sur https://github.com/settings/tokens
   - Cliquez sur "Generate new token" → "Generate new token (classic)"
   - Donnez un nom (ex: "Cursor - rer-a-pk")
   - Sélectionnez les permissions : `repo` (accès complet aux repositories)
   - Cliquez sur "Generate token"
   - **Copiez le token** (vous ne pourrez plus le voir après)

2. **Configurer Git avec le token** :
   ```bash
   git config --global credential.helper store
   ```
   
   Lors du premier push, Git vous demandera :
   - **Username** : `kyfun93`
   - **Password** : collez votre token (pas votre mot de passe)

### Option 2 : SSH (plus sécurisé)

1. **Générer une clé SSH** (si vous n'en avez pas) :
   ```bash
   ssh-keygen -t ed25519 -C "votre.email@example.com"
   ```
   Appuyez sur Entrée pour accepter l'emplacement par défaut.

2. **Ajouter la clé SSH à l'agent** :
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

3. **Copier la clé publique** :
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   Copiez tout le contenu affiché.

4. **Ajouter la clé sur GitHub** :
   - Allez sur https://github.com/settings/keys
   - Cliquez sur "New SSH key"
   - Donnez un titre (ex: "MacBook - Cursor")
   - Collez la clé publique
   - Cliquez sur "Add SSH key"

5. **Changer l'URL du remote en SSH** :
   ```bash
   git remote set-url origin git@github.com:kyfun93/rer-a-pk.git
   ```

### Option 3 : GitHub CLI (gh)

1. **Installer GitHub CLI** :
   ```bash
   brew install gh
   ```

2. **S'authentifier** :
   ```bash
   gh auth login
   ```
   Suivez les instructions à l'écran.

## 📋 Commandes pour synchroniser avec GitHub

### Vérifier l'état actuel
```bash
git status
git remote -v
```

### Récupérer les dernières modifications de GitHub
```bash
git fetch origin
git pull origin main
```

### Ajouter vos modifications
```bash
# Voir les fichiers modifiés
git status

# Ajouter tous les fichiers
git add .

# Ou ajouter des fichiers spécifiques
git add index.html README.md
```

### Faire un commit
```bash
git commit -m "Description de vos modifications"
```

### Envoyer vers GitHub
```bash
# Premier push (configurer le tracking)
git push -u origin main

# Pushes suivants
git push
```

## 🔄 Workflow recommandé

1. **Avant de commencer à travailler** :
   ```bash
   git pull origin main
   ```

2. **Faire vos modifications** dans Cursor

3. **Vérifier les changements** :
   ```bash
   git status
   git diff
   ```

4. **Ajouter et commiter** :
   ```bash
   git add .
   git commit -m "Description claire de vos modifications"
   ```

5. **Envoyer vers GitHub** :
   ```bash
   git push
   ```

## 🛠️ Utilisation dans Cursor

### Via l'interface graphique

1. **Ouvrir le panneau Git** :
   - Cliquez sur l'icône Git dans la barre latérale (ou `Ctrl+Shift+G` / `Cmd+Shift+G`)

2. **Voir les changements** :
   - Les fichiers modifiés apparaissent avec un `M` (Modified)
   - Les nouveaux fichiers apparaissent avec un `U` (Untracked)

3. **Staging** :
   - Cliquez sur le `+` à côté d'un fichier pour l'ajouter au staging
   - Ou cliquez sur le `+` en haut pour tout ajouter

4. **Commit** :
   - Entrez un message de commit dans la zone de texte
   - Cliquez sur l'icône ✓ pour commiter

5. **Push** :
   - Cliquez sur les `...` en haut du panneau Git
   - Sélectionnez "Push" ou "Push to..."

### Via le terminal intégré

Ouvrez le terminal dans Cursor (`Ctrl+`` ou `Cmd+``) et utilisez les commandes Git normales.

## 🔍 Vérification de la configuration

Pour vérifier que tout est bien configuré :

```bash
# Vérifier le remote
git remote -v
# Devrait afficher :
# origin  https://github.com/kyfun93/rer-a-pk.git (fetch)
# origin  https://github.com/kyfun93/rer-a-pk.git (push)

# Vérifier la branche
git branch
# Devrait afficher : * main

# Vérifier la configuration Git
git config --list | grep -E "(user|remote|branch)"
```

## ⚠️ Résolution de problèmes

### Erreur : "Permission denied"
- Vérifiez que vous êtes authentifié (voir section Authentification ci-dessus)
- Pour HTTPS : utilisez un token d'accès personnel
- Pour SSH : vérifiez que votre clé SSH est ajoutée sur GitHub

### Erreur : "Repository not found"
- Vérifiez que le repository existe : https://github.com/kyfun93/rer-a-pk
- Vérifiez que vous avez les droits d'accès au repository

### Erreur : "Updates were rejected"
- Quelqu'un d'autre a poussé des modifications
- Faites d'abord : `git pull origin main`
- Résolvez les conflits si nécessaire
- Puis : `git push`

### Conflits de merge
Si vous avez des conflits lors d'un pull :
```bash
# Voir les fichiers en conflit
git status

# Éditer les fichiers pour résoudre les conflits
# (cherchez les marqueurs <<<<<<<, =======, >>>>>>>)

# Après résolution, ajoutez les fichiers
git add <fichier-résolu>

# Finalisez le merge
git commit
```

## 📚 Ressources

- **Repository GitHub** : https://github.com/kyfun93/rer-a-pk
- **Documentation Git** : https://git-scm.com/doc
- **Documentation GitHub** : https://docs.github.com
- **GitHub CLI** : https://cli.github.com

## ✅ Checklist de configuration

- [x] Repository Git initialisé
- [x] Remote GitHub configuré
- [x] Branche main configurée
- [ ] Authentification GitHub configurée (à faire)
- [ ] Premier push effectué (à faire)
- [ ] Cursor détecte le repo Git (à vérifier après rechargement)











