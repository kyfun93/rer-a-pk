# Changelog - PK Assistant RER A

## Modifications récentes

### Améliorations du système de calibrage et précision PK

#### 1. **Système d'interpolation amélioré**
- **Rayon de recherche augmenté** :
  - AccessPoints : 500m → 1000m
  - Points de calibration : 1000m → 3000m
- **Poids des points de calibration** : 1.5 → 2.0 (jusqu'à 2.5 selon l'accuracy GPS)
- **Nombre de points utilisés** : 5 → 10 points
- **Fonction de poids** : Utilisation d'une fonction exponentielle pour favoriser les points proches
- **Interpolation activée** même avec un seul point proche (au lieu de 2)

#### 2. **Combinaison projection/interpolation améliorée**
- < 50m : Interpolation à 100%
- < 200m : Interpolation à 70%
- < 500m : Interpolation à 50-60%
- < 1000m : Interpolation à 30%
- < 2000m : Interpolation à 15%

#### 3. **Système de cache pour les polylignes calibrées**
- Cache de 5 secondes pour éviter de reconstruire les polylignes à chaque calcul
- Reconstruction automatique lors d'un nouveau recalage
- Améliore les performances, surtout avec beaucoup de points de calibration

#### 4. **Poids dynamique selon l'accuracy GPS**
- Les points de calibration avec une meilleure précision GPS ont un poids plus élevé :
  - Accuracy < 10m : poids 2.5
  - Accuracy < 20m : poids 2.2
  - Accuracy < 50m : poids 2.0
  - Accuracy ≥ 50m : poids 1.8

#### 5. **Vérification de l'enregistrement des recalages**
- Confirmation visuelle après chaque recalage
- Vérification automatique dans le localStorage
- Affichage du nombre total de recalages enregistrés

### Mode "Couvreur cheminant seul"

#### Fonctionnalités
- **Surveillance du mouvement** : Détection de l'absence de mouvement (seuil de 3 mètres)
- **Timer** : 10 minutes d'immobilité avant déclenchement
- **Vérification** : Toutes les 30 secondes et à chaque mise à jour GPS
- **Envoi automatique du SMS** : Ouvre automatiquement l'application SMS avec le message pré-rempli après 10 minutes sans mouvement
- **Timer SMS** : Mesure le temps qu'il faut pour envoyer le SMS
- **Sonnerie forte** : Se déclenche automatiquement après 30 secondes si le SMS n'est pas envoyé
- **Vibration** : Vibration continue sur mobile si disponible
- **Affichage du temps** : Affiche le temps total qu'il a fallu pour envoyer le SMS et garde l'information affichée

### Améliorations de l'interface

#### 1. **Réorganisation des paramètres**
- Section "Signalement d'avarie" remontée en haut des paramètres
- Section "Numéro SOS" déplacée en bas des paramètres
- Bouton "Générer le message de signalement" changé en vert pastel (`btn-good`)

#### 2. **Suppression des couleurs rouges**
- Fond rouge de la section "Signalement d'avarie" supprimé
- Bordure rouge supprimée
- Ombre rouge supprimée
- Utilisation d'un fond transparent et d'une bordure standard

#### 3. **Améliorations visuelles**
- Cartes transparentes pour voir les étoiles en arrière-plan
- Texte gris éclairci pour meilleure lisibilité
- Changement "Orientation" → "Plan" dans les textes visibles

### Corrections de bugs

#### 1. **Système de calibrage**
- Vérification que les recalages sont bien enregistrés dans le localStorage
- Affichage du nombre de recalages enregistrés
- Reconstruction automatique des polylignes lors d'un nouveau recalage

#### 2. **Système d'interpolation**
- Correction de l'utilisation des points de calibration
- Amélioration de la combinaison entre projection et interpolation
- Gestion des zones éloignées des points de référence

## Notes techniques

### Variables importantes
- `COUVREUR_NO_MOVEMENT_THRESHOLD = 3` : Seuil de mouvement (mètres)
- `COUVREUR_ALERT_DELAY = 10 * 60 * 1000` : Délai avant alerte (10 minutes)
- `SMS_TIMER_DELAY = 30 * 1000` : Délai avant sonnerie (30 secondes)
- `ALARM_FREQUENCY = 800` : Fréquence de la sonnerie (Hz)

### Fichiers modifiés
- `index.html` : Toutes les modifications

### Compatibilité
- Compatible avec tous les navigateurs modernes
- Utilise l'API Web Audio pour la sonnerie
- Utilise l'API Vibration pour mobile (si disponible)

