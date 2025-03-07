// Access Control App JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize date range pickers
    initializeDateRangePicker();
    
    // Initialize charts if they exist on the page
    initializeCharts();
    
    // Initialize dropdown toggles
    initializeDropdowns();
    
    // Initialize permission form handlers
    initializePermissionForms();
});

/**
 * Initialize date range picker for activity filtering
 */
function initializeDateRangePicker() {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const filterForm = document.getElementById('date-filter-form');
    
    if (!startDateInput || !endDateInput || !filterForm) return;
    
    // Set default date range (last 7 days)
    if (!startDateInput.value) {
        const defaultStartDate = new Date();
        defaultStartDate.setDate(defaultStartDate.getDate() - 7);
        startDateInput.value = formatDate(defaultStartDate);
    }
    
    if (!endDateInput.value) {
        const today = new Date();
        endDateInput.value = formatDate(today);
    }
    
    // Add event listener for form submission
    filterForm.addEventListener('submit', function(e) {
        // Validate date range
        const startDate = new Date(startDateInput.value);
        const endDate = new Date(endDateInput.value);
        
        if (startDate > endDate) {
            e.preventDefault();
            showAlert('Start date cannot be after end date', 'danger');
            return false;
        }
    });
}

/**
 * Format date as YYYY-MM-DD for input fields
 */
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

/**
 * Initialize charts for activity visualization
 */
function initializeCharts() {
    const activityChartCanvas = document.getElementById('activity-chart');
    if (!activityChartCanvas) return;
    
    // Get activity data from the data attribute
    const activityData = JSON.parse(activityChartCanvas.dataset.activities || '[]');
    
    // Prepare data for chart
    const labels = [];
    const datasets = {
        'user': [],
        'group': [],
        'permission': []
    };
    
    // Group activities by date and type
    const groupedData = {};
    
    activityData.forEach(activity => {
        const date = activity.timestamp.split('T')[0];
        if (!groupedData[date]) {
            groupedData[date] = {
                'user': 0,
                'group': 0,
                'permission': 0
            };
        }
        
        // Increment count based on activity type
        if (activity.target_type === 'user') {
            groupedData[date].user++;
        } else if (activity.target_type === 'group') {
            groupedData[date].group++;
        } else if (activity.target_type === 'permission') {
            groupedData[date].permission++;
        }
    });
    
    // Sort dates and prepare chart data
    const sortedDates = Object.keys(groupedData).sort();
    
    sortedDates.forEach(date => {
        labels.push(date);
        datasets.user.push(groupedData[date].user);
        datasets.group.push(groupedData[date].group);
        datasets.permission.push(groupedData[date].permission);
    });
    
    // Create chart
    const ctx = activityChartCanvas.getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'User Activities',
                    data: datasets.user,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    tension: 0.1
                },
                {
                    label: 'Group Activities',
                    data: datasets.group,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    tension: 0.1
                },
                {
                    label: 'Permission Activities',
                    data: datasets.permission,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 2,
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

/**
 * Initialize dropdown toggles
 */
function initializeDropdowns() {
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const dropdown = this.nextElementSibling;
            dropdown.classList.toggle('show');
            
            // Close other open dropdowns
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                if (menu !== dropdown) {
                    menu.classList.remove('show');
                }
            });
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.matches('.dropdown-toggle') && !e.target.closest('.dropdown-menu')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
}

/**
 * Initialize permission forms
 */
function initializePermissionForms() {
    const userPermissionForm = document.getElementById('user-permission-form');
    const groupPermissionForm = document.getElementById('group-permission-form');
    
    if (userPermissionForm) {
        userPermissionForm.addEventListener('submit', validatePermissionForm);
    }
    
    if (groupPermissionForm) {
        groupPermissionForm.addEventListener('submit', validatePermissionForm);
    }
}

/**
 * Validate permission form before submission
 */
function validatePermissionForm(e) {
    const form = e.target;
    const userOrGroupSelect = form.querySelector('select[name="user"]') || form.querySelector('select[name="group"]');
    const permissionSelect = form.querySelector('select[name="permission"]');
    
    if (!userOrGroupSelect.value) {
        e.preventDefault();
        showAlert('Please select a user or group', 'danger');
        return false;
    }
    
    if (!permissionSelect.value) {
        e.preventDefault();
        showAlert('Please select a permission', 'danger');
        return false;
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertsContainer = document.getElementById('alerts-container');
    if (!alertsContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    
    alert.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    `;
    
    alertsContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => {
            alertsContainer.removeChild(alert);
        }, 150);
    }, 5000);
    
    // Add click event for dismiss button
    const closeButton = alert.querySelector('.close');
    closeButton.addEventListener('click', function() {
        alert.classList.remove('show');
        setTimeout(() => {
            alertsContainer.removeChild(alert);
        }, 150);
    });
}

/**
 * Toggle sidebar on mobile
 */
function toggleSidebar() {
    const sidebar = document.querySelector('.access-control-sidebar');
    if (sidebar) {
        sidebar.classList.toggle('show-mobile');
    }
}

/**
 * Confirm action with modal
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Handle bulk permission operations
 */
function handleBulkOperation(operation) {
    const selectedItems = document.querySelectorAll('input[name="selected_items"]:checked');
    
    if (selectedItems.length === 0) {
        showAlert('Please select at least one item', 'warning');
        return;
    }
    
    const itemIds = Array.from(selectedItems).map(item => item.value);
    
    // Redirect to bulk operation page with selected IDs
    window.location.href = `/access-control/${operation}/?ids=${itemIds.join(',')}`;
}

/**
 * Toggle select all checkboxes
 */
function toggleSelectAll(source) {
    const checkboxes = document.querySelectorAll('input[name="selected_items"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = source.checked;
    });
} 