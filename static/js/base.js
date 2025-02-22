document.addEventListener('DOMContentLoaded', function() {
    const profileToggle = document.querySelector('.profile-toggle');
    const dropdownContent = document.querySelector('.profile-dropdown-content');

    if (profileToggle && dropdownContent) {
        // Toggle dropdown on click
        profileToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            dropdownContent.classList.toggle('show');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!dropdownContent.contains(e.target) && !profileToggle.contains(e.target)) {
                dropdownContent.classList.remove('show');
            }
        });

        // Make dropdown links clickable
        const dropdownLinks = dropdownContent.querySelectorAll('a');
        dropdownLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.stopPropagation();
                // Allow the link to work normally
            });
        });
    }
}); 