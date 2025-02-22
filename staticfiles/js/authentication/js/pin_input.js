document.addEventListener('DOMContentLoaded', function() {
    const pinDisplay = document.getElementById('pin-display');
    const keypadButtons = document.querySelectorAll('.keypad-btn');
    const togglePassword = document.querySelector('.toggle-password');
    
    // Handle keypad input
    keypadButtons.forEach(button => {
        button.addEventListener('mousedown', function(e) {
            e.preventDefault(); // Prevent double input
            
            if (this.classList.contains('clear-btn')) {
                pinDisplay.value = '';
            } else if (!this.classList.contains('enter-btn')) {
                if (pinDisplay.value.length < 4) {
                    pinDisplay.value += this.dataset.value;
                }
            }
        });
    });

    // Toggle password visibility
    togglePassword.addEventListener('mousedown', function(e) {
        e.preventDefault();
        const type = pinDisplay.getAttribute('type') === 'password' ? 'text' : 'password';
        pinDisplay.setAttribute('type', type);
        
        // Toggle icon
        const icon = this.querySelector('i');
        icon.classList.toggle('fa-eye');
        icon.classList.toggle('fa-eye-slash');
    });

    // Prevent keyboard input on the PIN display
    pinDisplay.addEventListener('keydown', function(e) {
        e.preventDefault();
    });

    // Clear messages after 5 seconds
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
});

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateY(0);
            opacity: 1;
        }
        to {
            transform: translateY(-10px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style); 