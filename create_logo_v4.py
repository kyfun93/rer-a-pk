#!/usr/bin/env python3
"""
Génère un logo vectoriel carré 1:1 pour PK Assist
Style retrowave doux, couleurs pastel, design simple et lisible
Rails en style contour (lignes pastel, pas de remplissage)
"""

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import numpy as np
except ImportError:
    print("❌ Erreur : Pillow et numpy nécessaires")
    print("   Installation : pip3 install Pillow numpy")
    exit(1)

import math

def create_pk_assist_logo_v4(size=2048):
    """Crée le logo PK Assist version 4"""
    
    # Créer l'image avec fond transparent
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Couleurs pastel
    violet_fonce = (45, 35, 65)  # Violet foncé désaturé
    rose_corail = (255, 180, 180)  # Rose corail clair
    bleu_lavande = (180, 200, 255)  # Bleu lavande clair
    blanc_casse = (240, 240, 250)  # Blanc cassé
    bleu_tres_clair = (200, 220, 255)  # Bleu très clair
    
    # 1. Grand carré aux coins très arrondis
    margin = size * 0.1  # 10% de marge
    square_size = size - 2 * margin
    corner_radius = square_size * 0.25  # Coins très arrondis (25% du côté)
    
    # Intérieur violet nuit foncé avec petits points lumineux (étoiles)
    square_bg = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    square_draw = ImageDraw.Draw(square_bg)
    
    # Fond uniforme violet nuit
    square_draw.rounded_rectangle(
        [(margin, margin), (size - margin, size - margin)],
        radius=int(corner_radius),
        fill=(*violet_fonce, 255)
    )
    
    # Petits points lumineux discrets (étoiles) à l'intérieur du carré
    np.random.seed(42)
    num_stars = 20
    for _ in range(num_stars):
        x = np.random.randint(int(margin * 1.1), int(size - margin * 1.1))
        y = np.random.randint(int(margin * 1.1), int(size - margin * 1.1))
        brightness = np.random.randint(180, 240)
        radius = np.random.randint(1, 2)
        square_draw.ellipse([(x-radius, y-radius), (x+radius, y+radius)], 
                           fill=(brightness, brightness, brightness, 120))
    
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
    
    # 2. Contour fin en dégradé pastel (rose clair en haut → bleu lavande en bas)
    border_width = int(size * 0.012)  # Contour fin (1.2% de la taille)
    
    # Créer le contour avec dégradé vertical
    border_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    
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
    
    # 3. Rails ferroviaires minimalistes en style contour (moitié supérieure)
    center_x = size / 2
    half_height = size / 2
    rail_top_y = margin + square_size * 0.15  # 15% depuis le haut
    rail_bottom_y = half_height - square_size * 0.05  # Juste au-dessus du milieu
    
    # Deux lignes parallèles en perspective
    rail_spacing_start = square_size * 0.12  # Espacement en bas
    rail_spacing_end = square_size * 0.04   # Espacement en haut (perspective)
    
    line_width = int(size * 0.008)  # Lignes fines pour style contour
    
    for rail_idx in range(2):
        # Calculer l'offset pour chaque rail
        if rail_idx == 0:
            offset_start = -rail_spacing_start / 2
            offset_end = -rail_spacing_end / 2
            rail_color = (*rose_corail, 240)  # Rose pour le rail gauche
        else:
            offset_start = rail_spacing_start / 2
            offset_end = rail_spacing_end / 2
            rail_color = (*bleu_lavande, 240)  # Bleu pour le rail droit
        
        # Point de départ (en bas)
        start_x = center_x + offset_start
        start_y = rail_bottom_y
        
        # Point d'arrivée (en haut)
        end_x = center_x + offset_end
        end_y = rail_top_y
        
        # Dessiner la ligne du rail (style contour)
        steps = 100
        for i in range(steps - 1):
            t1 = i / steps
            t2 = (i + 1) / steps
            
            x1 = start_x + (end_x - start_x) * t1
            y1 = start_y + (end_y - start_y) * t1
            x2 = start_x + (end_x - start_x) * t2
            y2 = start_y + (end_y - start_y) * t2
            
            # Dessiner un segment de ligne
            draw.line([(x1, y1), (x2, y2)], fill=rail_color, width=line_width)
        
        # Dessiner quelques traverses simples
        num_traverses = 5
        for i in range(num_traverses):
            t = i / (num_traverses - 1) if num_traverses > 1 else 0
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            
            # Traverse horizontale qui relie les deux rails
            traverse_width = rail_spacing_start * (1 - t * 0.6)  # Rétrécit avec la perspective
            traverse_height = line_width * 0.6
            
            # Position de la traverse (centrée entre les deux rails)
            traverse_x1 = center_x - traverse_width / 2
            traverse_x2 = center_x + traverse_width / 2
            
            # Dessiner la traverse (ligne horizontale)
            draw.line(
                [(traverse_x1, y), (traverse_x2, y)],
                fill=(220, 220, 240, 200),
                width=int(traverse_height)
            )
    
    # 4. Texte "PK Assist" dans la moitié inférieure, sur UNE SEULE ligne
    try:
        font_size_main = int(size * 0.095)
        try:
            font_main = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size_main)
        except:
            try:
                font_main = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size_main)
            except:
                font_main = ImageFont.load_default()
    except:
        font_main = ImageFont.load_default()
    
    text = "PK Assist"  # Exactement comme demandé, pas tout en majuscules
    # Positionner dans la moitié inférieure
    text_y = half_height + square_size * 0.12  # 12% dans la moitié inférieure
    
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
    
    # Ajouter un effet glow léger
    glow_img = text_img.copy()
    glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=1.5))
    
    # Combiner avec l'image principale
    img = Image.alpha_composite(img, glow_img)
    img = Image.alpha_composite(img, text_img)
    
    # 5. Texte "RER A" juste en dessous, plus petit
    try:
        font_size_sub = int(size * 0.048)
        try:
            font_sub = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size_sub)
        except:
            try:
                font_sub = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size_sub)
            except:
                font_sub = ImageFont.load_default()
    except:
        font_sub = ImageFont.load_default()
    
    text_sub = "RER A"  # Exactement comme demandé
    bbox_sub = draw.textbbox((0, 0), text_sub, font=font_sub)
    text_width_sub = bbox_sub[2] - bbox_sub[0]
    text_x_sub = (size - text_width_sub) / 2
    text_y_sub = text_y + font_size_main + size * 0.018
    
    # Dessiner en bleu très clair ou blanc cassé
    draw.text((text_x_sub, text_y_sub), text_sub, font=font_sub, fill=(*bleu_tres_clair, 255))
    
    return img

if __name__ == "__main__":
    print("Création du logo PK Assist v4...")
    
    # Créer le logo en haute résolution
    logo = create_pk_assist_logo_v4(2048)
    
    # Sauvegarder
    output_path = "images/pk-assist-logo.png"
    logo.save(output_path, 'PNG', optimize=True)
    
    print(f"✅ Logo créé : {output_path}")
    print(f"   Taille : {logo.size}")
    print(f"   Format : PNG avec transparence")
    print(f"   Rails : style contour minimaliste dans moitié supérieure")
    print(f"   Texte : PK Assist (une seule ligne)")

