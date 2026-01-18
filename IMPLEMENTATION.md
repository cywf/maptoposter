# MapToPoster GitHub Pages Implementation

## Summary

This implementation adds a complete GitHub Pages web UI with an issue-based workflow for generating map posters.

## What Was Implemented

### 1. Python Library Refactoring
- Created `maptoposter/` module with reusable library functions
- `maptoposter/generator.py` - Core generation logic
- `maptoposter/__init__.py` - Module exports
- Refactored `create_map_poster.py` to use the library (CLI still works)

### 2. GitHub Pages UI
- **Location**: `site/` directory
- **Files**:
  - `index.html` - Main UI with form and theme gallery
  - `styles.css` - Clean, responsive styling
  - `app.js` - JavaScript for form handling and GitHub issue creation
  - `themes/index.json` - Theme metadata index
  - `assets/theme-previews/*.png` - Preview images for all 17 themes

### 3. GitHub Actions Workflows
1. **`generate_from_issue.yml`** - Main workflow
   - Triggers on issue creation with "JOB: MAPTOPOSTER" marker
   - Parses city, country, theme, distance from issue body
   - Validates inputs
   - Runs poster generation
   - Creates private Gist with GitHub CLI
   - Comments back with download link

2. **`deliver_gist.yml`** - Reusable workflow for Gist creation
   - Takes poster file path and filename
   - Authenticates with GIST_TOKEN
   - Creates private Gist
   - Returns Gist URL

3. **`deploy_pages.yml`** - GitHub Pages deployment
   - Deploys `site/` directory to GitHub Pages
   - Triggers on push to main when site files change

4. **`build_theme_index.yml`** - Auto-update theme index
   - Regenerates `site/themes/index.json` when themes change
   - Commits changes automatically

5. **`generate_previews.yml`** - Generate real theme previews
   - Manual workflow to generate actual poster previews
   - Uses specified city (default: San Francisco)
   - Creates resized preview images for all themes

### 4. Tools
- `tools/build_theme_index.py` - Builds theme index JSON
- `tools/generate_placeholder_previews.py` - Creates placeholder preview images

### 5. Documentation
- Updated README.md with:
  - Web UI section with usage instructions
  - Required secrets documentation (GIST_TOKEN)
  - Issue-based workflow explanation
  - Link to GitHub Pages URL

### 6. Tests
- `tests/test_generator.py` - Basic library tests
  - Tests `list_themes()`
  - Tests `load_theme()`
  - Tests fallback handling

## How It Works

### User Flow
1. User visits GitHub Pages site at `https://cywf.github.io/maptoposter`
2. Browses theme gallery with previews
3. Fills in city, country, distance, and selects theme
4. Clicks "Generate Map Poster"
5. Redirected to GitHub issue creation with pre-filled data
6. Submits issue (requires GitHub login)
7. GitHub Actions workflow:
   - Detects the issue
   - Parses parameters
   - Installs dependencies
   - Generates poster using OSMnx
   - Creates private Gist with poster
   - Comments on issue with Gist URL
8. User clicks Gist link to download poster

### Issue Body Schema
```
JOB: MAPTOPOSTER
city: <City>
country: <Country>
theme: <theme>
distance: <distance>
requested_at: <ISO-8601 timestamp>
user_agent: <browser user agent>
```

## Required Setup

### For Repository Maintainers
1. **Add GIST_TOKEN secret**:
   - GitHub Settings → Developer settings → Personal access tokens
   - Generate token with `gist` scope
   - Add to repository as secret: Settings → Secrets → Actions → New secret
   - Name: `GIST_TOKEN`

2. **Enable GitHub Pages**:
   - Repository Settings → Pages
   - Source: GitHub Actions
   - The `deploy_pages.yml` workflow will handle deployment

3. **Enable Issues**:
   - Repository Settings → Features → Issues (checked)

## Security Features

✅ No tokens in client-side JavaScript
✅ Private Gists (not public)
✅ Token stored only in GitHub Actions secrets
✅ Input validation in workflow
✅ Safe distance range enforcement (1000-50000m)
✅ Theme existence validation

## Testing

All tests pass:
```bash
$ python tests/test_generator.py
✓ test_list_themes passed - found 17 themes
✓ test_load_theme passed - loaded theme 'Noir'
✓ test_load_nonexistent_theme passed - fallback works
✅ All tests passed!
```

CLI still works:
```bash
$ python create_map_poster.py --list-themes
# Lists all 17 themes with descriptions
```

## Screenshot

Full UI: https://github.com/user-attachments/assets/3405570c-a348-4b0a-a964-c8c0ca577ca0

## Notes

- Placeholder preview images are currently simple grid patterns based on theme colors
- Run the `generate_previews.yml` workflow manually to create real poster previews
- Poster generation typically takes 3-5 minutes depending on city size and OSM API response time
- Generated Gists are private and only accessible via the direct URL
