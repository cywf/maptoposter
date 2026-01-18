"""
Core generator module for creating map posters.
"""

import osmnx as ox
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.colors as mcolors
import numpy as np
from geopy.geocoders import Nominatim
from tqdm import tqdm
import time
import json
import os
from datetime import datetime

THEMES_DIR = "themes"
FONTS_DIR = "fonts"
POSTERS_DIR = "posters"


def load_fonts():
    """
    Load Roboto fonts from the fonts directory.
    Returns dict with font paths for different weights.
    """
    fonts = {
        'bold': os.path.join(FONTS_DIR, 'Roboto-Bold.ttf'),
        'regular': os.path.join(FONTS_DIR, 'Roboto-Regular.ttf'),
        'light': os.path.join(FONTS_DIR, 'Roboto-Light.ttf')
    }
    
    # Verify fonts exist
    for weight, path in fonts.items():
        if not os.path.exists(path):
            return None
    
    return fonts


def list_themes():
    """
    Returns a list of available theme names from the themes directory.
    """
    if not os.path.exists(THEMES_DIR):
        return []
    
    themes = []
    for file in sorted(os.listdir(THEMES_DIR)):
        if file.endswith('.json'):
            theme_name = file[:-5]  # Remove .json extension
            themes.append(theme_name)
    return themes


def load_theme(theme_name="feature_based"):
    """
    Load theme from JSON file in themes directory.
    Returns a dict with theme colors and metadata.
    """
    theme_file = os.path.join(THEMES_DIR, f"{theme_name}.json")
    
    if not os.path.exists(theme_file):
        # Fallback to embedded default theme
        return {
            "name": "Feature-Based Shading",
            "bg": "#FFFFFF",
            "text": "#000000",
            "gradient_color": "#FFFFFF",
            "water": "#C0C0C0",
            "parks": "#F0F0F0",
            "road_motorway": "#0A0A0A",
            "road_primary": "#1A1A1A",
            "road_secondary": "#2A2A2A",
            "road_tertiary": "#3A3A3A",
            "road_residential": "#4A4A4A",
            "road_default": "#3A3A3A"
        }
    
    with open(theme_file, 'r') as f:
        theme = json.load(f)
        return theme


def get_coordinates(city, country):
    """
    Fetches coordinates for a given city and country using geopy.
    Returns (latitude, longitude) tuple.
    """
    geolocator = Nominatim(user_agent="city_map_poster")
    
    # Add a small delay to respect Nominatim's usage policy
    time.sleep(1)
    
    location = geolocator.geocode(f"{city}, {country}")
    
    if location:
        return (location.latitude, location.longitude)
    else:
        raise ValueError(f"Could not find coordinates for {city}, {country}")


def create_gradient_fade(ax, color, location='bottom', zorder=10):
    """
    Creates a fade effect at the top or bottom of the map.
    """
    vals = np.linspace(0, 1, 256).reshape(-1, 1)
    gradient = np.hstack((vals, vals))
    
    rgb = mcolors.to_rgb(color)
    my_colors = np.zeros((256, 4))
    my_colors[:, 0] = rgb[0]
    my_colors[:, 1] = rgb[1]
    my_colors[:, 2] = rgb[2]
    
    if location == 'bottom':
        my_colors[:, 3] = np.linspace(1, 0, 256)
        extent_y_start = 0
        extent_y_end = 0.25
    else:
        my_colors[:, 3] = np.linspace(0, 1, 256)
        extent_y_start = 0.75
        extent_y_end = 1.0

    custom_cmap = mcolors.ListedColormap(my_colors)
    
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    y_range = ylim[1] - ylim[0]
    
    y_bottom = ylim[0] + y_range * extent_y_start
    y_top = ylim[0] + y_range * extent_y_end
    
    ax.imshow(gradient, extent=[xlim[0], xlim[1], y_bottom, y_top], 
              aspect='auto', cmap=custom_cmap, zorder=zorder, origin='lower')


def get_edge_colors_by_type(G, theme):
    """
    Assigns colors to edges based on road type hierarchy.
    Returns a list of colors corresponding to each edge in the graph.
    """
    edge_colors = []
    
    for u, v, data in G.edges(data=True):
        # Get the highway type (can be a list or string)
        highway = data.get('highway', 'unclassified')
        
        # Handle list of highway types (take the first one)
        if isinstance(highway, list):
            highway = highway[0] if highway else 'unclassified'
        
        # Assign color based on road type
        if highway in ['motorway', 'motorway_link']:
            color = theme['road_motorway']
        elif highway in ['trunk', 'trunk_link', 'primary', 'primary_link']:
            color = theme['road_primary']
        elif highway in ['secondary', 'secondary_link']:
            color = theme['road_secondary']
        elif highway in ['tertiary', 'tertiary_link']:
            color = theme['road_tertiary']
        elif highway in ['residential', 'living_street', 'unclassified']:
            color = theme['road_residential']
        else:
            color = theme['road_default']
        
        edge_colors.append(color)
    
    return edge_colors


def get_edge_widths_by_type(G):
    """
    Assigns line widths to edges based on road type.
    Major roads get thicker lines.
    """
    edge_widths = []
    
    for u, v, data in G.edges(data=True):
        highway = data.get('highway', 'unclassified')
        
        if isinstance(highway, list):
            highway = highway[0] if highway else 'unclassified'
        
        # Assign width based on road importance
        if highway in ['motorway', 'motorway_link']:
            width = 1.2
        elif highway in ['trunk', 'trunk_link', 'primary', 'primary_link']:
            width = 1.0
        elif highway in ['secondary', 'secondary_link']:
            width = 0.8
        elif highway in ['tertiary', 'tertiary_link']:
            width = 0.6
        else:
            width = 0.4
        
        edge_widths.append(width)
    
    return edge_widths


def create_poster(city, country, theme, dist=29000, output_path=None, 
                  dpi=300, network_type='all', verbose=True):
    """
    Create a map poster for a given city.
    
    Args:
        city: City name
        country: Country name
        theme: Theme name or theme dict
        dist: Map radius in meters (default: 29000)
        output_path: Output file path (default: auto-generate in posters/)
        dpi: DPI for output image (default: 300)
        network_type: OSMnx network type (default: 'all')
        verbose: Print progress messages (default: True)
    
    Returns:
        str: Path to the generated poster file
    """
    # Load theme if string provided
    if isinstance(theme, str):
        theme_data = load_theme(theme)
        theme_name = theme
    else:
        theme_data = theme
        theme_name = theme.get('name', 'custom')
    
    # Get coordinates
    if verbose:
        print(f"\nGenerating map for {city}, {country}...")
        print("Looking up coordinates...")
    
    coords = get_coordinates(city, country)
    
    if verbose:
        print(f"✓ Found coordinates: {coords[0]:.4f}, {coords[1]:.4f}")
    
    # Generate output filename if not provided
    if output_path is None:
        if not os.path.exists(POSTERS_DIR):
            os.makedirs(POSTERS_DIR)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        city_slug = city.lower().replace(' ', '_')
        filename = f"{city_slug}_{theme_name}_{timestamp}.png"
        output_path = os.path.join(POSTERS_DIR, filename)
    
    # Fetch map data
    if verbose:
        pbar = tqdm(total=3, desc="Fetching map data", unit="step", 
                   bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}')
    
    # 1. Fetch Street Network
    if verbose:
        pbar.set_description("Downloading street network")
    G = ox.graph_from_point(coords, dist=dist, dist_type='bbox', network_type=network_type)
    if verbose:
        pbar.update(1)
    time.sleep(0.5)
    
    # 2. Fetch Water Features
    if verbose:
        pbar.set_description("Downloading water features")
    try:
        water = ox.features_from_point(coords, tags={'natural': 'water', 'waterway': 'riverbank'}, dist=dist)
    except:
        water = None
    if verbose:
        pbar.update(1)
    time.sleep(0.3)
    
    # 3. Fetch Parks
    if verbose:
        pbar.set_description("Downloading parks/green spaces")
    try:
        parks = ox.features_from_point(coords, tags={'leisure': 'park', 'landuse': 'grass'}, dist=dist)
    except:
        parks = None
    if verbose:
        pbar.update(1)
        pbar.close()
        print("✓ All data downloaded successfully!")
    
    # Setup plot
    if verbose:
        print("Rendering map...")
    
    fig, ax = plt.subplots(figsize=(12, 16), facecolor=theme_data['bg'])
    ax.set_facecolor(theme_data['bg'])
    ax.set_position([0, 0, 1, 1])
    
    # Plot layers
    if water is not None and not water.empty:
        water.plot(ax=ax, facecolor=theme_data['water'], edgecolor='none', zorder=1)
    if parks is not None and not parks.empty:
        parks.plot(ax=ax, facecolor=theme_data['parks'], edgecolor='none', zorder=2)
    
    # Roads with hierarchy coloring
    edge_colors = get_edge_colors_by_type(G, theme_data)
    edge_widths = get_edge_widths_by_type(G)
    
    ox.plot_graph(
        G, ax=ax, bgcolor=theme_data['bg'],
        node_size=0,
        edge_color=edge_colors,
        edge_linewidth=edge_widths,
        show=False, close=False
    )
    
    # Gradients
    create_gradient_fade(ax, theme_data['gradient_color'], location='bottom', zorder=10)
    create_gradient_fade(ax, theme_data['gradient_color'], location='top', zorder=10)
    
    # Typography
    fonts = load_fonts()
    if fonts:
        font_main = FontProperties(fname=fonts['bold'], size=60)
        font_top = FontProperties(fname=fonts['bold'], size=40)
        font_sub = FontProperties(fname=fonts['light'], size=22)
        font_coords = FontProperties(fname=fonts['regular'], size=14)
        font_attr = FontProperties(fname=fonts['light'], size=8)
    else:
        font_main = FontProperties(family='monospace', weight='bold', size=60)
        font_top = FontProperties(family='monospace', weight='bold', size=40)
        font_sub = FontProperties(family='monospace', weight='normal', size=22)
        font_coords = FontProperties(family='monospace', size=14)
        font_attr = FontProperties(family='monospace', size=8)
    
    spaced_city = "  ".join(list(city.upper()))

    # Bottom text
    ax.text(0.5, 0.14, spaced_city, transform=ax.transAxes,
            color=theme_data['text'], ha='center', fontproperties=font_main, zorder=11)
    
    ax.text(0.5, 0.10, country.upper(), transform=ax.transAxes,
            color=theme_data['text'], ha='center', fontproperties=font_sub, zorder=11)
    
    lat, lon = coords
    coords_text = f"{lat:.4f}° N / {lon:.4f}° E" if lat >= 0 else f"{abs(lat):.4f}° S / {lon:.4f}° E"
    if lon < 0:
        coords_text = coords_text.replace("E", "W")
    
    ax.text(0.5, 0.07, coords_text, transform=ax.transAxes,
            color=theme_data['text'], alpha=0.7, ha='center', fontproperties=font_coords, zorder=11)
    
    ax.plot([0.4, 0.6], [0.125, 0.125], transform=ax.transAxes, 
            color=theme_data['text'], linewidth=1, zorder=11)

    # Attribution
    ax.text(0.98, 0.02, "© OpenStreetMap contributors", transform=ax.transAxes,
            color=theme_data['text'], alpha=0.5, ha='right', va='bottom', 
            fontproperties=font_attr, zorder=11)

    # Save
    if verbose:
        print(f"Saving to {output_path}...")
    plt.savefig(output_path, dpi=dpi, facecolor=theme_data['bg'])
    plt.close()
    
    if verbose:
        print(f"✓ Done! Poster saved as {output_path}")
    
    return output_path
