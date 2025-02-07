document.addEventListener('DOMContentLoaded', async function() {
    // Add this at the beginning of your DOMContentLoaded handler
    try {
        const quoteNumberUrl = document.getElementById('quote-form').dataset.quoteNumberUrl;
        const response = await fetch(quoteNumberUrl);
        const data = await response.json();
        document.getElementById('quote_number').value = data.quote_number;
        document.getElementById('preview-quote-number').textContent = data.quote_number;
    } catch (error) {
        console.error('Error fetching quote number:', error);
    }

    const quoteForm = document.getElementById('quote-form');
    const addItemBtn = document.getElementById('add-item');
    const quoteItems = document.getElementById('quote-items');
    
    // Update preview when form fields change
    function updatePreview() {
        // Update client
        const clientSelect = document.getElementById('client');
        const clientName = clientSelect.options[clientSelect.selectedIndex].text;
        document.getElementById('preview-client').textContent = clientName;

        // Update quote number
        const quoteNumber = document.getElementById('quote_number').value;
        document.getElementById('preview-quote-number').textContent = quoteNumber || '-';

        // Update quote title
        const quoteTitle = document.getElementById('quote_title').value;
        document.getElementById('preview-title').textContent = quoteTitle || '-';

        // Update terms
        const terms = document.getElementById('terms').value;
        document.getElementById('preview-terms').textContent = terms || '-';

        // Update items and calculations
        updateItems();
    }

    // Update items table and calculations
    function updateItems() {
        const tbody = document.getElementById('preview-items');
        tbody.innerHTML = '';
        let subtotal = 0;

        // Get all quote items
        const items = document.querySelectorAll('.quote-item');
        items.forEach(item => {
            const description = item.querySelector('[name="items[][description]"]').value;
            const quantity = parseFloat(item.querySelector('[name="items[][quantity]"]').value) || 0;
            const unitPrice = parseFloat(item.querySelector('[name="items[][unit_price]"]').value) || 0;
            const discount = parseFloat(item.querySelector('[name="items[][discount]"]').value) || 0;
            
            const itemTotal = quantity * unitPrice * (1 - discount/100);
            subtotal += itemTotal;

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${description || '-'}</td>
                <td>${quantity || 0}</td>
                <td>$${unitPrice.toFixed(2)}</td>
                <td>${discount}%</td>
                <td>$${itemTotal.toFixed(2)}</td>
            `;
            tbody.appendChild(tr);
        });

        // Update totals
        const tax = subtotal * 0.16;
        const total = subtotal + tax;

        document.getElementById('preview-subtotal').textContent = `$${subtotal.toFixed(2)}`;
        document.getElementById('preview-tax').textContent = `$${tax.toFixed(2)}`;
        document.getElementById('preview-total').textContent = `$${total.toFixed(2)}`;
    }

    // Add new item row
    addItemBtn.addEventListener('click', function() {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'quote-item';
        itemDiv.innerHTML = `
            <label>Description</label>
            <input type="text" name="items[][description]" placeholder="Description" required>
            
            <div class="numeric-fields">
                <div>
                    <label>Quantity</label>
                    <input type="number" name="items[][quantity]" placeholder="Quantity" required>
                </div>
                
                <div>
                    <label>Unit Price</label>
                    <input type="number" name="items[][unit_price]" placeholder="Unit Price" required>
                </div>
                
                <div>
                    <label>Discount %</label>
                    <input type="number" name="items[][discount]" placeholder="Discount %" required>
                </div>
            </div>
            
            <button type="button" class="remove-item">Remove</button>
        `;
        quoteItems.appendChild(itemDiv);

        // Add change event listeners to new inputs
        itemDiv.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', updatePreview);
        });
    });
    
    // Remove item row
    quoteItems.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-item')) {
            e.target.parentElement.remove();
            updatePreview();
        }
    });

    // Add change event listeners to all form inputs
    quoteForm.querySelectorAll('input, select, textarea').forEach(input => {
        input.addEventListener('input', updatePreview);
    });
    
    // Initial preview update
    updatePreview();

    // Handle form submission
    quoteForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Collect form data
        const formData = {
            client_id: document.getElementById('client').value,
            quote_number: document.getElementById('quote_number').value,
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            subtotal: document.getElementById('subtotal').value,
            tax_rate: document.getElementById('tax_rate').value,
            tax_amount: document.getElementById('tax_amount').value,
            total_amount: document.getElementById('total_amount').value,
            valid_until: document.getElementById('valid_until').value,
            terms: document.getElementById('terms').value
        };

        try {
            const response = await fetch('/documents/quote/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                alert('Error creating quote: ' + data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to create quote. Please try again.');
        }
    });
}); 