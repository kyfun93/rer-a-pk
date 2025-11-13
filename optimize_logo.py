#!/usr/bin/env python3
"""
Script pour nettoyer et optimiser le logo PK-ASSIST
- Supprime le fond damier (transparence)
- Renforce les couleurs neon
- Nettoie les bords
- Exporte en PNG transparent haute résolution
"""

try:
    from PIL import Image, ImageEnhance, ImageFilter
    import numpy as np
except ImportError:
    print("❌ Erreur : Pillow et numpy nécessaires")
    print("   Installation : pip3 install Pillow numpy")
    exit(1)

import sys
import os

def remove_checkerboard_background(img):
    """Supprime le fond damier en détectant les pixels gris/blancs du damier"""
    img_array = np.array(img)
    
    # Convertir en RGBA si nécessaire
    if len(img_array.shape) == 3 and img_array.shape[2] == 3:
        alpha = np.ones((img_array.shape[0], img_array.shape[1]), dtype=np.uint8) * 255
        img_array = np.dstack([img_array, alpha])
    
    # Détecter les pixels du damier (gris clair/foncé alternés)
    r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
    gray = (r.astype(float) + g.astype(float) + b.astype(float)) / 3.0
    
    # Calculer la saturation (différence entre les canaux)
    saturation = np.abs(r.astype(float) - g.astype(float)) + np.abs(g.astype(float) - b.astype(float))
    
    # Les pixels du damier ont une saturation faible et sont gris
    # Le damier alterne entre gris clair (~240) et gris foncé (~200)
    checkerboard_mask = (
        (saturation < 40) &  # Faible saturation (gris)
        ((gray > 180) | (gray < 120))  # Gris clair ou foncé du damier
    )
    
    # Créer un masque alpha : transparent pour le damier, opaque pour le reste
    alpha = img_array[:, :, 3].copy()
    alpha[checkerboard_mask] = 0
    
    # Nettoyer les bords : éroder puis dilater pour lisser
    # Utiliser une méthode simple sans scipy
    alpha_bool = alpha > 128
    # Dilatation simple (voisinage 3x3)
    h, w = alpha.shape
    alpha_dilated = alpha_bool.copy()
    for y in range(1, h-1):
        for x in range(1, w-1):
            if alpha_bool[y, x]:
                alpha_dilated[y-1:y+2, x-1:x+2] = True
    
    alpha = (alpha_dilated.astype(np.uint8) * 255)
    
    img_array[:, :, 3] = alpha
    return Image.fromarray(img_array)

def enhance_neon_colors(img):
    """Renforce les couleurs neon (rose/magenta et cyan/bleu) avec effet de brillance"""
    img_array = np.array(img)
    
    if len(img_array.shape) != 3 or img_array.shape[2] < 3:
        return img
    
    r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
    alpha = img_array[:, :, 3] if img_array.shape[2] == 4 else None
    
    # Masque pour rose/magenta (rouge élevé, bleu moyen-élevé, vert faible)
    pink_mask = (r > 150) & (g < 180) & (b > 100) & (r > g + 30)
    
    # Masque pour cyan/bleu (bleu élevé, vert moyen-élevé, rouge faible)
    cyan_mask = (b > 120) & (g > 100) & (r < 150) & (b > r + 30)
    
    # Renforcer les couleurs dans ces zones avec effet de brillance
    enhanced = img_array.copy()
    
    # Rose/Magenta : augmenter fortement la saturation et l'intensité pour faire briller
    if np.any(pink_mask):
        # Augmenter l'intensité globale
        enhanced[pink_mask, 0] = np.clip(enhanced[pink_mask, 0] * 1.3, 0, 255)  # R - plus fort
        enhanced[pink_mask, 1] = np.clip(enhanced[pink_mask, 1] * 0.7, 0, 255)  # G - réduit
        enhanced[pink_mask, 2] = np.clip(enhanced[pink_mask, 2] * 1.2, 0, 255)  # B - renforcé
        
        # Créer un effet de brillance en augmentant les zones les plus lumineuses
        brightness = (enhanced[pink_mask, 0].astype(float) + enhanced[pink_mask, 1].astype(float) + enhanced[pink_mask, 2].astype(float)) / 3.0
        bright_pink = brightness > 150
        if np.any(bright_pink):
            bright_indices = np.where(pink_mask)
            bright_mask = np.zeros_like(pink_mask)
            bright_mask[bright_indices[0][bright_pink], bright_indices[1][bright_pink]] = True
            enhanced[bright_mask, 0] = np.clip(enhanced[bright_mask, 0] * 1.1, 0, 255)
            enhanced[bright_mask, 2] = np.clip(enhanced[bright_mask, 2] * 1.1, 0, 255)
    
    # Cyan/Bleu : renforcer avec effet de brillance
    if np.any(cyan_mask):
        # Augmenter l'intensité globale
        enhanced[cyan_mask, 0] = np.clip(enhanced[cyan_mask, 0] * 0.6, 0, 255)  # R - réduit
        enhanced[cyan_mask, 1] = np.clip(enhanced[cyan_mask, 1] * 1.2, 0, 255)  # G - renforcé
        enhanced[cyan_mask, 2] = np.clip(enhanced[cyan_mask, 2] * 1.3, 0, 255)  # B - plus fort
        
        # Créer un effet de brillance pour les zones cyan les plus lumineuses
        brightness = (enhanced[cyan_mask, 0].astype(float) + enhanced[cyan_mask, 1].astype(float) + enhanced[cyan_mask, 2].astype(float)) / 3.0
        bright_cyan = brightness > 120
        if np.any(bright_cyan):
            bright_indices = np.where(cyan_mask)
            bright_mask = np.zeros_like(cyan_mask)
            bright_mask[bright_indices[0][bright_cyan], bright_indices[1][bright_cyan]] = True
            enhanced[bright_mask, 1] = np.clip(enhanced[bright_mask, 1] * 1.1, 0, 255)
            enhanced[bright_mask, 2] = np.clip(enhanced[bright_mask, 2] * 1.1, 0, 255)
    
    return Image.fromarray(enhanced)

def clean_edges(img):
    """Nettoie les bords en supprimant les pixels gris résiduels"""
    img_array = np.array(img)
    
    if len(img_array.shape) != 3 or img_array.shape[2] < 4:
        return img
    
    # Trouver les pixels transparents ou presque transparents
    alpha = img_array[:, :, 3]
    transparent_mask = alpha < 15
    
    # Pour les pixels transparents, s'assurer qu'ils sont vraiment transparents
    img_array[transparent_mask, :] = 0
    
    # Nettoyer les bords avec un filtre de netteté léger
    img = Image.fromarray(img_array)
    
    # Appliquer un filtre de netteté
    try:
        sharpened = img.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))
    except:
        sharpened = img
    
    return sharpened

def optimize_logo(input_path, output_path):
    """Fonction principale pour optimiser le logo"""
    print(f"Chargement de l'image : {input_path}")
    
    # Charger l'image
    img = Image.open(input_path).convert('RGBA')
    original_size = img.size
    print(f"Taille originale : {original_size}")
    
    # Étape 1 : Supprimer le fond damier
    print("Suppression du fond damier...")
    img = remove_checkerboard_background(img)
    
    # Étape 2 : Renforcer les couleurs neon
    print("Renforcement des couleurs neon...")
    img = enhance_neon_colors(img)
    
    # Étape 3 : Nettoyer les bords
    print("Nettoyage des bords...")
    img = clean_edges(img)
    
    # Étape 3.5 : Ajouter un effet de glow supplémentaire pour faire briller
    print("Ajout d'effet de brillance...")
    img_array = np.array(img)
    # Créer une version floutée pour l'effet de glow
    img_blurred = img.filter(ImageFilter.GaussianBlur(radius=2))
    blur_array = np.array(img_blurred)
    
    # Combiner l'original avec le flou pour créer un effet de glow
    # Seulement sur les zones non-transparentes
    alpha = img_array[:, :, 3] > 10
    glow_factor = 0.3
    for c in range(3):  # RGB seulement
        img_array[alpha, c] = np.clip(
            img_array[alpha, c].astype(float) * (1 - glow_factor) + 
            blur_array[alpha, c].astype(float) * glow_factor,
            0, 255
        ).astype(np.uint8)
    
    # Étape 3.6 : Ajouter du blanc à l'intérieur des lettres pour meilleure lisibilité
    print("Ajout de blanc à l'intérieur des lettres...")
    # Détecter les zones sombres (probablement le texte)
    # Les lettres sont généralement plus sombres que le fond neon
    r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
    brightness = (r.astype(float) + g.astype(float) + b.astype(float)) / 3.0
    
    # Identifier les zones sombres (lettres) qui ont de l'alpha
    text_mask = (alpha) & (brightness < 100)  # Zones sombres avec transparence
    
    # Ajouter du blanc progressif dans les zones sombres
    white_boost = 0.4  # Intensité du blanc à ajouter
    for c in range(3):  # RGB
        img_array[text_mask, c] = np.clip(
            img_array[text_mask, c].astype(float) * (1 - white_boost) + 
            255 * white_boost,
            0, 255
        ).astype(np.uint8)
    
    # Étape 3.7 : Ajouter des ombres internes dans le dessin
    print("Ajout d'ombres internes...")
    # Créer des ombres internes en assombrissant les bords supérieurs et gauches
    # Utiliser des opérations vectorisées numpy pour la performance
    
    # Créer un masque des zones non-transparentes
    mask = alpha.astype(float)
    h, w = img_array.shape[:2]
    
    # Créer un gradient d'ombre avec numpy vectorisé (beaucoup plus rapide)
    # Distance depuis le bord supérieur et gauche (normalisée)
    y_coords, x_coords = np.mgrid[0:h, 0:w].astype(float)
    dist_top = y_coords / max(h, 1)
    dist_left = x_coords / max(w, 1)
    
    # Combiner pour créer un gradient d'ombre (seulement dans les zones non-transparentes)
    shadow_map = (dist_top * 0.6 + dist_left * 0.4) * 0.4 * (mask > 0.5)
    
    # Appliquer l'ombre interne en assombrissant progressivement (vectorisé)
    shadow_strength = 0.25
    shadow_factor = 1 - shadow_map * shadow_strength
    
    # Appliquer à tous les canaux RGB en une seule opération
    img_array[:, :, :3] = np.clip(
        img_array[:, :, :3].astype(float) * shadow_factor[:, :, np.newaxis],
        0, 255
    ).astype(np.uint8)
    
    img = Image.fromarray(img_array)
    
    # Étape 4 : Redimensionner le logo à une taille optimale pour le web
    # Taille cible : 2000x2000 pixels (haute qualité mais léger)
    original_size = img.size
    target_size = 2000
    if img.width < target_size or img.height < target_size:
        # Si l'image est plus petite, on l'agrandit proportionnellement
        ratio = max(target_size / img.width, target_size / img.height)
        new_width = int(img.width * ratio)
        new_height = int(img.height * ratio)
    else:
        # Si l'image est plus grande, on la réduit à la taille cible
        if img.width > img.height:
            new_width = target_size
            new_height = int(img.height * (target_size / img.width))
        else:
            new_height = target_size
            new_width = int(img.width * (target_size / img.height))
    
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    print(f"Redimensionnement de {original_size} à : {img.size}")
    
    # Étape 5 : Sauvegarder en PNG transparent
    print(f"Sauvegarde vers : {output_path}")
    img.save(output_path, 'PNG', optimize=True)
    
    print(f"✅ Logo optimisé sauvegardé : {output_path}")
    print(f"   Taille finale : {img.size}")
    print(f"   Format : PNG avec transparence")

if __name__ == "__main__":
    input_file = "images/1.png"
    output_file = "images/pk-assist-logo.png"
    
    if not os.path.exists(input_file):
        print(f"❌ Erreur : fichier {input_file} introuvable")
        sys.exit(1)
    
    try:
        optimize_logo(input_file, output_file)
    except Exception as e:
        print(f"❌ Erreur lors de l'optimisation : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

