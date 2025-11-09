# ⚡ Configuration rapide de l'authentification GitHub

## 🎯 Méthode la plus rapide : HTTPS avec token

### Étape 1 : Créer un token GitHub (2 minutes)

1. **Ouvrez** : https://github.com/settings/tokens
2. **Cliquez** sur "Generate new token" → "Generate new token (classic)"
3. **Donnez un nom** : `Cursor - rer-a-pk`
4. **Sélectionnez** : `repo` (accès complet aux repositories)
5. **Cliquez** sur "Generate token"
6. **⚠️ COPIEZ LE TOKEN** (vous ne pourrez plus le voir après)

### Étape 2 : Configurer Git (déjà fait ✅)

Le credential helper est déjà configuré.

### Étape 3 : Premier push

```bash
# Ajouter vos fichiers
git add .

# Faire un commit
git commit -m "Mise à jour: corrections et documentation"

# Pousser vers GitHub
git push origin main
```

**Lorsque Git vous demande** :
- **Username** : `kyfun93`
- **Password** : collez votre **TOKEN** (pas votre mot de passe GitHub)

✅ **C'est tout !** Le token sera sauvegardé automatiquement.

---

## 🔑 Alternative : SSH (plus sécurisé)

Si vous préférez SSH, exécutez :

```bash
./setup-github-auth.sh
```

Et choisissez l'option 2 (SSH).

---

## 📋 Vérification

Pour vérifier que tout fonctionne :

```bash
# Vérifier le remote
git remote -v

# Tester la connexion
git ls-remote origin
```

---

## 📖 Documentation complète

Pour plus de détails, consultez :
- **Guide complet** : [`AUTHENTIFICATION_GITHUB.md`](AUTHENTIFICATION_GITHUB.md)
- **Script automatique** : `./setup-github-auth.sh`











