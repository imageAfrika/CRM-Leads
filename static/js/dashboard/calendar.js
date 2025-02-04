
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
    });
