document.addEventListener('DOMContentLoaded', () => {
    
    // --- FEATURE: Geolocation Detection ---
    const detectLocationBtn = document.getElementById('detectLocationBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');

    if (detectLocationBtn) {
        detectLocationBtn.addEventListener('click', () => {
            if ("geolocation" in navigator) {
                // UI transition for loading state
                detectLocationBtn.style.display = 'none';
                loadingIndicator.style.display = 'block';

                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        // Execute GET request with coords instead of city name
                        window.location.href = `/result?lat=${lat}&lon=${lon}`;
                    },
                    (error) => {
                        // Handle user denied or other errors gracefully
                        let msg = "Error getting location.";
                        if(error.code === 1) msg = "Location access denied by user.";
                        if(error.code === 2) msg = "Network location unavailable.";
                        
                        alert(msg);
                        
                        // Revert UI to default
                        loadingIndicator.style.display = 'none';
                        detectLocationBtn.style.display = 'inline-flex';
                    },
                    {
                        enableHighAccuracy: false, // Standard fidelity to respond quicker
                        timeout: 10000,
                        maximumAge: 0
                    }
                );
            } else {
                alert("Geolocation is not supported by your browser");
            }
        });
    }

    // --- FEATURE: Load & Render Recent Searches (Local Storage) ---
    const recentSearchesContainer = document.getElementById('recentSearchesContainer');
    const recentSearchesList = document.getElementById('recentSearchesList');
    
    if (recentSearchesContainer && recentSearchesList) {
        try {
            const recent = JSON.parse(localStorage.getItem('recentSearches') || '[]');
            if (recent.length > 0) {
                recentSearchesContainer.style.display = 'block';
                recent.forEach(city => {
                    const tag = document.createElement('div');
                    tag.className = 'tag';
                    tag.innerHTML = `<i class="fa-solid fa-clock-rotate-left"></i> ${city}`;
                    tag.addEventListener('click', () => {
                        // Auto-fill and submit form
                        const cityInput = document.getElementById('cityInput');
                        cityInput.value = city;
                        // Add visual feedback to tag click
                        tag.style.transform = 'scale(0.95)';
                        document.getElementById('searchForm').submit();
                    });
                    recentSearchesList.appendChild(tag);
                });
            }
        } catch (e) {
            console.error("Local storage processing error:", e);
        }
    }

    // --- FEATURE: Form Validation & Client UX Handlers ---
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            const cityInput = document.getElementById('cityInput');
            
            // Validate input
            if (cityInput.value.trim() === '') {
                e.preventDefault();
                // Shakes animation class via JS instead of alert for better UX
                cityInput.style.border = '2px solid red';
                setTimeout(() => { cityInput.style.border = '2px solid #e2e8f0'; }, 1000);
            } else {
                // UI transition for form submit
                const submitBtn = document.getElementById('submitBtn');
                submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Analyzing...';
                // Note: we don't disable button here because some browsers skip form submit if button is disabled immediately
                submitBtn.style.opacity = '0.8';
                submitBtn.style.cursor = 'not-allowed';
            }
        });
    }
});
