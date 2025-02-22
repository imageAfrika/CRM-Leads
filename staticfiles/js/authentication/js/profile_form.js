document.addEventListener('DOMContentLoaded', function() {
    const avatarInput = document.getElementById('avatar');
    const avatarPreview = document.getElementById('avatarPreview');
    const togglePassword = document.querySelector('.toggle-password');
    const pinInput = document.getElementById('pin');

    // Handle avatar preview
    avatarInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                avatarPreview.innerHTML = `
                    <img src="${e.target.result}" alt="Profile Avatar" style="width: 100%; height: 100%; object-fit: cover;">
                `;
            }
            reader.readAsDataURL(file);
        }
    });

    // Toggle PIN visibility
    togglePassword.addEventListener('click', function() {
        const type = pinInput.getAttribute('type') === 'password' ? 'text' : 'password';
        pinInput.setAttribute('type', type);
        
        const icon = this.querySelector('i');
        icon.classList.toggle('fa-eye');
        icon.classList.toggle('fa-eye-slash');
    });

    // Ensure PIN contains only numbers
    pinInput.addEventListener('input', function(e) {
        this.value = this.value.replace(/\D/g, '');
    });
}); 