#!/usr/bin/env python3
"""
Build theme index JSON for the GitHub Pages UI.
Reads all theme files from themes/ and generates site/themes/index.json
"""

import json
import os
import sys

def build_theme_index():
    """Generate themes index JSON file."""
    themes_dir = "themes"
    output_dir = "site/themes"
    output_file = os.path.join(output_dir, "index.json")
    
    if not os.path.exists(themes_dir):
        print(f"Error: {themes_dir} directory not found")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Read all theme files
    themes = []
    for filename in sorted(os.listdir(themes_dir)):
        if not filename.endswith('.json'):
            continue
        
        theme_id = filename[:-5]  # Remove .json extension
        theme_path = os.path.join(themes_dir, filename)
        
        try:
            with open(theme_path, 'r') as f:
                theme_data = json.load(f)
                
            themes.append({
                "theme": theme_id,
                "name": theme_data.get("name", theme_id),
                "description": theme_data.get("description", "")
            })
            
        except Exception as e:
            print(f"Warning: Could not read {theme_path}: {e}")
            continue
    
    # Write index file
    with open(output_file, 'w') as f:
        json.dump(themes, f, indent=2)
    
    print(f"✓ Generated {output_file} with {len(themes)} themes")
    return len(themes)

if __name__ == "__main__":
    build_theme_index()
