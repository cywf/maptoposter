#!/usr/bin/env python3
"""
Generate placeholder preview images for themes.
Creates simple colored rectangles based on theme colors.
"""

import json
import os
from PIL import Image, ImageDraw, ImageFont

def create_placeholder_preview(theme_id, theme_data, output_path):
    """Create a simple placeholder preview image."""
    # Image dimensions (portrait orientation)
    width, height = 300, 400
    
    # Get theme colors
    bg_color = theme_data.get('bg', '#FFFFFF')
    road_color = theme_data.get('road_primary', '#000000')
    text_color = theme_data.get('text', '#000000')
    
    # Create image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw some simple roads as lines
    road_width = 3
    for i in range(0, width, 30):
        draw.line([(i, 0), (i, height)], fill=road_color, width=road_width)
    
    for i in range(0, height, 30):
        draw.line([(0, i), (width, i)], fill=road_color, width=road_width)
    
    # Add theme name text at bottom
    try:
        # Try to use a nice font, fallback to default
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except (OSError, IOError):
        font = ImageFont.load_default()
    
    theme_name = theme_data.get('name', theme_id)
    
    # Draw text background
    text_bbox = draw.textbbox((0, 0), theme_name, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_x = (width - text_width) // 2
    text_y = height - text_height - 20
    
    # Draw semi-transparent background for text
    draw.rectangle(
        [(0, height - 60), (width, height)],
        fill=bg_color
    )
    
    # Draw text
    draw.text((text_x, text_y), theme_name, fill=text_color, font=font)
    
    # Save
    img.save(output_path)
    print(f"  Created {output_path}")

def main():
    themes_dir = "themes"
    output_dir = "site/assets/theme-previews"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Read all theme files
    for filename in os.listdir(themes_dir):
        if not filename.endswith('.json'):
            continue
        
        theme_id = filename[:-5]
        theme_path = os.path.join(themes_dir, filename)
        
        with open(theme_path, 'r') as f:
            theme_data = json.load(f)
        
        output_path = os.path.join(output_dir, f"{theme_id}.png")
        create_placeholder_preview(theme_id, theme_data, output_path)
    
    print(f"\n✓ Generated placeholder previews for all themes")

if __name__ == "__main__":
    main()
