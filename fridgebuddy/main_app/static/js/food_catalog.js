/*
FOOD CATALOG INTERACTIVE FUNCTIONALITY

This script handles category expansion, batch operations, and individual item actions
for the food catalog page.

Key Features:
1. Category Toggle: Expand/collapse food categories with smooth animations
2. Batch Selection: Select multiple items for bulk add to shopping list
3. Individual Actions: Add items to specific containers
4. Live Feedback: Real-time counters and status updates
*/

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    initializeCategoryToggles();
    initializeBatchOperations();
    initializeIndividualActions();
});

// =============================================================================
// CATEGORY MANAGEMENT
// =============================================================================

/**
 * Initialize category toggle functionality
 */
function initializeCategoryToggles() {
    // Add click handlers to category headers
    document.querySelectorAll('.category-header').forEach(header => {
        header.addEventListener('click', function() {
            const category = this.dataset.category;
            if (category) {
                toggleCategory(category);
            }
        });
    });
}

/**
 * Toggle the visibility of a category's food list with smooth animation
 * @param {string} category - The category identifier
 */
function toggleCategory(category) {
    const list = document.getElementById(`category-${category}`);
    const header = document.querySelector(`[data-category="${category}"]`);
    
    if (!list || !header) return;
    
    const arrow = header.querySelector('.category-arrow');
    const isExpanded = header.getAttribute('data-expanded') === 'true';
    
    if (isExpanded) {
        // Collapse
        list.setAttribute('data-animating', 'hide');
        setTimeout(() => {
            list.style.display = 'none';
            list.removeAttribute('data-animating');
        }, 300);
        header.setAttribute('data-expanded', 'false');
        if (arrow) arrow.textContent = '▶';
    } else {
        // Expand
        list.style.display = 'block';
        list.setAttribute('data-animating', 'show');
        setTimeout(() => {
            list.removeAttribute('data-animating');
        }, 300);
        header.setAttribute('data-expanded', 'true');
        if (arrow) arrow.textContent = '▼';
    }
}

// =============================================================================
// BATCH OPERATIONS
// =============================================================================

/**
 * Initialize batch operations functionality
 */
function initializeBatchOperations() {
    // Initialize checkbox listeners
    document.querySelectorAll('.food-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectedCount);
    });
    
    // Initialize batch add button
    const batchAddBtn = document.getElementById('batch-add-btn');
    if (batchAddBtn) {
        batchAddBtn.addEventListener('click', handleBatchAdd);
    }
    
    // Set initial count
    updateSelectedCount();
}

/**
 * Update the count of selected items
 */
function updateSelectedCount() {
    const selectedCount = document.querySelectorAll('.food-checkbox:checked').length;
    const countElement = document.getElementById('selected-count');
    if (countElement) {
        countElement.textContent = `${selectedCount} item${selectedCount !== 1 ? 's' : ''} selected`;
    }
}

/**
 * Handle batch add to shopping list
 */
async function handleBatchAdd() {
    const selectedCheckboxes = document.querySelectorAll('.food-checkbox:checked');
    const selectedFoodIds = Array.from(selectedCheckboxes).map(checkbox => checkbox.dataset.foodId);
    
    if (selectedFoodIds.length === 0) {
        alert('Please select at least one food item to add to your shopping list.');
        return;
    }

    // Disable button during request
    const button = document.getElementById('batch-add-btn');
    const originalText = button.textContent;
    button.disabled = true;
    button.textContent = 'Adding...';

    try {
        // Make AJAX call to add items to shopping list
        const response = await fetch(batchAddToShoppingUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                food_ids: selectedFoodIds
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show success message
            showNotification(data.message, 'success');
            
            // Uncheck all checkboxes
            selectedCheckboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
            
            updateSelectedCount();
            
            // Reload page to show updated shopping list and counter
            setTimeout(() => {
                window.location.reload();
            }, 1000);
            
        } else {
            throw new Error(data.error || 'Failed to add items');
        }
        
    } catch (error) {
        console.error('Error adding to shopping list:', error);
        showNotification('Error adding items to shopping list: ' + error.message, 'error');
    } finally {
        button.textContent = originalText;
        button.disabled = false;
    }
}

// =============================================================================
// INDIVIDUAL ACTIONS
// =============================================================================

/**
 * Initialize individual "Add to Container" buttons
 */
function initializeIndividualActions() {
    document.querySelectorAll('.add-to-container-btn').forEach(button => {
        button.addEventListener('click', async function() {
            const foodId = this.dataset.foodId;
            const containerSelect = document.querySelector(`.container-select[data-food-id="${foodId}"]`);
            const containerId = containerSelect.value;
            
            if (!containerId) {
                alert('Please select a list first.');
                return;
            }
            
            await handleAddToContainer(this, foodId, containerId);
        });
    });
}

/**
 * Handle adding individual item to container
 * @param {HTMLElement} button - The clicked button
 * @param {string} foodId - The food item ID
 * @param {string} containerId - The target container ID
 */
async function handleAddToContainer(button, foodId, containerId) {
    // Disable button during request
    button.disabled = true;
    const originalText = button.textContent;
    button.textContent = 'Adding...';
    
    try {
        // Make AJAX call to add food to container
        const response = await fetch(addFoodToContainerUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                food_id: foodId,
                container_id: containerId,
                quantity: 1
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show success feedback
            button.textContent = '✅ Added!';
            button.style.background = '#28a745';
            
            // Show success message with details
            const message = data.message + (data.created ? '' : ` (Quantity: ${data.new_quantity})`);
            showNotification(message, 'success');
            
            // If added to shopping list, reload page to update counter and sidebar
            const containerSelect = document.querySelector(`.container-select[data-food-id="${foodId}"]`);
            const selectedOption = containerSelect.options[containerSelect.selectedIndex];
            if (selectedOption.textContent.includes('🛒')) {
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            }
            
        } else {
            throw new Error(data.error || 'Failed to add item');
        }
        
    } catch (error) {
        console.error('Error adding to container:', error);
        showNotification('Error adding item to list: ' + error.message, 'error');
        button.style.background = '#dc3545';
        button.textContent = 'Error';
    } finally {
        // Reset button after 2 seconds
        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '';
            button.disabled = false;
        }, 2000);
    }
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Show notification message
 * @param {string} message - The message to display
 * @param {string} type - The notification type (success, error, info)
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    let backgroundColor;
    switch (type) {
        case 'success':
            backgroundColor = 'var(--primary-color)';
            break;
        case 'error':
            backgroundColor = 'var(--danger-color)';
            break;
        default:
            backgroundColor = '#007bff';
    }
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${backgroundColor};
        color: white;
        padding: 1rem;
        border-radius: var(--border-radius);
        z-index: 1001;
        animation: slideInNotification 0.3s ease-out;
        max-width: 300px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutNotification 0.3s ease-out';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

/**
 * Get CSRF token from cookies for Django AJAX requests
 * @param {string} name - Cookie name
 * @returns {string|null} Cookie value
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// =============================================================================
// CSS ANIMATIONS FOR NOTIFICATIONS
// =============================================================================

// Add notification animation styles if they don't exist
if (!document.getElementById('catalog-notification-styles')) {
    const style = document.createElement('style');
    style.id = 'catalog-notification-styles';
    style.textContent = `
        @keyframes slideInNotification {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideOutNotification {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
}
