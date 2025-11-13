#!/usr/bin/env python3
"""
Génère un logo vectoriel carré 1:1 pour PK ASSIST
Style retrowave doux, couleurs pastel, design simple et lisible
Rails OBLIGATOIRES dans la moitié supérieure
"""

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import numpy as np
except ImportError:
    print("❌ Erreur : Pillow et numpy nécessaires")
    print("   Installation : pip3 install Pillow numpy")
    exit(1)

import math

def create_pk_assist_logo_v3(size=2048):
    """Crée le logo PK ASSIST version 3"""
    
    # Créer l'image avec fond transparent
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Couleurs pastel
    violet_fonce = (45, 35, 65)  # Violet foncé désaturé
    rose_corail = (255, 180, 180)  # Rose corail clair
    bleu_lavande = (180, 200, 255)  # Bleu lavande clair
    blanc_casse = (240, 240, 250)  # Blanc cassé
    bleu_tres_clair = (200, 220, 255)  # Bleu très clair
    
    # 1. Un seul carré aux coins très arrondis
    margin = size * 0.1  # 10% de marge
    square_size = size - 2 * margin
    corner_radius = square_size * 0.25  # Coins très arrondis (25% du côté)
    
    # Intérieur du carré en violet nuit légèrement désaturé
    square_bg = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    square_draw = ImageDraw.Draw(square_bg)
    
    # Fond uniforme violet nuit
    square_draw.rounded_rectangle(
        [(margin, margin), (size - margin, size - margin)],
        radius=int(corner_radius),
        fill=(*violet_fonce, 255)
    )
    
    # Masque pour le carré arrondi
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        [(margin, margin), (size - margin, size - margin)],
        radius=int(corner_radius),
        fill=255
    )
    
    # Appliquer le fond
    img.paste(square_bg, (0, 0), mask)
    
    # 2. Contour du carré en dégradé pastel (rose corail → bleu lavande)
    border_width = int(size * 0.015)  # 1.5% de la taille
    
    # Créer le contour avec dégradé vertical
    border_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(border_img)
    
    outer_margin = margin - border_width
    
    # Masque pour le contour (carré extérieur moins carré intérieur)
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
    
    # Combiner les masques
    border_outer_array = np.array(border_outer_mask)
    border_inner_array = np.array(border_inner_mask)
    border_mask_final = (border_outer_array > 128) & (border_inner_array > 128)
    
    # Remplir le contour avec dégradé vertical (rose en haut, bleu en bas)
    for y in range(size):
        if outer_margin <= y < size - outer_margin:
            ratio = (y - outer_margin) / (size - 2 * outer_margin)
            r = int(rose_corail[0] * (1 - ratio) + bleu_lavande[0] * ratio)
            g = int(rose_corail[1] * (1 - ratio) + bleu_lavande[1] * ratio)
            b = int(rose_corail[2] * (1 - ratio) + bleu_lavande[2] * ratio)
            
            for x in range(size):
                if border_mask_final[y, x]:
                    border_img.putpixel((x, y), (r, g, b, 220))
    
    img = Image.alpha_composite(img, border_img)
    
    # 3. Rails OBLIGATOIRES dans la moitié supérieure du carré
    center_x = size / 2
    half_height = size / 2  # Limite entre moitié supérieure et inférieure
    rail_top_y = margin + square_size * 0.15  # 15% depuis le haut du carré
    rail_bottom_y = half_height - square_size * 0.05  # Juste au-dessus du milieu
    
    # Deux lignes parallèles en perspective
    num_rails = 2
    rail_spacing_start = square_size * 0.15  # Espacement en bas
    rail_spacing_end = square_size * 0.05   # Espacement en haut (perspective)
    
    rail_width = int(size * 0.02)  # 2% de la taille (rails bien visibles)
    
    for rail_idx in range(num_rails):
        # Calculer l'offset pour chaque rail
        if rail_idx == 0:
            offset_start = -rail_spacing_start / 2
            offset_end = -rail_spacing_end / 2
        else:
            offset_start = rail_spacing_start / 2
            offset_end = rail_spacing_end / 2
        
        # Point de départ (en bas)
        start_x = center_x + offset_start
        start_y = rail_bottom_y
        
        # Point d'arrivée (en haut)
        end_x = center_x + offset_end
        end_y = rail_top_y
        
        # Dessiner le rail avec dégradé
        steps = 80
        for i in range(steps):
            t = i / steps
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            
            # Dégradé rose → bleu selon la position
            color_ratio = t
            if rail_idx == 0:
                # Premier rail : plus rose
                rail_color = (
                    int(rose_corail[0] * (1 - color_ratio * 0.5) + bleu_lavande[0] * color_ratio * 0.5),
                    int(rose_corail[1] * (1 - color_ratio * 0.5) + bleu_lavande[1] * color_ratio * 0.5),
                    int(rose_corail[2] * (1 - color_ratio * 0.5) + bleu_lavande[2] * color_ratio * 0.5),
                    255
                )
            else:
                # Deuxième rail : plus bleu
                rail_color = (
                    int(rose_corail[0] * (0.5 - color_ratio * 0.3) + bleu_lavande[0] * (0.5 + color_ratio * 0.3)),
                    int(rose_corail[1] * (0.5 - color_ratio * 0.3) + bleu_lavande[1] * (0.5 + color_ratio * 0.3)),
                    int(rose_corail[2] * (0.5 - color_ratio * 0.3) + bleu_lavande[2] * (0.5 + color_ratio * 0.3)),
                    255
                )
            
            # Dessiner un segment du rail (plus épais pour visibilité)
            draw.ellipse(
                [(x - rail_width/2, y - rail_width/2),
                 (x + rail_width/2, y + rail_width/2)],
                fill=rail_color
            )
        
        # Dessiner les traverses simples
        num_traverses = 6
        for i in range(num_traverses):
            t = i / (num_traverses - 1) if num_traverses > 1 else 0
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            
            # Traverse horizontale qui relie les deux rails
            traverse_width = rail_spacing_start * (1 - t * 0.5)  # Rétrécit avec la perspective
            traverse_height = rail_width * 0.4
            
            # Calculer les positions des deux extrémités de la traverse
            if rail_idx == 0:
                # Traverse partant du rail gauche
                traverse_x1 = center_x - traverse_width / 2
                traverse_x2 = center_x + traverse_width / 2
            else:
                # Pour le rail droit, on dessine seulement si c'est le dernier rail
                continue
            
            # Dessiner la traverse
            draw.rectangle(
                [(traverse_x1, y - traverse_height/2),
                 (traverse_x2, y + traverse_height/2)],
                fill=(220, 220, 240, 220)
            )
    
    # 4. Texte "PK ASSIST" dans la moitié inférieure, sur UNE SEULE ligne
    try:
        font_size_main = int(size * 0.10)
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
    # Positionner dans la moitié inférieure
    text_y = half_height + square_size * 0.15  # 15% dans la moitié inférieure
    
    # Calculer la largeur du texte pour le centrer
    bbox = draw.textbbox((0, 0), text, font=font_main)
    text_width = bbox[2] - bbox[0]
    text_x = (size - text_width) / 2
    
    # Créer une image temporaire pour le texte avec dégradé
    text_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_img)
    
    # Dessiner le texte caractère par caractère avec dégradé
    char_widths = []
    for char in text:
        bbox_char = text_draw.textbbox((0, 0), char, font=font_main)
        char_widths.append(bbox_char[2] - bbox_char[0])
    
    current_x = text_x
    for i, char in enumerate(text):
        ratio = i / (len(text) - 1) if len(text) > 1 else 0
        
        # Dégradé pastel rose → bleu lavande
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
    
    # 5. Texte "RER A" juste en dessous, plus petit
    try:
        font_size_sub = int(size * 0.05)
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
    
    # Dessiner en bleu très clair, sans glow excessif
    draw.text((text_x_sub, text_y_sub), text_sub, font=font_sub, fill=(*bleu_tres_clair, 255))
    
    return img

if __name__ == "__main__":
    print("Création du logo PK ASSIST v3...")
    
    # Créer le logo en haute résolution
    logo = create_pk_assist_logo_v3(2048)
    
    # Sauvegarder
    output_path = "images/pk-assist-logo.png"
    logo.save(output_path, 'PNG', optimize=True)
    
    print(f"✅ Logo créé : {output_path}")
    print(f"   Taille : {logo.size}")
    print(f"   Format : PNG avec transparence")
    print(f"   Rails : bien visibles dans la moitié supérieure")
    print(f"   Texte : PK ASSIST sur une seule ligne")

