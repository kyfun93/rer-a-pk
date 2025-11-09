# Configuration Git pour ce projet

## Commandes à exécuter dans le terminal

Ouvrez un terminal dans ce dossier et exécutez les commandes suivantes :

### 1. Initialiser le repository Git (si pas déjà fait)
```bash
git init
```

### 2. Configurer le remote GitHub
```bash
git remote add origin https://github.com/kyfun93/rer-a-pk.git
```

### 3. Vérifier la configuration
```bash
git remote -v
```

Vous devriez voir :
```
origin  https://github.com/kyfun93/rer-a-pk.git (fetch)
origin  https://github.com/kyfun93/rer-a-pk.git (push)
```

### 4. Ajouter tous les fichiers
```bash
git add .
```

### 5. Faire le commit initial
```bash
git commit -m "Initial commit: PK Assistant RER A"
```

### 6. Configurer la branche principale
```bash
git branch -M main
```

### 7. Pousser vers GitHub
```bash
git push -u origin main
```

## Si le repo GitHub existe déjà

Si le repository `kyfun93/rer-a-pk` existe déjà sur GitHub, vous pouvez :

### Option 1 : Pull d'abord (recommandé)
```bash
git pull origin main --allow-unrelated-histories
```

Puis résolvez les conflits si nécessaire, puis :
```bash
git push -u origin main
```

### Option 2 : Force push (attention, écrase l'historique distant)
```bash
git push -u origin main --force
```

## Configuration dans Cursor

Une fois le repo configuré, Cursor devrait automatiquement détecter le repository Git. Vous pourrez :

- Voir les changements dans l'interface
- Faire des commits directement depuis Cursor
- Push/pull depuis l'interface

## Commandes utiles

### Voir l'état
```bash
git status
```

### Voir les remotes
```bash
git remote -v
```

### Changer l'URL du remote
```bash
git remote set-url origin https://github.com/kyfun93/rer-a-pk.git
```












