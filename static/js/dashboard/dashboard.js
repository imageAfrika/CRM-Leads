document.addEventListener('DOMContentLoaded', function() {
    const miniCalendarEl = document.getElementById('miniCalendar');
    if (miniCalendarEl) {
        const miniCalendar = new FullCalendar.Calendar(miniCalendarEl, {
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next',
                center: 'title',
                right: 'today'
            },
            height: 'auto',
            events: [], // You can populate this with your events
            dayMaxEvents: 2, // Limit number of events shown per day
            eventDisplay: 'block',
            displayEventTime: false,
        });
        miniCalendar.render();
    }

    // Quick Add Event Form Handler
    const quickEventForm = document.getElementById('quickEventForm');
    if (quickEventForm) {
        quickEventForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const title = document.getElementById('quickEventTitle').value;
            const start = document.getElementById('quickEventStart').value;
            
            // Here you would typically send this data to your backend
            console.log('Quick Event:', { title, start });
            
            // Clear form
            quickEventForm.reset();
        });
    }
}); 