document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');

    // Initialize FullCalendar
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth', // Default view
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: [
            // Example events (replace with dynamic data from Django)
            {
                title: 'Meeting with John Doe',
                start: '2023-10-10T10:00:00',
                end: '2023-10-10T11:00:00'
            },
            {
                title: 'Follow-up with Jane Smith',
                start: '2023-10-12T14:00:00',
                end: '2023-10-12T15:00:00'
            }
        ],
        editable: true, // Allow drag-and-drop
        selectable: true, // Allow date/time selection
        eventClick: function(info) {
            // Handle event click (e.g., open a modal with event details)
            alert('Event: ' + info.event.title);
        },
        dateClick: function(info) {
            // Handle date click (e.g., create a new event)
            alert('Clicked on: ' + info.dateStr);
        }
    });

    // Render the calendar
    calendar.render();

    // Modal elements
    const modal = document.getElementById('event-modal');
    const addEventBtn = document.getElementById('add-event');
    const closeBtn = document.querySelector('.close');
    const eventForm = document.getElementById('event-form');

    // Open modal
    addEventBtn.onclick = function() {
        modal.style.display = "block";
    }

    // Close modal
    closeBtn.onclick = function() {
        modal.style.display = "none";
    }

    // Close modal when clicking outside
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    // Handle form submission
    eventForm.onsubmit = async function(e) {
        e.preventDefault();
        
        const title = document.getElementById('event-title').value;
        const start = document.getElementById('event-start').value;
        const end = document.getElementById('event-end').value;
        const description = document.getElementById('event-description').value;

        try {
            // Send data to backend
            const response = await fetch('/api/events/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    title,
                    start,
                    end,
                    description
                })
            });

            if (response.ok) {
                // Get documents URL from form data attribute
                const documentsUrl = eventForm.dataset.documentsUrl;
                window.location.href = documentsUrl;
            } else {
                throw new Error('Failed to save event');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to save event. Please try again.');
        }

        // Close modal and reset form
        modal.style.display = "none";
        eventForm.reset();
    }

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

    // Form toggle functionality
    const toggleBtn = document.getElementById('toggleForm');
    const form = document.querySelector('.add-event-form');
    const container = document.querySelector('.calendar-container');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            form.classList.toggle('active');
            container.classList.toggle('form-visible');
            toggleBtn.innerHTML = form.classList.contains('active') ? 
                '<i class="fas fa-times"></i> Close Form' : 
                '<i class="fas fa-plus"></i> Add Event';
        });
    }
});
