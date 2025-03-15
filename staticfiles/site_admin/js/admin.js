document.addEventListener('DOMContentLoaded', function() {
    console.log('Site Admin JS initialized');
    
    // Initialize all components
    initAlerts();
    initToggles();
    initSearch();
    initSort();
    initPermissionCheckboxes();
});

/**
 * Initialize alert messages with auto-dismiss and close buttons
 */
function initAlerts() {
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            fadeOut(alert);
        });
    }, 5000);

    // Close button for alerts
    document.querySelectorAll('.close-alert').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const alert = this.parentElement;
            fadeOut(alert);
        });
    });
}

/**
 * Fade out element and remove it
 */
function fadeOut(element) {
    if (!element) return;
    
    let opacity = 1;
    const timer = setInterval(function() {
        if (opacity <= 0.1) {
            clearInterval(timer);
            element.style.display = 'none';
            element.remove();
        }
        element.style.opacity = opacity;
        opacity -= 0.1;
    }, 50);
}

/**
 * Initialize toggle switches for enable/disable functionality
 */
function initToggles() {
    const toggles = document.querySelectorAll('.permission-toggle');
    if (!toggles.length) return;

    toggles.forEach(function(toggle) {
        toggle.addEventListener('change', function() {
            const userId = this.dataset.userId;
            const viewId = this.dataset.viewId;
            const action = this.checked ? 'grant' : 'revoke';
            const checkbox = this;
            
            // Show loading state
            checkbox.disabled = true;
            
            // Prepare data for POST request
            const data = new FormData();
            data.append('user_id', userId);
            data.append('view_id', viewId);
            data.append('action', action);
            
            // Send request to update permission
            fetch(window.location.href, {
                method: 'POST',
                body: data,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                checkbox.disabled = false;
                
                if (data.status === 'success') {
                    showAlert(data.message, 'success');
                } else {
                    // Revert the checkbox if there was an error
                    checkbox.checked = !checkbox.checked;
                    showAlert(data.message || 'An error occurred', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                checkbox.disabled = false;
                checkbox.checked = !checkbox.checked;
                showAlert('An error occurred while updating the permission', 'danger');
            });
        });
    });
}

/**
 * Initialize search functionality
 */
function initSearch() {
    const searchInput = document.getElementById('searchInput');
    const clearButton = document.getElementById('clearSearch');
    if (!searchInput || !clearButton) return;

    // Search as you type
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase();
        
        if (document.getElementById('permissionsGrid')) {
            // For permissions grid
            const rows = document.querySelectorAll('.user-row');
            const headers = document.querySelectorAll('.view-column');
            
            // Show/hide rows based on username
            rows.forEach(function(row) {
                const username = row.querySelector('.user-info').textContent.toLowerCase();
                row.style.display = username.includes(query) ? '' : 'none';
            });
            
            // Show/hide columns based on view name
            headers.forEach(function(header, index) {
                const viewName = header.textContent.trim().toLowerCase();
                const showColumn = viewName.includes(query);
                
                // Set visibility for the header
                header.style.display = showColumn ? '' : 'none';
                
                // Set visibility for cells in this column
                const cells = document.querySelectorAll(`.permission-cell:nth-child(${index + 2})`);
                cells.forEach(cell => {
                    cell.style.display = showColumn ? '' : 'none';
                });
            });
        } else if (document.querySelector('.data-table')) {
            // For regular tables
            const rows = document.querySelectorAll('.data-table tbody tr');
            
            rows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        }
    });
    
    // Clear search
    clearButton.addEventListener('click', function() {
        searchInput.value = '';
        
        // Reset visibility
        if (document.getElementById('permissionsGrid')) {
            document.querySelectorAll('.user-row').forEach(row => {
                row.style.display = '';
            });
            document.querySelectorAll('.view-column, .permission-cell').forEach(el => {
                el.style.display = '';
            });
        } else if (document.querySelector('.data-table')) {
            document.querySelectorAll('.data-table tbody tr').forEach(row => {
                row.style.display = '';
            });
        }
    });
}

/**
 * Initialize table column sorting
 */
function initSort() {
    const sortableHeaders = document.querySelectorAll('.sortable');
    if (!sortableHeaders.length) return;
    
    sortableHeaders.forEach(function(header) {
        header.addEventListener('click', function() {
            const sortBy = this.dataset.sort;
            const currentSortDir = this.classList.contains('sorted-asc') ? 'desc' : 'asc';
            
            // Update URL with sort parameters
            const url = new URL(window.location.href);
            url.searchParams.set('sort_by', sortBy);
            url.searchParams.set('sort_dir', currentSortDir);
            
            window.location.href = url.toString();
        });
    });
}

/**
 * Initialize permission checkboxes
 */
function initPermissionCheckboxes() {
    const permissionCheckboxes = document.querySelectorAll('.permission-checkbox');
    
    permissionCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const userId = this.getAttribute('data-user');
            const viewId = this.getAttribute('data-view');
            const isChecked = this.checked;
            const csrfToken = getCookie('csrftoken');
            
            // Show loading indicator
            this.classList.add('loading');
            
            fetch('/site-admin/update-permission/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    user_id: userId,
                    view_id: viewId,
                    is_active: isChecked
                })
            })
            .then(response => response.json())
            .then(data => {
                // Remove loading indicator
                this.classList.remove('loading');
                
                if (data.success) {
                    showAlert('success', data.message);
                } else {
                    showAlert('error', data.message);
                    // Revert the checkbox if there was an error
                    this.checked = !isChecked;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Remove loading indicator
                this.classList.remove('loading');
                showAlert('error', 'An error occurred. Please try again.');
                // Revert the checkbox if there was an error
                this.checked = !isChecked;
            });
        });
    });
}

/**
 * Show a dynamic alert message
 */
function showAlert(message, type = 'info') {
    const alertsContainer = document.getElementById('alerts');
    if (!alertsContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="close-alert">&times;</button>
    `;
    
    alertsContainer.appendChild(alert);
    
    // Add close functionality
    alert.querySelector('.close-alert').addEventListener('click', function() {
        fadeOut(alert);
    });
    
    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        fadeOut(alert);
    }, 5000);
}

/**
 * Get cookie by name (for CSRF token)
 * @param {string} name - The cookie name
 * @return {string} The cookie value
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