/*
SHOPPING LIST PAGE JAVASCRIPT

This JavaScript file handles the interactive functionality for the shopping list page.
It focuses on client-side interactions that cannot be easily handled server-side.

Key Responsibilities:
1. Modal interactions (open/close/submit)
2. Container content loading and display
3. Real-time UI updates after AJAX calls
4. Client-side form validation
5. User interface animations and feedback

Note: Batch operations and form submissions are handled via Django forms
where possible to reduce JavaScript complexity.
*/

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

/**
 * Initialize all event listeners
 */
function initializeEventListeners() {
    // Clear selection button
    const clearSelectionBtn = document.querySelector('[data-action="clear-selection"]');
    if (clearSelectionBtn) {
        clearSelectionBtn.addEventListener('click', clearSelection);
    }
    
    // Move item buttons
    document.querySelectorAll('[data-action="show-move-modal"]').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            const itemName = this.dataset.itemName;
            const quantity = this.dataset.quantity;
            showMoveModal(itemId, itemName, quantity);
        });
    });
    
    // Modal close buttons
    document.querySelectorAll('[data-action="close-move-modal"]').forEach(button => {
        button.addEventListener('click', closeMoveModal);
    });
    
    // Confirm move button
    const confirmMoveBtn = document.querySelector('[data-action="confirm-move"]');
    if (confirmMoveBtn) {
        confirmMoveBtn.addEventListener('click', confirmMove);
    }
}

// =============================================================================
// GLOBAL STATE MANAGEMENT
// =============================================================================

let currentItemData = null;
let selectedContainerData = null;

// =============================================================================
// CONTAINER CONTENT LOADING
// =============================================================================

/**
 * Load container contents when container is selected
 * This provides real-time preview of selected container
 */
function loadContainerContents() {
    const select = document.getElementById('container-select');
    const selectedOption = select.options[select.selectedIndex];
    const containerId = select.value;
    
    if (!containerId) {
        document.getElementById('container-contents').innerHTML = `
            <div class="empty-container">
                <h3>Select a container</h3>
                <p>Choose a container from the dropdown to see its contents</p>
            </div>`;
        document.getElementById('container-title').textContent = '📦 Select Container';
        document.getElementById('container-count').textContent = '0';
        return;
    }
    
    const containerName = selectedOption.dataset.name;
    const containerType = selectedOption.dataset.type;
    
    // Update panel header
    document.getElementById('container-title').textContent = `📦 ${containerName}`;
    
    // Store selected container data for modal use
    selectedContainerData = {
        id: containerId,
        name: containerName,
        type: containerType
    };
    
    // Fetch container contents via existing Django view
    fetch(`/my-lists/${containerId}/`)
        .then(response => response.text())
        .then(html => {
            // Parse the response to extract container items
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const items = doc.querySelectorAll('.food-item-card');
            
            let containerHtml = '';
            let itemCount = 0;
            
            if (items.length > 0) {
                items.forEach(item => {
                    const nameElement = item.querySelector('.food-item-header h3');
                    const quantityElement = item.querySelector('.quantity-display');
                    const expirationElements = item.querySelectorAll('.expiry-status span');
                    
                    if (nameElement && quantityElement) {
                        const name = nameElement.textContent.trim();
                        const quantity = quantityElement.textContent.trim();
                        
                        let expirationHtml = '';
                        if (expirationElements.length > 0) {
                            const expirationElement = expirationElements[0];
                            const expiration = expirationElement.textContent.trim();
                            const expirationClass = expirationElement.className;
                            expirationHtml = `<div class="expiration-info ${expirationClass}">${expiration}</div>`;
                        }
                        
                        containerHtml += `
                            <div class="container-item">
                                <div class="item-info">
                                    <div class="item-name">${name}</div>
                                    ${expirationHtml}
                                </div>
                                <div class="item-quantity">${quantity}</div>
                            </div>`;
                        itemCount++;
                    }
                });
            } else {
                containerHtml = `
                    <div class="empty-container">
                        <h3>Empty ${containerName}</h3>
                        <p>No items in this container yet</p>
                    </div>`;
            }
            
            document.getElementById('container-contents').innerHTML = containerHtml;
            document.getElementById('container-count').textContent = itemCount;
        })
        .catch(error => {
            console.error('Error loading container contents:', error);
            document.getElementById('container-contents').innerHTML = `
                <div class="empty-container">
                    <h3>Error loading container</h3>
                    <p>Unable to load container contents</p>
                </div>`;
        });
}

// =============================================================================
// MODAL FUNCTIONALITY
// =============================================================================

/**
 * Show move modal for individual item
 * Pre-fills modal with item and container information
 */
function showMoveModal(itemId, itemName, quantity) {
    if (!selectedContainerData) {
        alert('Please select a container first');
        return;
    }
    
    currentItemData = {
        id: itemId,
        name: itemName,
        quantity: quantity
    };
    
    document.getElementById('modal-item-name').textContent = itemName;
    document.getElementById('modal-quantity').textContent = quantity;
    document.getElementById('modal-container-name').textContent = selectedContainerData.name;
    
    // Calculate and show default expiration info
    updateDefaultExpirationInfo();
    
    // Show modal
    document.getElementById('moveModal').style.display = 'block';
}

/**
 * Update default expiration info based on container type
 * Provides user guidance on automatic expiration calculation
 */
function updateDefaultExpirationInfo() {
    if (!selectedContainerData) return;
    
    const infoDiv = document.getElementById('default-expiration-info');
    const textSpan = document.getElementById('default-expiration-text');
    
    let defaultText = '';
    if (selectedContainerData.type === 'FREEZER') {
        defaultText = 'Extended expiration (frozen storage)';
    } else if (selectedContainerData.type === 'FRIDGE') {
        defaultText = 'Standard refrigerated expiration';
    } else if (selectedContainerData.type === 'PANTRY') {
        defaultText = 'Room temperature storage expiration';
    }
    
    textSpan.textContent = defaultText;
    infoDiv.style.display = defaultText ? 'block' : 'none';
}

/**
 * Close move modal and reset state
 */
function closeMoveModal() {
    document.getElementById('moveModal').style.display = 'none';
    document.getElementById('expiration-date').value = '';
    currentItemData = null;
}

/**
 * Confirm move action via AJAX
 * Handles the individual item move functionality
 */
function confirmMove() {
    if (!currentItemData || !selectedContainerData) {
        alert('Missing required data');
        return;
    }
    
    const expirationDate = document.getElementById('expiration-date').value;
    
    const data = {
        item_id: currentItemData.id,
        container_id: selectedContainerData.id,
        quantity: currentItemData.quantity,
        expiration_date: expirationDate || null
    };
    
    // Show loading state
    const moveButton = document.querySelector('.modal-actions .btn-primary');
    const originalText = moveButton.textContent;
    moveButton.textContent = 'Moving...';
    moveButton.disabled = true;
    
    fetch(moveToContainerUrl, {  // URL will be provided by template
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            // Remove item from shopping list display
            const itemElement = document.querySelector(`[data-item-id="${currentItemData.id}"]`);
            if (itemElement) {
                itemElement.style.animation = 'fadeOut 0.3s ease-out';
                setTimeout(() => {
                    itemElement.remove();
                    
                    // Update shopping list count
                    const remainingCount = document.querySelectorAll('.shopping-item').length;
                    if (remainingCount === 0) {
                        location.reload(); // Reload to show empty state
                    } else {
                        updateItemCounts(remainingCount);
                    }
                    
                    // Update shopping counter in nav
                    updateShoppingCounter(result.shopping_count);
                }, 300);
            }
            
            // Refresh container contents
            loadContainerContents();
            
            // Close modal
            closeMoveModal();
            
            // Show success message
            showNotification(result.message, 'success');
        } else {
            alert('Error: ' + result.error);
        }
    })
    .catch(error => {
        console.error('Error moving item:', error);
        alert('An error occurred while moving the item');
    })
    .finally(() => {
        // Reset button state
        moveButton.textContent = originalText;
        moveButton.disabled = false;
    });
}

// =============================================================================
// UI UPDATE UTILITIES
// =============================================================================

/**
 * Update item count displays throughout the page
 */
function updateItemCounts(count) {
    const itemCountElement = document.querySelector('.item-count');
    if (itemCountElement) {
        itemCountElement.textContent = `${count} item${count !== 1 ? 's' : ''}`;
    }
    
    const badge = document.querySelector('.shopping-panel .badge');
    if (badge) {
        badge.textContent = count;
    }
}

/**
 * Update shopping counter in navigation
 */
function updateShoppingCounter(count) {
    const navCounter = document.querySelector('.shopping-counter');
    if (navCounter) {
        navCounter.textContent = count;
    }
}

/**
 * Show notification messages to user
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? 'var(--primary-color)' : 'var(--danger-color)'};
        color: white;
        padding: 1rem;
        border-radius: var(--border-radius);
        z-index: 1001;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// =============================================================================
// EVENT HANDLERS
// =============================================================================

/**
 * Close modal when clicking outside
 */
window.onclick = function(event) {
    const modal = document.getElementById('moveModal');
    if (event.target === modal) {
        closeMoveModal();
    }
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Get CSRF token for Django AJAX requests
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
// INITIALIZATION
// =============================================================================

// Initialize page when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Any initialization code can go here
    console.log('Shopping list page initialized');
});
