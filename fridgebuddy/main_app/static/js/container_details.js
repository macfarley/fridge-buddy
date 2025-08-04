/*
INTERACTIVE CONTAINER MANAGEMENT JAVASCRIPT

This script provides real-time interaction for managing food items within a container.
It handles batch operations, quantity adjustments, and provides live user feedback.

Key Features:
1. Batch Selection: Select multiple items for bulk operations
2. Quantity Management: Adjust quantities with immediate visual feedback
3. Live Counters: Real-time updates of selections and pending changes
4. Dynamic UI: Show/hide operation bars based on user actions

Data Structures:
- quantityChanges: Object tracking modified quantities {itemId: newQuantity}
- selectedItems: Set of selected item IDs for batch operations
*/

// =============================================================================
// GLOBAL STATE MANAGEMENT
// =============================================================================

// Track quantity changes for each item: {itemId: newQuantity}
// This allows users to make multiple changes before saving
let quantityChanges = {};

// Track selected items for batch operations using Set for efficient lookups
// Set automatically handles uniqueness and provides fast add/delete operations
let selectedItems = new Set();

// Current modal item IDs
let currentEditItemId = null;
let currentDeleteItemId = null;

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    initializeBulkSelection();
    initializeItemSelection();
});

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    initializeBulkSelection();
    initializeItemSelection();
    initializeActionButtons();
});

/**
 * Initialize action button event listeners
 */
function initializeActionButtons() {
    // Batch operations
    const batchMoveBtn = document.querySelector('[data-action="batch-move"]');
    if (batchMoveBtn) batchMoveBtn.addEventListener('click', batchMoveItems);
    
    const batchRemoveBtn = document.querySelector('[data-action="batch-remove"]');
    if (batchRemoveBtn) batchRemoveBtn.addEventListener('click', batchRemoveItems);
    
    const clearSelectionBtn = document.querySelector('[data-action="clear-selection"]');
    if (clearSelectionBtn) clearSelectionBtn.addEventListener('click', clearSelection);
    
    // Quantity changes
    const saveQuantitiesBtn = document.querySelector('[data-action="save-quantities"]');
    if (saveQuantitiesBtn) saveQuantitiesBtn.addEventListener('click', saveQuantityChanges);
    
    const resetQuantitiesBtn = document.querySelector('[data-action="reset-quantities"]');
    if (resetQuantitiesBtn) resetQuantitiesBtn.addEventListener('click', resetQuantities);
    
    // Quantity adjustment buttons
    document.querySelectorAll('[data-action="adjust-quantity"]').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            const change = parseInt(this.dataset.change);
            adjustQuantity(itemId, change);
        });
    });
    
    // Modal buttons
    document.querySelectorAll('[data-action="show-edit-modal"]').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            const itemName = this.dataset.itemName;
            const expirationDate = this.dataset.expirationDate;
            const quantity = this.dataset.quantity;
            showEditModal(itemId, itemName, expirationDate, quantity);
        });
    });
    
    document.querySelectorAll('[data-action="show-delete-modal"]').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            const itemName = this.dataset.itemName;
            const quantity = this.dataset.quantity;
            showDeleteModal(itemId, itemName, quantity);
        });
    });
    
    // Edit modal buttons
    document.querySelectorAll('[data-action="close-edit-modal"]').forEach(button => {
        button.addEventListener('click', closeEditModal);
    });
    
    const confirmEditBtn = document.querySelector('[data-action="confirm-edit"]');
    if (confirmEditBtn) confirmEditBtn.addEventListener('click', confirmEdit);
    
    // Delete modal buttons
    document.querySelectorAll('[data-action="close-delete-modal"]').forEach(button => {
        button.addEventListener('click', closeDeleteModal);
    });
    
    const confirmDeleteBtn = document.querySelector('[data-action="confirm-delete"]');
    if (confirmDeleteBtn) confirmDeleteBtn.addEventListener('click', confirmDelete);
}

// =============================================================================
// BULK SELECTION FUNCTIONALITY
// =============================================================================

/**
 * Initialize bulk selection functionality
 */
function initializeBulkSelection() {
    const selectAllCheckbox = document.getElementById('select-all');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.item-select');
            
            // Update all individual checkboxes to match the master checkbox
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
                
                // Update the selectedItems Set based on checkbox state
                if (this.checked) {
                    selectedItems.add(checkbox.dataset.itemId);
                } else {
                    selectedItems.delete(checkbox.dataset.itemId);
                }
            });
            
            // Update the UI to show/hide batch operations
            updateBatchOperations();
        });
    }
}

/**
 * Initialize individual item selection
 */
function initializeItemSelection() {
    document.querySelectorAll('.item-select').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            // Update selection state based on checkbox
            if (this.checked) {
                selectedItems.add(this.dataset.itemId);
            } else {
                selectedItems.delete(this.dataset.itemId);
            }
            
            // Update the UI to reflect current selection
            updateBatchOperations();
        });
    });
}

// =============================================================================
// DYNAMIC UI UPDATE FUNCTIONS
// =============================================================================

/**
 * UPDATE BATCH OPERATIONS VISIBILITY AND COUNTER
 * 
 * Shows/hides the batch operations bar based on selection state.
 * Updates the counter to show how many items are selected.
 * Provides immediate visual feedback to users about their selections.
 */
function updateBatchOperations() {
    const batchOps = document.getElementById('batch-operations');
    const selectedCount = document.getElementById('selected-count');
    
    if (selectedItems.size > 0) {
        // Show operations bar when items are selected
        batchOps.style.display = 'flex';
        selectedCount.textContent = selectedItems.size;
    } else {
        // Hide operations bar when no items are selected
        batchOps.style.display = 'none';
    }
}

/**
 * UPDATE QUANTITY CHANGES VISIBILITY AND COUNTER
 * 
 * Shows/hides the quantity changes bar based on pending modifications.
 * Updates the counter to show how many items have quantity changes.
 * Provides feedback about unsaved changes to prevent data loss.
 */
function updateQuantityChanges() {
    const quantityOps = document.getElementById('quantity-changes');
    const changesCount = document.getElementById('changes-count');
    const changeCount = Object.keys(quantityChanges).length;
    
    if (changeCount > 0) {
        // Show changes bar when there are pending modifications
        quantityOps.style.display = 'flex';
        changesCount.textContent = changeCount;
    } else {
        // Hide changes bar when no modifications are pending
        quantityOps.style.display = 'none';
    }
}

// =============================================================================
// QUANTITY MANAGEMENT FUNCTIONS
// =============================================================================

/**
 * ADJUST ITEM QUANTITY WITH +/- BUTTONS
 * 
 * Modifies the quantity of a specific item and tracks the change.
 * Provides immediate visual feedback and prevents negative quantities.
 * 
 * @param {number} itemId - The ID of the food item to modify
 * @param {number} change - The amount to change (+1 for increase, -1 for decrease)
 */
function adjustQuantity(itemId, change) {
    const qtyDisplay = document.getElementById(`qty-${itemId}`);
    const originalQty = parseInt(qtyDisplay.dataset.original);
    const currentQty = parseInt(qtyDisplay.textContent);
    
    // Calculate new quantity, ensuring it doesn't go below 0
    const newQty = Math.max(0, currentQty + change);
    
    // Update the visual display immediately
    qtyDisplay.textContent = newQty;
    
    // Track changes for batch saving
    if (newQty !== originalQty) {
        // Store the change if different from original
        quantityChanges[itemId] = newQty;
    } else {
        // Remove from changes if back to original value
        delete quantityChanges[itemId];
    }
    
    // Update the UI to show/hide the changes bar
    updateQuantityChanges();
}

// =============================================================================
// USER ACTION FUNCTIONS
// =============================================================================

/**
 * CLEAR ALL SELECTIONS
 * 
 * Resets all checkboxes and clears the selection state.
 * Provides a quick way to deselect all items.
 */
function clearSelection() {
    selectedItems.clear();
    
    // Uncheck all checkboxes
    document.querySelectorAll('.item-select').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    const selectAllCheckbox = document.getElementById('select-all');
    if (selectAllCheckbox) {
        selectAllCheckbox.checked = false;
    }
    
    // Update UI to hide batch operations
    updateBatchOperations();
}

/**
 * RESET ALL QUANTITY CHANGES
 * 
 * Reverts all quantity displays to their original values.
 * Clears the pending changes without saving to database.
 */
function resetQuantities() {
    // Revert each changed quantity to its original value
    Object.keys(quantityChanges).forEach(itemId => {
        const qtyDisplay = document.getElementById(`qty-${itemId}`);
        qtyDisplay.textContent = qtyDisplay.dataset.original;
    });
    
    // Clear the changes tracking
    quantityChanges = {};
    
    // Update UI to hide changes bar
    updateQuantityChanges();
}

// =============================================================================
// BATCH OPERATION FUNCTIONS
// =============================================================================

/**
 * BATCH MOVE SELECTED ITEMS TO ANOTHER CONTAINER
 * 
 * Moves all selected items to the chosen destination container.
 * Includes validation and user feedback.
 */
function batchMoveItems() {
    const targetContainer = document.getElementById('move-to-container').value;
    
    // Validate that a destination container is selected
    if (!targetContainer) {
        alert('Please select a container to move items to.');
        return;
    }
    
    const itemIds = Array.from(selectedItems);
    console.log('Moving items:', itemIds, 'to container:', targetContainer);
    
    // TODO: Replace with actual AJAX call to backend
    // Example AJAX implementation:
    /*
    fetch('/api/batch-move-items/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            item_ids: itemIds,
            target_container: targetContainer
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload(); // Refresh to show changes
        } else {
            alert('Error moving items: ' + data.error);
        }
    });
    */
    
    // Placeholder alert for demonstration
    alert(`Moving ${itemIds.length} items to container ${targetContainer}`);
}

/**
 * BATCH REMOVE SELECTED ITEMS
 * 
 * Removes all selected items from the container with confirmation.
 * Includes safety confirmation to prevent accidental deletions.
 */
function batchRemoveItems() {
    // Safety confirmation for destructive action
    if (!confirm(`Are you sure you want to remove ${selectedItems.size} items?`)) {
        return;
    }
    
    const itemIds = Array.from(selectedItems);
    console.log('Removing items:', itemIds);
    
    // TODO: Replace with actual AJAX call to backend
    // Similar to batch move, but for deletion
    
    // Placeholder alert for demonstration
    alert(`Removing ${itemIds.length} items`);
}

/**
 * SAVE ALL QUANTITY CHANGES TO DATABASE
 * 
 * Commits all pending quantity modifications to the backend.
 * Provides feedback on the number of changes being saved.
 */
function saveQuantityChanges() {
    console.log('Saving quantity changes:', quantityChanges);
    
    // TODO: Replace with actual AJAX call to backend
    /*
    fetch('/api/update-quantities/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            quantity_changes: quantityChanges
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update original values and clear changes
            Object.keys(quantityChanges).forEach(itemId => {
                const qtyDisplay = document.getElementById(`qty-${itemId}`);
                qtyDisplay.dataset.original = quantityChanges[itemId];
            });
            quantityChanges = {};
            updateQuantityChanges();
        } else {
            alert('Error saving changes: ' + data.error);
        }
    });
    */
    
    // Placeholder alert for demonstration
    alert(`Saving ${Object.keys(quantityChanges).length} quantity changes`);
}

// =============================================================================
// MODAL FUNCTIONALITY
// =============================================================================

/**
 * SHOW EDIT MODAL FOR FOOD ITEM
 * 
 * Opens the edit modal with current item data pre-filled
 */
function showEditModal(itemId, itemName, expirationDate, quantity) {
    currentEditItemId = itemId;
    
    document.getElementById('edit-item-name').textContent = itemName;
    document.getElementById('edit-expiration-date').value = expirationDate || '';
    document.getElementById('edit-quantity').value = quantity;
    
    document.getElementById('editModal').style.display = 'block';
}

/**
 * CLOSE EDIT MODAL
 */
function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
    currentEditItemId = null;
}

/**
 * CONFIRM EDIT CHANGES
 * 
 * Sends updated data to server and refreshes the page
 */
function confirmEdit() {
    if (!currentEditItemId) return;
    
    const expirationDate = document.getElementById('edit-expiration-date').value;
    const quantity = parseInt(document.getElementById('edit-quantity').value);
    
    const data = {
        item_id: currentEditItemId,
        expiration_date: expirationDate || null,
        quantity: quantity
    };
    
    // Show loading state
    const saveButton = document.querySelector('#editModal .btn-primary');
    const originalText = saveButton.textContent;
    saveButton.textContent = 'Saving...';
    saveButton.disabled = true;
    
    fetch(updateFoodItemUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showNotification(result.message, 'success');
            
            // Update the UI with new values
            const quantityDisplay = document.getElementById(`qty-${currentEditItemId}`);
            if (quantityDisplay) {
                quantityDisplay.textContent = result.quantity;
                quantityDisplay.dataset.original = result.quantity;
            }
            
            // Update expiration display and status class
            const itemCard = document.querySelector(`[data-item-id="${currentEditItemId}"]`);
            if (itemCard) {
                itemCard.className = `food-item-card ${result.status_class}`;
                
                // Update expiration text
                const expiryStatus = itemCard.querySelector('.expiry-status');
                if (expiryStatus && result.days_until_expiration !== null) {
                    let statusHtml = '';
                    if (result.days_until_expiration < 0) {
                        statusHtml = `<span class="expired">Expired ${Math.abs(result.days_until_expiration)} days ago</span>`;
                    } else if (result.days_until_expiration <= 3) {
                        statusHtml = `<span class="warning">Expires in ${result.days_until_expiration} days</span>`;
                    } else {
                        statusHtml = `<span class="fresh">${result.days_until_expiration} days remaining</span>`;
                    }
                    expiryStatus.innerHTML = statusHtml;
                }
            }
            
            closeEditModal();
        } else {
            alert('Error: ' + result.error);
        }
    })
    .catch(error => {
        console.error('Error updating item:', error);
        alert('An error occurred while updating the item');
    })
    .finally(() => {
        // Reset button state
        saveButton.textContent = originalText;
        saveButton.disabled = false;
    });
}

/**
 * SHOW DELETE MODAL FOR FOOD ITEM
 * 
 * Opens the delete modal with item details
 */
function showDeleteModal(itemId, itemName, quantity) {
    currentDeleteItemId = itemId;
    
    document.getElementById('delete-item-name').textContent = itemName;
    document.getElementById('delete-quantity').textContent = quantity;
    document.getElementById('add-to-shopping-checkbox').checked = true;
    
    document.getElementById('deleteModal').style.display = 'block';
}

/**
 * CLOSE DELETE MODAL
 */
function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
    currentDeleteItemId = null;
}

/**
 * CONFIRM DELETE ACTION
 * 
 * Deletes the item and optionally adds to shopping list
 */
function confirmDelete() {
    if (!currentDeleteItemId) return;
    
    const addToShopping = document.getElementById('add-to-shopping-checkbox').checked;
    
    const data = {
        item_id: currentDeleteItemId,
        add_to_shopping: addToShopping
    };
    
    // Show loading state
    const deleteButton = document.querySelector('#deleteModal .btn-danger');
    const originalText = deleteButton.textContent;
    deleteButton.textContent = 'Removing...';
    deleteButton.disabled = true;
    
    fetch(deleteFoodItemUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showNotification(result.message, 'success');
            
            // Remove item from UI
            const itemCard = document.querySelector(`[data-item-id="${currentDeleteItemId}"]`);
            if (itemCard) {
                itemCard.style.animation = 'fadeOut 0.3s ease-out';
                setTimeout(() => {
                    itemCard.remove();
                    
                    // Check if container is now empty
                    const remainingItems = document.querySelectorAll('.food-item-card');
                    if (remainingItems.length === 0) {
                        location.reload(); // Reload to show empty state
                    }
                }, 300);
            }
            
            // Update shopping counter if item was added to shopping list
            if (result.shopping_count && result.shopping_count > 0) {
                const navCounter = document.querySelector('.shopping-counter');
                if (navCounter) {
                    navCounter.textContent = result.shopping_count;
                }
            }
            
            closeDeleteModal();
        } else {
            alert('Error: ' + result.error);
        }
    })
    .catch(error => {
        console.error('Error deleting item:', error);
        alert('An error occurred while deleting the item');
    })
    .finally(() => {
        // Reset button state
        deleteButton.textContent = originalText;
        deleteButton.disabled = false;
    });
}

// =============================================================================
// EVENT LISTENERS
// =============================================================================

// Close modals when clicking outside
window.onclick = function(event) {
    const editModal = document.getElementById('editModal');
    const deleteModal = document.getElementById('deleteModal');
    
    if (event.target === editModal) {
        closeEditModal();
    } else if (event.target === deleteModal) {
        closeDeleteModal();
    }
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

// Helper function to show notifications
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

/**
 * GET CSRF TOKEN FOR DJANGO AJAX REQUESTS
 * 
 * Utility function to extract CSRF token from cookies for secure AJAX calls.
 * Required for POST requests to Django backend.
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
