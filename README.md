# PK Assistant – RER A

Application web pour estimer le point kilométrique (PK) en temps réel à partir de la géolocalisation GPS sur la ligne RER A.

🔗 **Repository GitHub** : [https://github.com/kyfun93/rer-a-pk](https://github.com/kyfun93/rer-a-pk)

## Fonctionnalités

- 📍 Calcul du PK actuel à partir de la position GPS
- 🧭 Détection automatique de la branche (Boissy-Saint-Léger ou Marne-la-Vallée – Chessy)
- 🚉 Recherche de gares et accès les plus proches
- 🎯 Définition d'un PK cible et calcul de la distance
- 📱 SMS d'urgence avec position GPS
- 🔧 Recalage PK manuel
- 📤 Export des calibrations
- 🚨 Signalement d'incidents

## Installation

### Option 1 : Cloner le repository
```bash
git clone https://github.com/kyfun93/rer-a-pk.git
cd rer-a-pk
```

### Option 2 : Télécharger directement
Téléchargez le fichier `index.html` depuis [GitHub](https://github.com/kyfun93/rer-a-pk/blob/main/index.html)

### Utilisation
Ouvrez `index.html` dans votre navigateur web

## Utilisation

1. Saisissez le code d'accès (3615 par défaut)
2. Autorisez la géolocalisation dans votre navigateur
3. Cliquez sur "Démarrer la géoloc"
4. L'application calcule automatiquement votre PK actuel

## Configuration

- **Code d'accès** : Modifiable dans le code (ligne 674)
- **Numéro SOS** : Configurable dans les paramètres
- **Sensibilité au mouvement** : Ajustable (Marche lente / Normal / Train)

## Développement

### Configuration GitHub

Pour travailler sur ce projet avec Git/GitHub, consultez :
- **Guide rapide** : [`QUICK_START.md`](QUICK_START.md)
- **Configuration complète** : [`CONFIGURATION_GITHUB.md`](CONFIGURATION_GITHUB.md)
- **Instructions Cursor** : [`INSTRUCTIONS_CURSOR.md`](INSTRUCTIONS_CURSOR.md)

### Commandes Git utiles

```bash
# Vérifier l'état
git status

# Récupérer les dernières modifications
git pull origin main

# Ajouter et commiter
git add .
git commit -m "Description des modifications"

# Envoyer vers GitHub
git push origin main
```

## Technologies

- HTML5
- CSS3
- JavaScript (vanilla)
- Geolocation API
- LocalStorage

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Ouvrir une [issue](https://github.com/kyfun93/rer-a-pk/issues) pour signaler un bug
- Proposer des améliorations via une [pull request](https://github.com/kyfun93/rer-a-pk/pulls)

## Licence

Usage interne – Accès réservé


