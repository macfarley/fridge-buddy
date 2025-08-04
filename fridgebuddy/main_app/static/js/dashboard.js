/*
DASHBOARD INTERACTIVE FUNCTIONALITY

Handles profile panel toggle and form interactions for the dashboard page.
*/

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    initializeProfilePanel();
});

// =============================================================================
// PROFILE PANEL MANAGEMENT
// =============================================================================

/**
 * Initialize profile panel functionality
 */
function initializeProfilePanel() {
    const editButton = document.querySelector('.edit-profile-btn');
    const cancelButton = document.querySelector('[onclick="toggleProfilePanel()"]');
    
    if (editButton) {
        editButton.addEventListener('click', toggleProfilePanel);
        editButton.removeAttribute('onclick'); // Remove inline onclick
    }
    
    if (cancelButton) {
        cancelButton.addEventListener('click', toggleProfilePanel);
        cancelButton.removeAttribute('onclick'); // Remove inline onclick
    }
}

/**
 * Toggle the visibility of the profile update panel
 */
function toggleProfilePanel() {
    const panel = document.getElementById('profile-update-panel');
    if (panel) {
        panel.classList.toggle('show');
        
        // Focus on first input when panel opens
        if (panel.classList.contains('show')) {
            setTimeout(() => {
                const firstInput = panel.querySelector('input');
                if (firstInput) {
                    firstInput.focus();
                }
            }, 300);
        }
    }
}

// =============================================================================
// FORM ENHANCEMENTS
// =============================================================================

/**
 * Add form validation and enhancement
 */
function initializeFormEnhancements() {
    const form = document.querySelector('#profile-update-panel form');
    if (form) {
        form.addEventListener('submit', function(e) {
            // Add any client-side validation here if needed
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Updating...';
                
                // Re-enable button after a delay in case of validation errors
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.textContent = 'Update Profile';
                }, 3000);
            }
        });
    }
}

// Initialize form enhancements when DOM is ready
document.addEventListener('DOMContentLoaded', initializeFormEnhancements);
