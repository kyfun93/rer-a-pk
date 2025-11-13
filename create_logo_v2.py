#!/usr/bin/env python3
"""
Génère un logo vectoriel carré 1:1 pour PK Assist
Style retrowave doux, couleurs pastel, design simple et lisible
"""

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import numpy as np
except ImportError:
    print("❌ Erreur : Pillow et numpy nécessaires")
    print("   Installation : pip3 install Pillow numpy")
    exit(1)

import math

def create_pk_assist_logo_v2(size=2048):
    """Crée le logo PK Assist version 2"""
    
    # Créer l'image avec fond transparent
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Couleurs pastel
    violet_fonce = (45, 35, 65)  # Violet foncé désaturé
    rose_corail = (255, 180, 180)  # Rose corail clair
    bleu_lavande = (180, 200, 255)  # Bleu lavande clair
    blanc_casse = (240, 240, 250)  # Blanc cassé
    bleu_tres_clair = (200, 220, 255)  # Bleu très clair
    
    # 1. Fond général : violet nuit très doux avec points lumineux
    for y in range(size):
        # Dégradé vertical très subtil
        ratio = y / size
        r = int(violet_fonce[0] * (1 - ratio * 0.1))
        g = int(violet_fonce[1] * (1 - ratio * 0.1))
        b = int(violet_fonce[2] * (1 - ratio * 0.15))
        draw.rectangle([(0, y), (size, y+1)], fill=(r, g, b, 255))
    
    # Petits points lumineux discrets (étoiles)
    np.random.seed(42)
    num_stars = 25
    for _ in range(num_stars):
        x = np.random.randint(0, size)
        y = np.random.randint(0, size)
        brightness = np.random.randint(180, 240)
        radius = np.random.randint(1, 2)
        draw.ellipse([(x-radius, y-radius), (x+radius, y+radius)], 
                    fill=(brightness, brightness, brightness, 100))
    
    # 2. Un seul carré aux coins très arrondis (comme icône d'app)
    margin = size * 0.12  # 12% de marge
    square_size = size - 2 * margin
    corner_radius = square_size * 0.25  # Coins très arrondis (25% du côté)
    
    # Fond du carré (légèrement transparent)
    square_bg = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    square_draw = ImageDraw.Draw(square_bg)
    
    # Fond du carré avec dégradé subtil
    for y in range(int(margin), int(size - margin)):
        r = int(violet_fonce[0] * 0.6)
        g = int(violet_fonce[1] * 0.6)
        b = int(violet_fonce[2] * 0.6)
        square_draw.rectangle(
            [(margin, y), (size - margin, y+1)],
            fill=(r, g, b, 220)
        )
    
    # Masque pour le carré arrondi
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        [(margin, margin), (size - margin, size - margin)],
        radius=int(corner_radius),
        fill=255
    )
    
    # Appliquer le masque
    img.paste(square_bg, (0, 0), mask)
    
    # 3. Contour léger en dégradé pastel rose corail → bleu lavande
    border_width = int(size * 0.012)  # 1.2% de la taille
    
    # Créer le contour avec dégradé vertical (rose en haut, bleu en bas)
    border_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(border_img)
    
    # Dessiner le contour extérieur
    outer_margin = margin - border_width
    
    # Créer un masque pour le contour (carré extérieur moins carré intérieur)
    border_outer_mask = Image.new('L', (size, size), 0)
    border_outer_draw = ImageDraw.Draw(border_outer_mask)
    border_outer_draw.rounded_rectangle(
        [(outer_margin, outer_margin), (size - outer_margin, size - outer_margin)],
        radius=int(corner_radius + border_width),
        fill=255
    )
    
    border_inner_mask = Image.new('L', (size, size), 255)
    border_inner_draw = ImageDraw.Draw(border_inner_mask)
    border_inner_draw.rounded_rectangle(
        [(margin, margin), (size - margin, size - margin)],
        radius=int(corner_radius),
        fill=0
    )
    
    # Combiner les masques pour obtenir uniquement le contour
    border_outer_array = np.array(border_outer_mask)
    border_inner_array = np.array(border_inner_mask)
    border_mask_final = (border_outer_array > 128) & (border_inner_array > 128)
    
    # Remplir le contour avec dégradé vertical
    for y in range(size):
        if outer_margin <= y < size - outer_margin:
            ratio = (y - outer_margin) / (size - 2 * outer_margin)
            r = int(rose_corail[0] * (1 - ratio) + bleu_lavande[0] * ratio)
            g = int(rose_corail[1] * (1 - ratio) + bleu_lavande[1] * ratio)
            b = int(rose_corail[2] * (1 - ratio) + bleu_lavande[2] * ratio)
            
            for x in range(size):
                if border_mask_final[y, x]:
                    border_img.putpixel((x, y), (r, g, b, 200))
    
    img = Image.alpha_composite(img, border_img)
    
    # 4. Rails en perspective au centre (du bas vers le centre)
    center_x = size / 2
    center_y = size / 2
    rail_bottom_y = size - margin - size * 0.2  # 20% depuis le bas
    rail_top_y = center_y - size * 0.05  # Légèrement au-dessus du centre
    
    # Dessiner les rails stylisés
    num_rails = 2  # Deux rails
    rail_spacing = square_size * 0.12
    
    for rail_idx in range(num_rails):
        offset = (rail_idx - 0.5) * rail_spacing
        
        # Point de départ (en bas)
        start_x = center_x + offset
        start_y = rail_bottom_y
        
        # Point d'arrivée (au centre, légèrement vers le haut)
        end_x = center_x + offset * 0.4  # Perspective : se rapprochent
        end_y = rail_top_y
        
        # Dessiner le rail avec dégradé
        rail_width = int(size * 0.018)  # 1.8% de la taille
        
        steps = 60
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
                240
            )
            
            # Dessiner un segment du rail
            draw.ellipse(
                [(x - rail_width/2, y - rail_width/2),
                 (x + rail_width/2, y + rail_width/2)],
                fill=rail_color
            )
        
        # Dessiner quelques traverses simplifiées
        for i in range(0, steps, 10):
            t = i / steps
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            
            # Traverse horizontale
            traverse_width = rail_width * 2.5
            draw.rectangle(
                [(x - traverse_width/2, y - rail_width/3),
                 (x + traverse_width/2, y + rail_width/3)],
                fill=(200, 200, 220, 200)
            )
    
    # 5. Texte "PK Assist" sur une seule ligne, centré
    try:
        font_size_main = int(size * 0.11)
        try:
            font_main = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size_main)
        except:
            try:
                font_main = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size_main)
            except:
                font_main = ImageFont.load_default()
    except:
        font_main = ImageFont.load_default()
    
    text = "PK Assist"
    text_y = size - margin - size * 0.28  # 28% depuis le bas
    
    # Calculer la largeur du texte pour le centrer
    bbox = draw.textbbox((0, 0), text, font=font_main)
    text_width = bbox[2] - bbox[0]
    text_x = (size - text_width) / 2
    
    # Créer une image temporaire pour le texte avec dégradé
    text_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_img)
    
    # Dessiner le texte avec dégradé pastel rose → bleu lavande
    # On dessine caractère par caractère pour le dégradé
    char_widths = []
    for char in text:
        bbox_char = text_draw.textbbox((0, 0), char, font=font_main)
        char_widths.append(bbox_char[2] - bbox_char[0])
    
    current_x = text_x
    for i, char in enumerate(text):
        ratio = i / (len(text) - 1) if len(text) > 1 else 0
        
        # Dégradé rose → bleu
        char_color = (
            int(rose_corail[0] * (1 - ratio) + bleu_lavande[0] * ratio),
            int(rose_corail[1] * (1 - ratio) + bleu_lavande[1] * ratio),
            int(rose_corail[2] * (1 - ratio) + bleu_lavande[2] * ratio),
            255
        )
        
        text_draw.text((current_x, text_y), char, font=font_main, fill=char_color)
        current_x += char_widths[i]
    
    # Ajouter un effet glow très léger
    glow_img = text_img.copy()
    glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=1.5))
    
    # Combiner avec l'image principale
    img = Image.alpha_composite(img, glow_img)
    img = Image.alpha_composite(img, text_img)
    
    # 6. Texte "RER A" (plus petit, centré, blanc cassé ou bleu très clair)
    try:
        font_size_sub = int(size * 0.055)
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
    text_y_sub = text_y + font_size_main + size * 0.015
    
    # Dessiner en bleu très clair
    draw.text((text_x_sub, text_y_sub), text_sub, font=font_sub, fill=(*bleu_tres_clair, 255))
    
    return img

if __name__ == "__main__":
    print("Création du logo PK Assist v2...")
    
    # Créer le logo en haute résolution
    logo = create_pk_assist_logo_v2(2048)
    
    # Sauvegarder
    output_path = "images/pk-assist-logo.png"
    logo.save(output_path, 'PNG', optimize=True)
    
    print(f"✅ Logo créé : {output_path}")
    print(f"   Taille : {logo.size}")
    print(f"   Format : PNG avec transparence")

