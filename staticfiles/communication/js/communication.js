document.addEventListener('DOMContentLoaded', function() {
    // Utility Functions
    function showNotification(message, type = 'info') {
        const notificationContainer = document.getElementById('notification-container');
        if (!notificationContainer) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.style.position = 'fixed';
            container.style.top = '20px';
            container.style.right = '20px';
            container.style.zIndex = '1000';
            document.body.appendChild(container);
        }

        const notification = document.createElement('div');
        notification.classList.add('communication-notification', `communication-notification-${type}`);
        notification.textContent = message;
        notification.style.backgroundColor = type === 'success' ? '#28a745' : 
                                             type === 'error' ? '#dc3545' : 
                                             type === 'warning' ? '#ffc107' : '#17a2b8';
        notification.style.color = 'white';
        notification.style.padding = '10px 15px';
        notification.style.borderRadius = '5px';
        notification.style.marginBottom = '10px';
        notification.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';

        document.getElementById('notification-container').appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Email Functionality
    const emailInbox = document.querySelector('.email-inbox');
    if (emailInbox) {
        emailInbox.addEventListener('click', function(event) {
            const emailItem = event.target.closest('.email-list-item');
            if (emailItem) {
                const emailId = emailItem.dataset.emailId;
                window.location.href = `/communication/email/view/${emailId}/`;
            }
        });

        // Email Compose Functionality
        const emailComposeForm = document.getElementById('email-compose-form');
        if (emailComposeForm) {
            emailComposeForm.addEventListener('submit', function(event) {
                event.preventDefault();
                const formData = new FormData(emailComposeForm);

                fetch('/communication/email/compose/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        showNotification('Email sent successfully!', 'success');
                        emailComposeForm.reset();
                    } else {
                        showNotification(data.message || 'Failed to send email', 'error');
                    }
                })
                .catch(error => {
                    showNotification('An error occurred while sending email', 'error');
                    console.error('Error:', error);
                });
            });
        }
    }

    // Contact Management
    const contactList = document.querySelector('.contact-list');
    if (contactList) {
        contactList.addEventListener('click', function(event) {
            const contactCard = event.target.closest('.contact-card');
            if (contactCard) {
                const contactId = contactCard.dataset.contactId;
                window.location.href = `/communication/contacts/edit/${contactId}/`;
            }
        });

        // Contact Search and Filter
        const contactSearchInput = document.getElementById('contact-search');
        if (contactSearchInput) {
            contactSearchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                const contactCards = document.querySelectorAll('.contact-card');

                contactCards.forEach(card => {
                    const contactName = card.querySelector('.contact-name').textContent.toLowerCase();
                    const contactEmail = card.querySelector('.contact-email').textContent.toLowerCase();

                    if (contactName.includes(searchTerm) || contactEmail.includes(searchTerm)) {
                        card.style.display = 'flex';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        }
    }

    // Calendar Event Interactions
    const calendarContainer = document.querySelector('.calendar-container');
    if (calendarContainer) {
        calendarContainer.addEventListener('click', function(event) {
            const eventItem = event.target.closest('.event-list-item');
            if (eventItem) {
                const eventId = eventItem.dataset.eventId;
                window.location.href = `/communication/calendar/event/edit/${eventId}/`;
            }
        });

        // Calendar Event Modal
        const createEventBtn = document.getElementById('create-event-btn');
        const eventModal = document.getElementById('event-modal');
        const eventForm = document.getElementById('event-form');

        if (createEventBtn && eventModal && eventForm) {
            createEventBtn.addEventListener('click', function() {
                eventModal.classList.add('show');
                eventModal.style.display = 'block';
            });

            eventForm.addEventListener('submit', function(event) {
                event.preventDefault();
                const formData = new FormData(eventForm);

                fetch('/communication/calendar/event/create/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        showNotification('Event created successfully!', 'success');
                        eventForm.reset();
                        eventModal.classList.remove('show');
                        eventModal.style.display = 'none';
                        // Optionally refresh the calendar view
                    } else {
                        showNotification(data.message || 'Failed to create event', 'error');
                    }
                })
                .catch(error => {
                    showNotification('An error occurred while creating event', 'error');
                    console.error('Error:', error);
                });
            });
        }
    }

    // Messaging Functionality
    const messagingContainer = document.querySelector('.messaging-container');
    if (messagingContainer) {
        const messageForm = messagingContainer.querySelector('form');
        const messageInput = messageForm.querySelector('input[type="text"]');
        const messageList = messagingContainer.querySelector('.message-list');
        const serviceSelect = document.getElementById('message-service');

        messageForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const message = messageInput.value.trim();
            const service = serviceSelect.value;
            
            if (message) {
                fetch('/communication/messages/send/', {
                    method: 'POST',
                    body: JSON.stringify({
                        message: message,
                        service: service
                    }),
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Create new message bubble
                        const messageBubble = document.createElement('div');
                        messageBubble.classList.add('message-bubble', 'sent');
                        messageBubble.textContent = message;
                        messageList.appendChild(messageBubble);
                        
                        // Reset input
                        messageInput.value = '';
                        showNotification(`Message sent via ${service}!`, 'success');
                    } else {
                        showNotification(data.message || 'Failed to send message', 'error');
                    }
                })
                .catch(error => {
                    showNotification('An error occurred while sending message', 'error');
                    console.error('Error:', error);
                });
            }
        });
    }

    // Notification Management
    const notificationList = document.querySelector('.notification-list');
    if (notificationList) {
        notificationList.addEventListener('click', function(event) {
            const markReadBtn = event.target.closest('.mark-read-btn');
            if (markReadBtn) {
                const notificationId = markReadBtn.dataset.notificationId;
                
                fetch(`/communication/notifications/mark-read/${notificationId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        const notificationItem = markReadBtn.closest('.notification-item');
                        notificationItem.classList.remove('unread');
                        markReadBtn.remove();
                        showNotification('Notification marked as read', 'info');
                    } else {
                        showNotification(data.message || 'Failed to mark notification', 'error');
                    }
                })
                .catch(error => {
                    showNotification('An error occurred', 'error');
                    console.error('Error:', error);
                });
            }
        });
    }

    // Sidebar Active State Management
    const sidebarLinks = document.querySelectorAll('.communication-app .sidebar-link');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function() {
            sidebarLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Generic Search and Filter Functionality
    const searchInputs = document.querySelectorAll('.communication-search');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const container = this.closest('.communication-app');
            const items = container.querySelectorAll('.list-group-item, .table-row');
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                item.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    });

    // Tooltips and Popovers Initialization (requires Bootstrap)
    if (window.bootstrap && window.bootstrap.Tooltip) {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }

    // Modal Handling
    const modalTriggers = document.querySelectorAll('[data-modal-target]');
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const targetModalId = this.getAttribute('data-modal-target');
            const targetModal = document.getElementById(targetModalId);
            
            if (targetModal) {
                const modal = new bootstrap.Modal(targetModal);
                modal.show();
            }
        });
    });

    // Attachment Preview
    const attachmentInputs = document.querySelectorAll('input[type="file"]');
    attachmentInputs.forEach(input => {
        input.addEventListener('change', function() {
            const previewContainer = this.closest('.attachment-group').querySelector('.attachment-preview');
            previewContainer.innerHTML = ''; // Clear previous previews

            Array.from(this.files).forEach(file => {
                const fileItem = document.createElement('div');
                fileItem.classList.add('attachment-item');
                fileItem.innerHTML = `
                    <i class="fas fa-file"></i>
                    <span>${file.name}</span>
                    <small>${(file.size / 1024).toFixed(2)} KB</small>
                `;
                previewContainer.appendChild(fileItem);
            });
        });
    });

    // Helper function to get CSRF token
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
});
