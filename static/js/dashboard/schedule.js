document.addEventListener('DOMContentLoaded', function() {
    // Initialize Calendar
    const calendarEl = document.getElementById('schedule-calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: [], // You'll populate this with your events
        eventClick: function(info) {
            // Handle event click
            console.log('Event clicked:', info.event);
        },
        dateClick: function(info) {
            // Handle date click
            openModal();
            document.getElementById('event-start').value = info.dateStr;
        }
    });
    calendar.render();

    // Modal Handling
    const modal = document.getElementById('event-modal');
    const addEventBtn = document.getElementById('add-event');
    const closeModal = document.querySelector('.close-modal');
    const cancelBtn = document.getElementById('cancel-event');
    const eventForm = document.getElementById('event-form');

    function openModal() {
        modal.style.display = 'block';
    }

    function closeModalHandler() {
        modal.style.display = 'none';
        eventForm.reset();
    }

    addEventBtn.addEventListener('click', openModal);
    closeModal.addEventListener('click', closeModalHandler);
    cancelBtn.addEventListener('click', closeModalHandler);

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeModalHandler();
        }
    });

    // Form Handling
    eventForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const eventData = {
            title: document.getElementById('event-title').value,
            start: document.getElementById('event-start').value,
            end: document.getElementById('event-end').value,
            type: document.getElementById('event-type').value,
            location: document.getElementById('event-location').value,
            description: document.getElementById('event-description').value
        };

        // Here you would typically send this data to your backend
        console.log('New event:', eventData);
        
        // Add event to calendar
        calendar.addEvent({
            title: eventData.title,
            start: eventData.start,
            end: eventData.end,
            className: eventData.type
        });

        closeModalHandler();
    });

    // Filter Handling
    const typeFilter = document.getElementById('event-type-filter');
    typeFilter.addEventListener('change', function(e) {
        const filterValue = e.target.value;
        const eventCards = document.querySelectorAll('.event-card');
        
        eventCards.forEach(card => {
            if (filterValue === 'all' || card.classList.contains(filterValue)) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
    });
}); 