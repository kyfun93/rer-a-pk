# 🔐 Guide d'authentification GitHub

Ce guide vous explique comment configurer l'authentification GitHub pour pouvoir push/pull sur le repository `kyfun93/rer-a-pk`.

## 🚀 Méthode rapide (script automatique)

Exécutez simplement :
```bash
./setup-github-auth.sh
```

Le script vous guidera à travers le processus.

## 📋 Méthodes d'authentification

### Option 1 : HTTPS avec token d'accès personnel ⭐ (Recommandé pour débutants)

**Avantages** : Simple, fonctionne partout  
**Inconvénients** : Token à gérer manuellement

#### Étapes :

1. **Créer un token GitHub** :
   - Allez sur : https://github.com/settings/tokens
   - Cliquez sur "Generate new token" → "Generate new token (classic)"
   - Donnez un nom (ex: "Cursor - rer-a-pk")
   - Sélectionnez les permissions : **`repo`** (accès complet aux repositories)
   - Cliquez sur "Generate token"
   - **⚠️ COPIEZ LE TOKEN** (vous ne pourrez plus le voir après)

2. **Configurer Git** :
   ```bash
   git config --global credential.helper store
   ```

3. **Premier push** :
   ```bash
   git push origin main
   ```
   - **Username** : `kyfun93`
   - **Password** : collez votre **TOKEN** (pas votre mot de passe GitHub)

4. **Token sauvegardé** :
   Git sauvegardera automatiquement le token pour les prochaines fois.

---

### Option 2 : SSH avec clé ⭐⭐ (Recommandé - Plus sécurisé)

**Avantages** : Plus sécurisé, pas besoin de token  
**Inconvénients** : Configuration initiale un peu plus complexe

#### Étapes :

1. **Vérifier si vous avez déjà une clé SSH** :
   ```bash
   ls -la ~/.ssh/id_*.pub
   ```
   Si vous voyez des fichiers, vous avez déjà une clé.

2. **Générer une nouvelle clé SSH** (si nécessaire) :
   ```bash
   ssh-keygen -t ed25519 -C "votre.email@example.com"
   ```
   - Appuyez sur Entrée pour accepter l'emplacement par défaut
   - Entrez un mot de passe (optionnel mais recommandé)
   - Ou appuyez sur Entrée deux fois pour ne pas mettre de mot de passe

3. **Démarrer l'agent SSH** :
   ```bash
   eval "$(ssh-agent -s)"
   ```

4. **Ajouter la clé à l'agent** :
   ```bash
   ssh-add ~/.ssh/id_ed25519
   ```

5. **Copier la clé publique** :
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   Copiez tout le contenu affiché.

6. **Ajouter la clé sur GitHub** :
   - Allez sur : https://github.com/settings/keys
   - Cliquez sur "New SSH key"
   - Donnez un titre (ex: "MacBook - Cursor")
   - Collez la clé publique dans le champ "Key"
   - Cliquez sur "Add SSH key"

7. **Changer l'URL du remote en SSH** :
   ```bash
   git remote set-url origin git@github.com:kyfun93/rer-a-pk.git
   ```

8. **Tester la connexion** :
   ```bash
   ssh -T git@github.com
   ```
   Vous devriez voir : `Hi kyfun93! You've successfully authenticated...`

9. **Tester avec un push** :
   ```bash
   git push origin main
   ```

---

### Option 3 : GitHub CLI (gh) ⭐⭐⭐ (Le plus simple si installé)

**Avantages** : Très simple, gestion automatique  
**Inconvénients** : Nécessite l'installation de `gh`

#### Étapes :

1. **Installer GitHub CLI** :
   ```bash
   # macOS
   brew install gh
   
   # Ou téléchargez depuis : https://cli.github.com
   ```

2. **S'authentifier** :
   ```bash
   gh auth login
   ```
   Suivez les instructions à l'écran :
   - Choisissez GitHub.com
   - Choisissez HTTPS ou SSH
   - Authentifiez-vous via le navigateur

3. **Vérifier l'authentification** :
   ```bash
   gh auth status
   ```

4. **Tester avec un push** :
   ```bash
   git push origin main
   ```

---

## 🔍 Vérification de l'authentification

### Vérifier le remote
```bash
git remote -v
```

**HTTPS** devrait afficher :
```
origin  https://github.com/kyfun93/rer-a-pk.git (fetch)
origin  https://github.com/kyfun93/rer-a-pk.git (push)
```

**SSH** devrait afficher :
```
origin  git@github.com:kyfun93/rer-a-pk.git (fetch)
origin  git@github.com:kyfun93/rer-a-pk.git (push)
```

### Tester la connexion

**Pour HTTPS** :
```bash
git ls-remote origin
```

**Pour SSH** :
```bash
ssh -T git@github.com
```

**Pour GitHub CLI** :
```bash
gh auth status
```

---

## ⚠️ Résolution de problèmes

### Erreur : "Permission denied (publickey)"

**Problème** : Clé SSH non configurée ou non ajoutée sur GitHub

**Solution** :
1. Vérifiez que votre clé est ajoutée : `ssh-add -l`
2. Vérifiez que la clé est sur GitHub : https://github.com/settings/keys
3. Testez la connexion : `ssh -T git@github.com`

### Erreur : "Authentication failed"

**Problème** : Token invalide ou expiré

**Solution** :
1. Créez un nouveau token : https://github.com/settings/tokens
2. Supprimez l'ancien token sauvegardé :
   ```bash
   # macOS/Linux
   rm ~/.git-credentials
   
   # Ou éditez le fichier et supprimez l'entrée
   ```
3. Réessayez le push

### Erreur : "Repository not found"

**Problème** : Pas d'accès au repository ou URL incorrecte

**Solution** :
1. Vérifiez que le repository existe : https://github.com/kyfun93/rer-a-pk
2. Vérifiez que vous avez les droits d'accès
3. Vérifiez l'URL du remote : `git remote -v`

---

## 📚 Ressources

- **Créer un token** : https://github.com/settings/tokens
- **Gérer les clés SSH** : https://github.com/settings/keys
- **Documentation Git** : https://git-scm.com/doc
- **Documentation GitHub** : https://docs.github.com
- **GitHub CLI** : https://cli.github.com

---

## ✅ Checklist

- [ ] Méthode d'authentification choisie
- [ ] Token créé OU clé SSH générée et ajoutée
- [ ] Remote configuré (HTTPS ou SSH)
- [ ] Connexion testée avec succès
- [ ] Premier push effectué

---

## 🎯 Recommandation

Pour la plupart des utilisateurs, je recommande :
1. **Débutants** : HTTPS avec token (Option 1)
2. **Utilisateurs réguliers** : SSH avec clé (Option 2)
3. **Développeurs avancés** : GitHub CLI (Option 3)

