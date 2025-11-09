#!/usr/bin/env python3
"""
Génère une icône PNG 180x180 pour iOS à partir du design du titre
"""
try:
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
except ImportError:
    print("Installation de Pillow nécessaire : pip3 install Pillow")
    exit(1)

# Créer une image 180x180
size = 180
img = Image.new('RGB', (size, size), color='#1a1b3a')
draw = ImageDraw.Draw(img)

# Créer un gradient radial (approximation)
# On va créer plusieurs cercles concentriques avec des couleurs différentes
center = size // 2
for i in range(size):
    for j in range(size):
        dist = ((i - center)**2 + (j - center)**2)**0.5
        max_dist = (center**2 + center**2)**0.5
        
        if dist < max_dist * 0.1:
            color = (255, 159, 123)  # #ff9f7b
        elif dist < max_dist * 0.24:
            # Interpolation entre #ff9f7b et #ff4b6b
            ratio = (dist - max_dist * 0.1) / (max_dist * 0.14)
            r = int(255 * (1 - ratio) + 255 * ratio)
            g = int(159 * (1 - ratio) + 75 * ratio)
            b = int(123 * (1 - ratio) + 107 * ratio)
            color = (r, g, b)
        elif dist < max_dist * 0.70:
            # Interpolation entre #ff4b6b et #3d7bff
            ratio = (dist - max_dist * 0.24) / (max_dist * 0.46)
            r = int(255 * (1 - ratio) + 61 * ratio)
            g = int(75 * (1 - ratio) + 123 * ratio)
            b = int(107 * (1 - ratio) + 255 * ratio)
            color = (r, g, b)
        else:
            # Interpolation entre #3d7bff et #1a1b3a
            ratio = (dist - max_dist * 0.70) / (max_dist * 0.30)
            r = int(61 * (1 - ratio) + 26 * ratio)
            g = int(123 * (1 - ratio) + 27 * ratio)
            b = int(255 * (1 - ratio) + 58 * ratio)
            color = (r, g, b)
        
        img.putpixel((i, j), color)

# Dessiner les coins arrondis (masquer les coins)
mask = Image.new('L', (size, size), 0)
mask_draw = ImageDraw.Draw(mask)
radius = 35
mask_draw.rounded_rectangle([(0, 0), (size-1, size-1)], radius, fill=255)
img.putalpha(mask)

# Créer une nouvelle image avec transparence
final_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
final_img.paste(img, (0, 0), mask)

# Dessiner l'emoji train (approximation avec un cercle blanc)
# Comme on ne peut pas facilement dessiner un emoji, on va utiliser un symbole
try:
    # Essayer d'utiliser une police qui supporte les emojis
    font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 100)
except:
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Apple Color Emoji.ttc", 100)
    except:
        font = ImageFont.load_default()

# Dessiner le train emoji
draw = ImageDraw.Draw(final_img)
text = "🚂"
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
position = ((size - text_width) // 2, (size - text_height) // 2 - 10)
draw.text(position, text, fill=(255, 255, 255, 255), font=font)

# Sauvegarder
final_img.save('icon-180x180.png', 'PNG')
print("Icône générée : icon-180x180.png")





