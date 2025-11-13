#!/usr/bin/env python3
"""
Génère un logo retrowave/synthwave pour PK-ASSIST
Style néon lumineux, grille 3D, voie ferrée stylisée
"""

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import numpy as np
except ImportError:
    print("❌ Erreur : Pillow et numpy nécessaires")
    print("   Installation : pip3 install Pillow numpy")
    exit(1)

import math

def create_retrowave_logo(size=8192):
    """Crée le logo retrowave PK-ASSIST"""
    
    # Créer l'image avec fond transparent
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Couleurs néon
    rouge_magenta = (255, 0, 150)  # Rouge/magenta vibrant
    orange_vif = (255, 100, 0)    # Orange vif
    jaune_neon = (255, 255, 0)    # Jaune néon
    bleu_electrique = (0, 255, 255)  # Bleu électrique/cyan
    blanc_neon = (255, 255, 255)  # Blanc néon
    
    center_x = size / 2
    center_y = size / 2
    
    # 1. Grille de voie ferrée stylisée en néon (perspective vers le centre)
    print("Création de la grille de voie ferrée...")
    
    # Rails en perspective
    num_rails = 2
    rail_spacing_start = size * 0.3  # Espacement en bas
    rail_spacing_end = size * 0.05   # Espacement en haut (perspective)
    
    rail_bottom_y = size * 0.75  # Position en bas
    rail_top_y = center_y  # Convergent vers le centre
    
    rail_width = int(size * 0.008)  # Épaisseur des rails
    
    for rail_idx in range(num_rails):
        if rail_idx == 0:
            offset_start = -rail_spacing_start / 2
            offset_end = -rail_spacing_end / 2
        else:
            offset_start = rail_spacing_start / 2
            offset_end = rail_spacing_end / 2
        
        start_x = center_x + offset_start
        start_y = rail_bottom_y
        end_x = center_x + offset_end
        end_y = rail_top_y
        
        # Dessiner le rail avec effet néon
        steps = 150
        for i in range(steps):
            t = i / steps
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            
            # Couleur néon cyan pour les rails
            rail_color = (*bleu_electrique, 255)
            
            # Dessiner avec glow
            for glow_radius in range(rail_width, 0, -1):
                alpha = 255 if glow_radius == rail_width else 100 - glow_radius * 10
                draw.ellipse(
                    [(x - glow_radius/2, y - glow_radius/2),
                     (x + glow_radius/2, y + glow_radius/2)],
                    fill=(*bleu_electrique, min(alpha, 255))
                )
        
        # Traverses en perspective
        num_traverses = 8
        for i in range(num_traverses):
            t = i / (num_traverses - 1) if num_traverses > 1 else 0
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            
            traverse_width = rail_spacing_start * (1 - t * 0.7)
            traverse_x1 = center_x - traverse_width / 2
            traverse_x2 = center_x + traverse_width / 2
            
            # Traverse avec effet néon
            for glow in range(3, 0, -1):
                alpha = 200 if glow == 3 else 100 - glow * 30
                draw.line(
                    [(traverse_x1, y), (traverse_x2, y)],
                    fill=(*bleu_electrique, min(alpha, 255)),
                    width=int(rail_width * 0.6) + glow
                )
    
    # 2. Lignes de vitesse horizontales lumineuses
    print("Ajout des lignes de vitesse...")
    num_speed_lines = 12
    for i in range(num_speed_lines):
        y_pos = size * 0.6 + i * (size * 0.3 / num_speed_lines)
        
        # Lignes qui s'étendent de chaque côté
        line_length = size * 0.4
        x_start = center_x - line_length
        x_end = center_x + line_length
        
        # Effet de vitesse avec dégradé
        for j in range(int(line_length)):
            t = j / line_length
            x1 = x_start + j
            x2 = x_start + j + 1
            
            # Dégradé d'intensité
            intensity = int(255 * (1 - abs(t - 0.5) * 2))
            speed_color = (*bleu_electrique, intensity // 3)
            
            draw.line([(x1, y_pos), (x2, y_pos)], fill=speed_color, width=2)
    
    # 3. Texte "PK-ASSIST" avec effet néon et grille 3D
    print("Création du texte PK-ASSIST...")
    
    try:
        font_size_main = int(size * 0.15)
        try:
            font_main = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size_main)
        except:
            try:
                font_main = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size_main)
            except:
                font_main = ImageFont.load_default()
    except:
        font_main = ImageFont.load_default()
    
    text = "PK-ASSIST"
    text_y = size * 0.5  # Position verticale
    
    # Calculer la largeur du texte
    bbox = draw.textbbox((0, 0), text, font=font_main)
    text_width = bbox[2] - bbox[0]
    text_x = (size - text_width) / 2
    
    # Créer plusieurs couches pour l'effet néon
    text_layers = []
    
    # Couche 1 : Halo bleu électrique (ombre externe)
    halo_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    halo_draw = ImageDraw.Draw(halo_img)
    
    # Dessiner le texte plusieurs fois avec blur pour créer le halo
    for blur_radius in [15, 12, 9, 6, 3]:
        temp_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        temp_draw.text((text_x, text_y), text, font=font_main, fill=(*bleu_electrique, 200))
        temp_img = temp_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        halo_img = Image.alpha_composite(halo_img, temp_img)
    
    # Couche 2 : Texte principal avec dégradé rouge/magenta → orange/jaune
    text_main_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    text_main_draw = ImageDraw.Draw(text_main_img)
    
    # Dessiner caractère par caractère avec dégradé
    char_widths = []
    for char in text:
        bbox_char = text_main_draw.textbbox((0, 0), char, font=font_main)
        char_widths.append(bbox_char[2] - bbox_char[0])
    
    current_x = text_x
    for i, char in enumerate(text):
        ratio = i / (len(text) - 1) if len(text) > 1 else 0
        
        # Dégradé rouge/magenta → orange → jaune
        if ratio < 0.5:
            # Rouge/magenta → orange
            r = int(rouge_magenta[0] * (1 - ratio * 2) + orange_vif[0] * (ratio * 2))
            g = int(rouge_magenta[1] * (1 - ratio * 2) + orange_vif[1] * (ratio * 2))
            b = int(rouge_magenta[2] * (1 - ratio * 2) + orange_vif[2] * (ratio * 2))
        else:
            # Orange → jaune
            local_ratio = (ratio - 0.5) * 2
            r = int(orange_vif[0] * (1 - local_ratio) + jaune_neon[0] * local_ratio)
            g = int(orange_vif[1] * (1 - local_ratio) + jaune_neon[1] * local_ratio)
            b = int(orange_vif[2] * (1 - local_ratio) + jaune_neon[2] * local_ratio)
        
        char_color = (r, g, b, 255)
        text_main_draw.text((current_x, text_y), char, font=font_main, fill=char_color)
        current_x += char_widths[i]
    
    # Couche 3 : Effet de grille 3D (lignes de perspective)
    grid_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    grid_draw = ImageDraw.Draw(grid_img)
    
    # Dessiner des lignes de grille qui partent du texte vers l'arrière
    num_grid_lines = 20
    for i in range(num_grid_lines):
        t = i / num_grid_lines
        y_pos = text_y + t * (size * 0.1)  # S'éloigne vers le bas
        
        # Lignes horizontales qui convergent
        x_start = text_x + t * text_width * 0.1
        x_end = text_x + text_width - t * text_width * 0.1
        
        grid_color = (*bleu_electrique, int(100 * (1 - t)))
        grid_draw.line([(x_start, y_pos), (x_end, y_pos)], fill=grid_color, width=1)
    
    # Couche 4 : Trail lumineux (ligne de lumière rémanente)
    trail_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    trail_draw = ImageDraw.Draw(trail_img)
    
    # Dessiner un trail qui suit les contours du texte
    trail_y = text_y + font_size_main * 0.1
    trail_x_start = text_x
    trail_x_end = text_x + text_width
    
    # Trail avec dégradé d'opacité
    for i in range(30):
        alpha = int(255 * (1 - i / 30))
        trail_width = int(size * 0.002 * (1 - i / 30))
        trail_y_pos = trail_y + i * 2
        
        trail_draw.line(
            [(trail_x_start, trail_y_pos), (trail_x_end, trail_y_pos)],
            fill=(*bleu_electrique, alpha),
            width=trail_width
        )
    
    # Combiner toutes les couches
    img = Image.alpha_composite(img, halo_img)  # Halo en premier
    img = Image.alpha_composite(img, grid_img)  # Grille
    img = Image.alpha_composite(img, trail_img)  # Trail
    img = Image.alpha_composite(img, text_main_img)  # Texte principal
    
    # 4. Texte "RER A" (plus petit, centré, en dessous)
    print("Ajout du texte RER A...")
    
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
    text_y_sub = text_y + font_size_main + size * 0.03
    
    # Halo bleu pour RER A aussi
    rer_halo_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    rer_halo_draw = ImageDraw.Draw(rer_halo_img)
    
    for blur_radius in [8, 6, 4, 2]:
        temp_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        temp_draw.text((text_x_sub, text_y_sub), text_sub, font=font_sub, fill=(*bleu_electrique, 150))
        temp_img = temp_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        rer_halo_img = Image.alpha_composite(rer_halo_img, temp_img)
    
    # Texte RER A en blanc néon
    rer_text_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    rer_text_draw = ImageDraw.Draw(rer_text_img)
    rer_text_draw.text((text_x_sub, text_y_sub), text_sub, font=font_sub, fill=(*blanc_neon, 255))
    
    img = Image.alpha_composite(img, rer_halo_img)
    img = Image.alpha_composite(img, rer_text_img)
    
    return img

if __name__ == "__main__":
    print("Création du logo retrowave PK-ASSIST...")
    
    # Créer le logo en 8K
    logo = create_retrowave_logo(8192)
    
    # Sauvegarder
    output_path = "images/pk-assist-logo.png"
    logo.save(output_path, 'PNG', optimize=True)
    
    print(f"✅ Logo créé : {output_path}")
    print(f"   Taille : {logo.size} (8K)")
    print(f"   Format : PNG avec transparence")
    print(f"   Style : Retrowave/Synthwave néon")

