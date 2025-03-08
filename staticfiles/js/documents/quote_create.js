document.addEventListener('DOMContentLoaded', async function() {
    // Get the quote number from the server
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
    const taxRateInput = document.getElementById('tax_rate');
    
    // Format number as currency
    function formatCurrency(number) {
        return new Intl.NumberFormat('en-KE', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(number);
    }
    
    // Update preview when form fields change
    function updatePreview() {
        // Update client
        const clientSelect = document.getElementById('client');
        if (clientSelect.selectedIndex > 0) {
            const clientName = clientSelect.options[clientSelect.selectedIndex].text;
            document.getElementById('preview-client').textContent = clientName;
            // Here you would ideally fetch client details from your backend
            // For now we'll use placeholder data
            document.getElementById('preview-client-address').textContent = 'Client Address';
            document.getElementById('preview-client-contact').textContent = 'client@example.com | +254 7XX XXX XXX';
        } else {
            document.getElementById('preview-client').textContent = '-';
            document.getElementById('preview-client-address').textContent = '-';
            document.getElementById('preview-client-contact').textContent = '-';
        }

        // Update quote number
        const quoteNumber = document.getElementById('quote_number').value;
        document.getElementById('preview-quote-number').textContent = quoteNumber || '-';

        // Update quote title and description
        const quoteTitle = document.getElementById('quote_title').value;
        document.getElementById('preview-title').textContent = quoteTitle || '-';
        
        const description = document.getElementById('description').value;
        document.getElementById('preview-description').textContent = description || '';

        // Update valid until date
        const validUntil = document.getElementById('valid_until').value;
        if (validUntil) {
            const formattedDate = new Date(validUntil).toLocaleDateString('en-US', {
                month: 'long',
                day: 'numeric',
                year: 'numeric'
            });
            document.getElementById('preview-valid-until').textContent = formattedDate;
        } else {
            document.getElementById('preview-valid-until').textContent = '-';
        }

        // Update tax rate
        const taxRate = parseFloat(taxRateInput.value) || 16;
        document.getElementById('preview-tax-rate').textContent = taxRate;

        // Update terms
        const terms = document.getElementById('terms').value;
        if (terms) {
            // Split terms by new lines and create paragraphs
            const termsHtml = terms.split('\n')
                .filter(line => line.trim().length > 0)
                .map(line => `<p>${line}</p>`)
                .join('');
            document.getElementById('preview-terms').innerHTML = termsHtml;
        } else {
            document.getElementById('preview-terms').innerHTML = '<p>-</p>';
        }

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
                <td>KES ${formatCurrency(unitPrice)}</td>
                <td>${discount}%</td>
                <td>KES ${formatCurrency(itemTotal)}</td>
            `;
            tbody.appendChild(tr);
        });

        // Update totals
        const taxRate = parseFloat(taxRateInput.value) || 16;
        const tax = subtotal * (taxRate / 100);
        const total = subtotal + tax;

        document.getElementById('preview-subtotal').textContent = `KES ${formatCurrency(subtotal)}`;
        document.getElementById('preview-tax').textContent = `KES ${formatCurrency(tax)}`;
        document.getElementById('preview-total').textContent = `KES ${formatCurrency(total)}`;
        
        // Update hidden fields for form submission
        document.getElementById('subtotal').value = subtotal.toFixed(2);
        document.getElementById('tax_amount').value = tax.toFixed(2);
        document.getElementById('total_amount').value = total.toFixed(2);
    }

    // Add new item row
    addItemBtn.addEventListener('click', function() {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'quote-item';
        itemDiv.innerHTML = `
            <label>Description</label>
            <input type="text" name="items[][description]" placeholder="Item description" required>
            
            <div class="numeric-fields">
                <div>
                    <label>Quantity</label>
                    <input type="number" name="items[][quantity]" min="1" placeholder="Qty" required>
                </div>
                
                <div>
                    <label>Unit Price (KES)</label>
                    <input type="number" name="items[][unit_price]" min="0" step="0.01" placeholder="0.00" required>
                </div>
                
                <div>
                    <label>Discount %</label>
                    <input type="number" name="items[][discount]" min="0" max="100" placeholder="0" value="0">
                </div>
            </div>
            
            <button type="button" class="remove-item">Remove Item</button>
        `;
        quoteItems.appendChild(itemDiv);

        // Add change event listeners to new inputs
        itemDiv.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', updatePreview);
        });
        
        // Focus on the new description field
        itemDiv.querySelector('[name="items[][description]"]').focus();
        
        // Update preview
        updatePreview();
    });
    
    // Remove item row
    quoteItems.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-item')) {
            // Don't remove if it's the last item
            if (document.querySelectorAll('.quote-item').length > 1) {
                e.target.closest('.quote-item').remove();
                updatePreview();
            } else {
                alert('At least one item is required.');
            }
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
        
        // Validate form
        const formValid = this.checkValidity();
        if (!formValid) {
            this.reportValidity();
            return;
        }
        
        // Collect items
        const items = [];
        document.querySelectorAll('.quote-item').forEach(item => {
            items.push({
                description: item.querySelector('[name="items[][description]"]').value,
                quantity: parseFloat(item.querySelector('[name="items[][quantity]"]').value),
                unit_price: parseFloat(item.querySelector('[name="items[][unit_price]"]').value),
                discount: parseFloat(item.querySelector('[name="items[][discount]"]').value) || 0
            });
        });
        
        // Collect form data
        const formData = {
            client_id: document.getElementById('client').value,
            quote_number: document.getElementById('quote_number').value,
            title: document.getElementById('quote_title').value,
            description: document.getElementById('description').value,
            valid_until: document.getElementById('valid_until').value,
            terms: document.getElementById('terms').value,
            tax_rate: document.getElementById('tax_rate').value,
            subtotal: document.getElementById('subtotal').value,
            tax_amount: document.getElementById('tax_amount').value,
            total_amount: document.getElementById('total_amount').value,
            items: items
        };

        try {
            // Show loading state
            const submitButton = quoteForm.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Processing...';
            submitButton.disabled = true;
            
            // Submit the form data
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
                // Reset button state
                submitButton.textContent = originalText;
                submitButton.disabled = false;
                
                // Show error message
                alert('Error creating quote: ' + data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to create quote. Please try again.');
            
            // Reset button state
            const submitButton = quoteForm.querySelector('button[type="submit"]');
            submitButton.textContent = 'Generate Quote';
            submitButton.disabled = false;
        }
    });
}); 