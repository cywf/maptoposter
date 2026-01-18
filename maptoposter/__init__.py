"""
MapToPoster - Generate beautiful city map posters

A library for creating minimalist map posters from OpenStreetMap data.
"""

from .generator import (
    load_theme,
    list_themes,
    get_coordinates,
    create_poster,
)

__version__ = "1.0.0"
__all__ = [
    "load_theme",
    "list_themes",
    "get_coordinates",
    "create_poster",
]
