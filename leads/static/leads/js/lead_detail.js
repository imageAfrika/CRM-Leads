document.addEventListener('DOMContentLoaded', function() {
    // Modal handling
    const modalTriggers = document.querySelectorAll('[data-modal-target]');
    const modalCloseTriggers = document.querySelectorAll('[data-modal-close]');
    
    // Open modal function
    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
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
            
            // Add click outside listener
            modal.addEventListener('click', closeModalOnClickOutside);
        }
    }
    
    // Close modal function
    function closeModal(modal) {
        if (modal) {
            modal.classList.remove('show');
            document.body.style.overflow = '';
            
            // Remove event listeners
            document.removeEventListener('keydown', closeModalOnEscape);
            modal.removeEventListener('click', closeModalOnClickOutside);
        }
    }
    
    // Close modal on escape key
    function closeModalOnEscape(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal-backdrop.show');
            if (openModal) closeModal(openModal);
        }
    }
    
    // Close modal when clicking outside
    function closeModalOnClickOutside(e) {
        if (e.target === e.currentTarget) {
            closeModal(e.target);
        }
    }
    
    // Add click listeners to modal triggers
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            const modalId = trigger.getAttribute('data-modal-target');
            openModal(modalId);
        });
    });
    
    // Add click listeners to modal close buttons
    modalCloseTriggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            const modal = trigger.closest('.modal-backdrop');
            closeModal(modal);
        });
    });
    
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