// Configuration
const GITHUB_REPO = 'cywf/maptoposter';
const THEMES_INDEX_URL = 'themes/index.json';

// State
let themes = [];
let selectedTheme = null;

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    await loadThemes();
    setupEventListeners();
});

// Load themes from index
async function loadThemes() {
    try {
        const response = await fetch(THEMES_INDEX_URL);
        if (!response.ok) {
            throw new Error('Failed to load themes');
        }
        themes = await response.json();
        renderThemes();
    } catch (error) {
        console.error('Error loading themes:', error);
        document.getElementById('themesGrid').innerHTML = 
            '<div class="loading" style="color: var(--error-color);">Failed to load themes. Please refresh the page.</div>';
    }
}

// Render theme grid
function renderThemes() {
    const grid = document.getElementById('themesGrid');
    
    if (themes.length === 0) {
        grid.innerHTML = '<div class="loading">No themes available.</div>';
        return;
    }

    grid.innerHTML = themes.map(theme => `
        <div class="theme-card" data-theme="${theme.theme}">
            <div class="theme-preview">
                <img src="assets/theme-previews/${theme.theme}.png" 
                     alt="${theme.name}" 
                     onerror="this.style.display='none'; this.parentElement.innerHTML='<span>Preview<br>Coming Soon</span>'">
            </div>
            <div class="theme-details">
                <h3>${theme.name}</h3>
                <p>${theme.description || 'No description available'}</p>
            </div>
        </div>
    `).join('');
    
    // Add event listeners after rendering
    document.querySelectorAll('.theme-card').forEach(card => {
        card.addEventListener('click', () => {
            const themeId = card.getAttribute('data-theme');
            selectTheme(themeId);
        });
    });
}

// Select theme
function selectTheme(themeId) {
    selectedTheme = themes.find(t => t.theme === themeId);
    
    // Update UI
    document.querySelectorAll('.theme-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.querySelector(`[data-theme="${themeId}"]`)?.classList.add('selected');
    
    // Update selected theme display
    const selectedThemeDiv = document.getElementById('selectedTheme');
    selectedThemeDiv.classList.add('has-selection');
    selectedThemeDiv.innerHTML = `
        <div class="theme-card-mini">
            <img src="assets/theme-previews/${selectedTheme.theme}.png" 
                 alt="${selectedTheme.name}"
                 onerror="this.style.display='none'">
            <div class="theme-info">
                <h3>${selectedTheme.name}</h3>
                <p>${selectedTheme.description || ''}</p>
            </div>
        </div>
    `;
    
    // Enable generate button if form is valid
    validateForm();
}

// Setup event listeners
function setupEventListeners() {
    // Form validation on input
    document.getElementById('city').addEventListener('input', validateForm);
    document.getElementById('country').addEventListener('input', validateForm);
    
    // Generate button
    document.getElementById('generateBtn').addEventListener('click', generateMapPoster);
}

// Validate form
function validateForm() {
    const city = document.getElementById('city').value.trim();
    const country = document.getElementById('country').value.trim();
    const generateBtn = document.getElementById('generateBtn');
    
    const isValid = city && country && selectedTheme;
    generateBtn.disabled = !isValid;
    
    return isValid;
}

// Generate map poster (create GitHub issue)
function generateMapPoster() {
    if (!validateForm()) {
        alert('Please fill in all required fields and select a theme.');
        return;
    }
    
    const city = document.getElementById('city').value.trim();
    const country = document.getElementById('country').value.trim();
    const distance = document.getElementById('distance').value;
    
    // Create issue body with exact schema
    const timestamp = new Date().toISOString();
    const userAgent = navigator.userAgent;
    
    const issueBody = `JOB: MAPTOPOSTER
city: ${city}
country: ${country}
theme: ${selectedTheme.theme}
distance: ${distance}
requested_at: ${timestamp}
user_agent: ${userAgent}`;
    
    const issueTitle = `Map Request: ${city}, ${country} (${selectedTheme.name})`;
    
    // Construct GitHub issue URL
    const issueUrl = `https://github.com/${GITHUB_REPO}/issues/new?` + 
        `title=${encodeURIComponent(issueTitle)}&` +
        `body=${encodeURIComponent(issueBody)}`;
    
    // Redirect to GitHub
    window.location.href = issueUrl;
}
