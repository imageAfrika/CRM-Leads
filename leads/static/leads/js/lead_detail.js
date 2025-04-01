document.addEventListener('DOMContentLoaded', function() {
    console.log("Lead detail script loaded");

    // Modal handling
    const modalTriggers = document.querySelectorAll('[data-modal-target]');
    const modalCloseTriggers = document.querySelectorAll('[data-modal-close]');
    
    console.log("Modal triggers found:", modalTriggers.length);
    modalTriggers.forEach(trigger => {
        console.log("Trigger for:", trigger.getAttribute('data-modal-target'));
    });
    
    // Open modal function
    function openModal(modalId) {
        console.log("Attempting to open modal:", modalId);
        const modal = document.getElementById(modalId);
        if (modal) {
            console.log("Modal found, adding show class");
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
            
            // Focus first input in modal
            setTimeout(() => {
                const firstInput = modal.querySelector('input, textarea');
                if (firstInput) {
                    firstInput.focus();
                }
            }, 100);
            
            // Add escape key listener
            document.addEventListener('keydown', closeModalOnEscape);
        } else {
            console.error("Modal not found:", modalId);
        }
    }
    
    // Close modal function
    function closeModal(modal) {
        console.log("Closing modal");
        if (modal) {
            modal.classList.remove('show');
            document.body.style.overflow = '';
            
            // Remove event listeners
            document.removeEventListener('keydown', closeModalOnEscape);
        }
    }
    
    // Close modal on escape key
    function closeModalOnEscape(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal-backdrop.show');
            if (openModal) closeModal(openModal);
        }
    }
    
    // Modal trigger event listeners
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const modalId = this.getAttribute('data-modal-target');
            console.log("Modal trigger clicked for:", modalId);
            openModal(modalId);
        });
    });
    
    // Modal close trigger event listeners
    modalCloseTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const modal = this.closest('.modal-backdrop');
            closeModal(modal);
        });
    });
    
    // Add click outside listener to all modals
    document.querySelectorAll('.modal-backdrop').forEach(modal => {
        modal.addEventListener('click', function(e) {
            // Only close if clicking the backdrop, not the modal content
            if (e.target === this) {
                closeModal(this);
            }
        });
    });

    // Add Note Form Submission
    const addNoteForm = document.getElementById('add-note-form');
    if (addNoteForm) {
        console.log("Note form found");
        addNoteForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log("Note form submitted");
            
            const formData = new FormData(this);
            const leadId = document.getElementById('lead-id').value;
            
            // Get CSRF token safely
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch(`/leads/leads/${leadId}/add-note/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log("Note submission response:", data);
                // Close modal and refresh notes section or add note dynamically
                if (data.success) {
                    const noteModal = document.getElementById('addNoteModal');
                    closeModal(noteModal);
                    
                    // Reload page to show the new note
                    window.location.reload();
                } else {
                    // Show errors
                    const errorContainer = document.getElementById('note-form-error');
                    if (errorContainer) {
                        errorContainer.textContent = data.errors ? Object.values(data.errors).join(', ') : 'Failed to add note';
                        errorContainer.classList.remove('d-none');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Show error message to user
                const errorContainer = document.getElementById('note-form-error');
                if (errorContainer) {
                    errorContainer.textContent = 'Failed to add note. Please try again.';
                    errorContainer.classList.remove('d-none');
                }
            });
        });
    } else {
        console.error("Note form not found");
    }
    
    // Add Document Form Submission
    const addDocumentForm = document.getElementById('add-document-form');
    if (addDocumentForm) {
        console.log("Document form found");
        addDocumentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log("Document form submitted");
            
            const formData = new FormData(this);
            const leadId = document.getElementById('lead-id').value;
            
            // Get CSRF token safely
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch(`/leads/leads/${leadId}/add-document/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log("Document submission response:", data);
                // Close modal and refresh documents section or add document dynamically
                if (data.success) {
                    const documentModal = document.getElementById('addDocumentModal');
                    closeModal(documentModal);
                    
                    // Reload page to show the new document
                    window.location.reload();
                } else {
                    // Show errors
                    const errorContainer = document.getElementById('document-form-error');
                    if (errorContainer) {
                        errorContainer.textContent = data.errors ? Object.values(data.errors).join(', ') : 'Failed to add document';
                        errorContainer.classList.remove('d-none');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Show error message to user
                const errorContainer = document.getElementById('document-form-error');
                if (errorContainer) {
                    errorContainer.textContent = 'Failed to add document. Please try again.';
                    errorContainer.classList.remove('d-none');
                }
            });
        });
    } else {
        console.error("Document form not found");
    }
    
    // File input enhancement
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            // Get file name and show it
            const fileName = this.value.split('\\').pop();
            if (fileName) {
                const fileNameDisplay = document.createElement('div');
                fileNameDisplay.className = 'selected-file';
                fileNameDisplay.innerHTML = `
                    <i class="fas fa-file"></i>
                    <span>${fileName}</span>
                `;
                
                // Remove previous selected file indicator if exists
                const previousDisplay = this.parentElement.querySelector('.selected-file');
                if (previousDisplay) {
                    previousDisplay.remove();
                }
                
                // Add new indicator
                this.parentElement.appendChild(fileNameDisplay);
            }
        });
    });
    
    // Add hover effects to cards
    const cards = document.querySelectorAll('.lead-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.classList.add('error');
                    
                    const errorMessage = document.createElement('div');
                    errorMessage.className = 'error-message';
                    errorMessage.textContent = 'This field is required';
                    
                    // Remove previous error messages
                    const previousErrors = field.parentElement.querySelectorAll('.error-message');
                    previousErrors.forEach(error => error.remove());
                    
                    field.parentElement.appendChild(errorMessage);
                } else {
                    field.classList.remove('error');
                    const previousErrors = field.parentElement.querySelectorAll('.error-message');
                    previousErrors.forEach(error => error.remove());
                }
            });
            
            if (!valid) {
                e.preventDefault();
            }
        });
    });
}); 