#!/usr/bin/env python3
"""
Génère un logo vectoriel carré 1:1 pour PK Assist
Style retrowave doux, couleurs pastel
"""

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import numpy as np
except ImportError:
    print("❌ Erreur : Pillow et numpy nécessaires")
    print("   Installation : pip3 install Pillow numpy")
    exit(1)

import math

def create_pk_assist_logo(size=1024):
    """Crée le logo PK Assist"""
    
    # Créer l'image avec fond transparent
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Couleurs pastel
    violet_fonce = (45, 35, 65)  # Violet foncé désaturé
    rose_corail = (255, 180, 180)  # Rose corail clair
    bleu_lavande = (180, 200, 255)  # Bleu lavande clair
    blanc_casse = (240, 240, 250)  # Blanc cassé
    bleu_tres_clair = (200, 220, 255)  # Bleu très clair
    
    # 1. Fond : dégradé nuit très doux violet foncé
    for y in range(size):
        # Dégradé vertical très subtil
        ratio = y / size
        r = int(violet_fonce[0] * (1 - ratio * 0.1))
        g = int(violet_fonce[1] * (1 - ratio * 0.1))
        b = int(violet_fonce[2] * (1 - ratio * 0.15))
        draw.rectangle([(0, y), (size, y+1)], fill=(r, g, b, 255))
    
    # 2. Petits points lumineux discrets (étoiles)
    np.random.seed(42)  # Pour la reproductibilité
    num_stars = 30
    for _ in range(num_stars):
        x = np.random.randint(0, size)
        y = np.random.randint(0, size)
        brightness = np.random.randint(180, 255)
        radius = np.random.randint(1, 2)
        draw.ellipse([(x-radius, y-radius), (x+radius, y+radius)], 
                    fill=(brightness, brightness, brightness, 120))
    
    # 3. Icône principale : grand carré aux coins très arrondis
    margin = size * 0.15  # 15% de marge
    square_size = size - 2 * margin
    corner_radius = square_size * 0.2  # Coins très arrondis (20% du côté)
    
    # Créer un masque pour le carré arrondi
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        [(margin, margin), (size - margin, size - margin)],
        radius=int(corner_radius),
        fill=255
    )
    
    # Fond du carré (légèrement transparent pour laisser voir le fond)
    square_bg = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    square_draw = ImageDraw.Draw(square_bg)
    
    # Dégradé pour le fond du carré (très subtil)
    for y in range(int(margin), int(size - margin)):
        ratio = (y - margin) / square_size
        r = int(violet_fonce[0] * 0.7)
        g = int(violet_fonce[1] * 0.7)
        b = int(violet_fonce[2] * 0.7)
        square_draw.rectangle(
            [(margin, y), (size - margin, y+1)],
            fill=(r, g, b, 200)
        )
    
    # Appliquer le masque
    img.paste(square_bg, (0, 0), mask)
    
    # 4. Contour léger en dégradé pastel rose corail → bleu lavande
    border_width = int(size * 0.015)  # 1.5% de la taille
    
    # Créer une image pour le contour avec dégradé
    border_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(border_img)
    
    # Dessiner le contour extérieur avec dégradé vertical (rose en haut, bleu en bas)
    outer_margin = margin - border_width
    for y in range(int(outer_margin), int(size - outer_margin)):
        ratio = (y - outer_margin) / (size - 2 * outer_margin)
        r = int(rose_corail[0] * (1 - ratio) + bleu_lavande[0] * ratio)
        g = int(rose_corail[1] * (1 - ratio) + bleu_lavande[1] * ratio)
        b = int(rose_corail[2] * (1 - ratio) + bleu_lavande[2] * ratio)
        color = (r, g, b, 180)
        
        # Bord gauche
        border_draw.rounded_rectangle(
            [(outer_margin, y), (margin, y+1)],
            radius=0,
            fill=color
        )
        # Bord droit
        border_draw.rounded_rectangle(
            [(size - margin, y), (size - outer_margin, y+1)],
            radius=0,
            fill=color
        )
    
    # Bords haut et bas
    for x in range(int(outer_margin), int(size - outer_margin)):
        ratio = (x - outer_margin) / (size - 2 * outer_margin)
        r = int(rose_corail[0] * (1 - ratio * 0.5) + bleu_lavande[0] * ratio * 0.5)
        g = int(rose_corail[1] * (1 - ratio * 0.5) + bleu_lavande[1] * ratio * 0.5)
        b = int(rose_corail[2] * (1 - ratio * 0.5) + bleu_lavande[2] * ratio * 0.5)
        color = (r, g, b, 180)
        
        # Bord haut
        border_draw.rounded_rectangle(
            [(x, outer_margin), (x+1, margin)],
            radius=0,
            fill=color
        )
        # Bord bas
        border_draw.rounded_rectangle(
            [(x, size - margin), (x+1, size - outer_margin)],
            radius=0,
            fill=color
        )
    
    # Appliquer le contour avec coins arrondis
    border_mask = Image.new('L', (size, size), 0)
    border_mask_draw = ImageDraw.Draw(border_mask)
    border_mask_draw.rounded_rectangle(
        [(outer_margin, outer_margin), (size - outer_margin, size - outer_margin)],
        radius=int(corner_radius + border_width),
        fill=255
    )
    # Soustraire le carré intérieur
    inner_mask = Image.new('L', (size, size), 255)
    inner_mask_draw = ImageDraw.Draw(inner_mask)
    inner_mask_draw.rounded_rectangle(
        [(margin, margin), (size - margin, size - margin)],
        radius=int(corner_radius),
        fill=0
    )
    
    # Combiner les masques
    border_mask_array = np.array(border_mask)
    inner_mask_array = np.array(inner_mask)
    final_border_mask = (border_mask_array > 128) & (inner_mask_array > 128)
    
    # Appliquer le contour
    border_array = np.array(border_img)
    border_array[~final_border_mask] = [0, 0, 0, 0]
    border_img = Image.fromarray(border_array)
    
    img = Image.alpha_composite(img, border_img)
    
    # 5. Rails stylisés en perspective (du bas vers le centre)
    center_x = size / 2
    center_y = size / 2
    rail_bottom_y = size - margin - size * 0.15  # 15% depuis le bas
    
    # Dessiner les rails en perspective
    num_rails = 3
    rail_spacing = square_size * 0.08
    
    for rail_idx in range(num_rails):
        offset = (rail_idx - num_rails // 2) * rail_spacing
        
        # Point de départ (en bas)
        start_x = center_x + offset
        start_y = rail_bottom_y
        
        # Point d'arrivée (au centre, légèrement vers le haut)
        end_x = center_x + offset * 0.3
        end_y = center_y - size * 0.1
        
        # Dessiner le rail avec dégradé
        rail_width = int(size * 0.015)  # 1.5% de la taille
        
        # Créer un dégradé pour le rail
        steps = 50
        for i in range(steps):
            t = i / steps
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            
            # Dégradé rose → bleu selon la position
            color_ratio = t
            rail_color = (
                int(rose_corail[0] * (1 - color_ratio) + bleu_lavande[0] * color_ratio),
                int(rose_corail[1] * (1 - color_ratio) + bleu_lavande[1] * color_ratio),
                int(rose_corail[2] * (1 - color_ratio) + bleu_lavande[2] * color_ratio),
                220
            )
            
            # Dessiner un segment du rail
            draw.ellipse(
                [(x - rail_width/2, y - rail_width/2),
                 (x + rail_width/2, y + rail_width/2)],
                fill=rail_color
            )
        
        # Dessiner les traverses (simplifiées)
        for i in range(0, steps, 8):
            t = i / steps
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            
            # Traverse horizontale
            traverse_width = rail_width * 2
            draw.rectangle(
                [(x - traverse_width/2, y - rail_width/4),
                 (x + traverse_width/2, y + rail_width/4)],
                fill=(200, 200, 220, 180)
            )
    
    # 6. Texte "PK Assist"
    try:
        # Essayer de charger une police sans sérif arrondie
        font_size_main = int(size * 0.12)
        try:
            font_main = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size_main)
        except:
            try:
                font_main = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size_main)
            except:
                font_main = ImageFont.load_default()
    except:
        font_main = ImageFont.load_default()
    
    text = "PK ASSIST"
    text_y = size - margin - size * 0.25  # 25% depuis le bas
    
    # Calculer la largeur du texte pour le centrer
    bbox = draw.textbbox((0, 0), text, font=font_main)
    text_width = bbox[2] - bbox[0]
    text_x = (size - text_width) / 2
    
    # Dessiner le texte avec dégradé pastel rose → bleu lavande
    # Créer une image temporaire pour le texte avec dégradé
    text_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_img)
    
    # Dessiner le texte plusieurs fois avec différentes couleurs pour créer un dégradé
    for i, char in enumerate(text):
        char_x = text_x + i * (text_width / len(text))
        ratio = i / (len(text) - 1) if len(text) > 1 else 0
        
        # Dégradé rose → bleu
        char_color = (
            int(rose_corail[0] * (1 - ratio) + bleu_lavande[0] * ratio),
            int(rose_corail[1] * (1 - ratio) + bleu_lavande[1] * ratio),
            int(rose_corail[2] * (1 - ratio) + bleu_lavande[2] * ratio),
            255
        )
        
        text_draw.text((char_x, text_y), char, font=font_main, fill=char_color)
    
    # Ajouter un effet glow très léger
    glow_img = text_img.copy()
    glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=2))
    
    # Combiner avec l'image principale
    img = Image.alpha_composite(img, glow_img)
    img = Image.alpha_composite(img, text_img)
    
    # 7. Texte "RER A" (plus petit, centré, blanc cassé ou bleu très clair)
    try:
        font_size_sub = int(size * 0.06)
        try:
            font_sub = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size_sub)
        except:
            try:
                font_sub = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size_sub)
            except:
                font_sub = ImageFont.load_default()
    except:
        font_sub = ImageFont.load_default()
    
    text_sub = "RER A"
    bbox_sub = draw.textbbox((0, 0), text_sub, font=font_sub)
    text_width_sub = bbox_sub[2] - bbox_sub[0]
    text_x_sub = (size - text_width_sub) / 2
    text_y_sub = text_y + font_size_main + size * 0.02
    
    # Dessiner en bleu très clair
    draw.text((text_x_sub, text_y_sub), text_sub, font=font_sub, fill=(*bleu_tres_clair, 255))
    
    return img

if __name__ == "__main__":
    print("Création du logo PK Assist...")
    
    # Créer le logo en haute résolution
    logo = create_pk_assist_logo(2048)
    
    # Sauvegarder
    output_path = "images/pk-assist-logo.png"
    logo.save(output_path, 'PNG', optimize=True)
    
    print(f"✅ Logo créé : {output_path}")
    print(f"   Taille : {logo.size}")
    print(f"   Format : PNG avec transparence")

