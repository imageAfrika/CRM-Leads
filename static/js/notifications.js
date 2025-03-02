/**
 * Custom notification system
 * Provides standardized notifications that automatically disappear after 3 seconds
 */

// Create notification container if it doesn't exist
function ensureNotificationContainer() {
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    return container;
}

/**
 * Show a notification message
 * @param {string} message - The message to display
 * @param {string} type - The type of notification: 'success', 'error', 'info', 'warning'
 * @param {number} duration - Duration in milliseconds before the notification disappears (default: 3000ms)
 */
function showNotification(message, type = 'info', duration = 3000) {
    const container = ensureNotificationContainer();
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.backgroundColor = getBackgroundColor(type);
    notification.style.color = '#fff';
    notification.style.padding = '12px 20px';
    notification.style.marginBottom = '10px';
    notification.style.borderRadius = '4px';
    notification.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
    notification.style.minWidth = '250px';
    notification.style.maxWidth = '400px';
    notification.style.opacity = '0';
    notification.style.transform = 'translateY(-20px)';
    notification.style.transition = 'opacity 0.3s, transform 0.3s';
    
    // Add close button
    const closeBtn = document.createElement('span');
    closeBtn.innerHTML = '&times;';
    closeBtn.style.float = 'right';
    closeBtn.style.cursor = 'pointer';
    closeBtn.style.marginLeft = '10px';
    closeBtn.onclick = function() {
        removeNotification(notification);
    };
    
    notification.appendChild(closeBtn);
    notification.appendChild(document.createTextNode(message));
    container.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateY(0)';
    }, 10);
    
    // Auto-remove after duration
    setTimeout(() => {
        removeNotification(notification);
    }, duration);
    
    return notification;
}

/**
 * Remove a notification with animation
 * @param {HTMLElement} notification - The notification element to remove
 */
function removeNotification(notification) {
    notification.style.opacity = '0';
    notification.style.transform = 'translateY(-20px)';
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

/**
 * Get background color based on notification type
 * @param {string} type - The type of notification
 * @returns {string} - The background color
 */
function getBackgroundColor(type) {
    switch (type) {
        case 'success':
            return '#28a745';
        case 'error':
            return '#dc3545';
        case 'warning':
            return '#ffc107';
        case 'info':
        default:
            return '#17a2b8';
    }
}

/**
 * Show a success notification
 * @param {string} message - The message to display
 * @param {number} duration - Duration in milliseconds (default: 3000ms)
 */
function showSuccess(message, duration = 3000) {
    return showNotification(message, 'success', duration);
}

/**
 * Show an error notification
 * @param {string} message - The message to display
 * @param {number} duration - Duration in milliseconds (default: 3000ms)
 */
function showError(message, duration = 3000) {
    return showNotification(message, 'error', duration);
}

/**
 * Show a warning notification
 * @param {string} message - The message to display
 * @param {number} duration - Duration in milliseconds (default: 3000ms)
 */
function showWarning(message, duration = 3000) {
    return showNotification(message, 'warning', duration);
}

/**
 * Show an info notification
 * @param {string} message - The message to display
 * @param {number} duration - Duration in milliseconds (default: 3000ms)
 */
function showInfo(message, duration = 3000) {
    return showNotification(message, 'info', duration);
}

/**
 * Override the default browser alert with our custom notification
 * @param {string} message - The message to display
 */
function customAlert(message) {
    showNotification(message, 'info', 3000);
    return true;
}

// Override the default alert if needed
// window.alert = customAlert; 