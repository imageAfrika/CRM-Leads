// CRM Leads - Main JavaScript File

// Execute when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize subscription plan selection
    initSubscriptionPlanSelection();
    
    // Initialize form validation
    initFormValidation();
    
    // Initialize smooth scrolling for anchor links
    initSmoothScrolling();
    
    // Initialize navbar scroll behavior
    initNavbarScroll();
});

// Initialize subscription plan selection
function initSubscriptionPlanSelection() {
    const subscriptionCards = document.querySelectorAll('.subscription-card');
    if (subscriptionCards.length === 0) return;
    
    subscriptionCards.forEach(card => {
        card.addEventListener('click', function() {
            // Remove selected class from all cards
            subscriptionCards.forEach(c => {
                c.classList.remove('selected');
            });
            
            // Add selected class to this card
            this.classList.add('selected');
            
            // Update hidden input value
            const planInput = document.getElementById('subscription_plan');
            if (planInput) {
                planInput.value = this.dataset.plan;
            }
        });
    });
}

// Initialize form validation
function initFormValidation() {
    const registrationForm = document.getElementById('registration-form');
    if (!registrationForm) return;
    
    registrationForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form fields
        const password = document.getElementById('password');
        const confirmPassword = document.getElementById('password_confirm');
        
        // Simple validation
        let valid = true;
        
        // Check passwords match
        if (password && confirmPassword && password.value !== confirmPassword.value) {
            showError(confirmPassword, 'Passwords do not match');
            valid = false;
        }
        
        // If valid, show success modal (in a real app, this would submit to server)
        if (valid) {
            const companyName = document.getElementById('company_name');
            if (companyName) {
                const domain = companyName.value.toLowerCase().replace(/[^a-z0-9]/g, '') + '.crm-leads.com';
                const tenantDomain = document.getElementById('tenant-domain');
                if (tenantDomain) {
                    tenantDomain.textContent = domain;
                }
            }
            
            const successModal = new bootstrap.Modal(document.getElementById('successModal'));
            successModal.show();
            
            // Set a timeout to submit the form after the modal is shown
            setTimeout(function() {
                // Add a hidden input for the plan if it's in the URL
                const urlParams = new URLSearchParams(window.location.search);
                const plan = urlParams.get('plan');
                if (plan) {
                    let planInput = document.getElementById('url_plan');
                    if (!planInput) {
                        planInput = document.createElement('input');
                        planInput.type = 'hidden';
                        planInput.id = 'url_plan';
                        planInput.name = 'url_plan';
                        registrationForm.appendChild(planInput);
                    }
                    planInput.value = plan;
                }
                
                // Submit the form
                // registrationForm.submit();
                
                // For demo purposes, redirect to dashboard after 2 seconds
                setTimeout(function() {
                    window.location.href = '/dashboard/';
                }, 2000);
            }, 1000);
        }
    });
}

// Show error message for form validation
function showError(inputElement, message) {
    // Clear previous error
    clearError(inputElement);
    
    // Create error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    // Add error class to input
    inputElement.classList.add('is-invalid');
    
    // Insert error message after input
    inputElement.parentNode.appendChild(errorDiv);
}

// Clear error message
function clearError(inputElement) {
    inputElement.classList.remove('is-invalid');
    
    const existingError = inputElement.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
}

// Initialize smooth scrolling for anchor links
function initSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]:not([href="#"])');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // Adjust for navbar height
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Initialize navbar scroll behavior
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });
} 