"""
Basic tests for the maptoposter library.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from maptoposter import list_themes, load_theme


def test_list_themes():
    """Test that list_themes returns expected themes."""
    themes = list_themes()
    
    assert isinstance(themes, list), "list_themes should return a list"
    assert len(themes) > 0, "Should have at least one theme"
    
    # Check for some expected themes
    expected_themes = ['noir', 'blueprint', 'sunset', 'feature_based']
    for theme in expected_themes:
        assert theme in themes, f"Expected theme '{theme}' not found"
    
    print(f"✓ test_list_themes passed - found {len(themes)} themes")


def test_load_theme():
    """Test that load_theme loads valid theme data."""
    # Test loading a known theme
    theme = load_theme('noir')
    
    assert isinstance(theme, dict), "load_theme should return a dict"
    assert 'bg' in theme, "Theme should have 'bg' color"
    assert 'text' in theme, "Theme should have 'text' color"
    assert 'road_motorway' in theme, "Theme should have road colors"
    
    # Test that theme has expected structure
    assert theme['bg'].startswith('#'), "Color should be hex format"
    
    print(f"✓ test_load_theme passed - loaded theme '{theme.get('name', 'unknown')}'")


def test_load_nonexistent_theme():
    """Test that load_theme handles nonexistent themes gracefully."""
    theme = load_theme('nonexistent_theme_xyz')
    
    assert isinstance(theme, dict), "Should return fallback theme dict"
    assert 'bg' in theme, "Fallback theme should have required fields"
    
    print("✓ test_load_nonexistent_theme passed - fallback works")


if __name__ == "__main__":
    print("Running maptoposter library tests...\n")
    
    test_list_themes()
    test_load_theme()
    test_load_nonexistent_theme()
    
    print("\n✅ All tests passed!")
