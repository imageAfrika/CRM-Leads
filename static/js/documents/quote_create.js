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

    // Preview button functionality
    const previewButton = document.getElementById('preview-button');
    const previewSection = document.querySelector('.preview-section');
    
    if (previewButton && previewSection) {
        previewButton.addEventListener('click', function() {
            // Toggle preview section visibility
            if (window.innerWidth <= 768) {
                // On mobile, toggle visibility
                if (previewSection.style.display === 'none' || !previewSection.style.display) {
                    previewSection.style.display = 'block';
                    previewButton.textContent = 'Hide Preview';
                } else {
                    previewSection.style.display = 'none';
                    previewButton.textContent = 'Show Preview';
                }
            }
            
            // Scroll to preview section
            previewSection.scrollIntoView({ behavior: 'smooth' });
        });
        
        // Initialize preview section visibility for mobile
        if (window.innerWidth <= 768) {
            previewSection.style.display = 'none';
            previewButton.textContent = 'Show Preview';
        }
    }

    // Preview functionality
    window.previewQuote = async function() {
        // Validate form data
        if (!document.getElementById('client').value) {
            alert('Please select a client.');
            return;
        }
        
        // Collect items
        const items = [];
        document.querySelectorAll('.quote-item').forEach(item => {
            items.push({
                description: item.querySelector('[name="items[][description]"]').value || 'No description',
                quantity: parseFloat(item.querySelector('[name="items[][quantity]"]').value) || 1,
                unit_price: parseFloat(item.querySelector('[name="items[][unit_price]"]').value) || 0,
                discount: parseFloat(item.querySelector('[name="items[][discount]"]').value) || 0
            });
        });
        
        // Set default values for required fields
        const today = new Date();
        const oneMonth = new Date();
        oneMonth.setMonth(oneMonth.getMonth() + 1);
        
        // Format date as YYYY-MM-DD
        const formatDate = (date) => {
            const year = date.getFullYear();
            const month = (date.getMonth() + 1).toString().padStart(2, '0');
            const day = date.getDate().toString().padStart(2, '0');
            return `${year}-${month}-${day}`;
        };
        
        // Collect form data
        const formData = {
            client_id: document.getElementById('client').value,
            quote_number: document.getElementById('quote_number').value || 'PREVIEW-001',
            title: document.getElementById('quote_title').value || 'Quote Preview',
            description: document.getElementById('description').value || '',
            valid_until: document.getElementById('valid_until').value || formatDate(oneMonth),
            terms: document.getElementById('terms').value || 'Standard terms and conditions apply.',
            tax_rate: document.getElementById('tax_rate').value || '16',
            subtotal: document.getElementById('subtotal').value || '0',
            tax_amount: document.getElementById('tax_amount').value || '0',
            total_amount: document.getElementById('total_amount').value || '0',
            items: items.length > 0 ? items : [{
                description: 'Sample Item',
                quantity: 1,
                unit_price: 0,
                discount: 0
            }]
        };

        try {
            // Submit the form data for preview
            const response = await fetch('/documents/quote/preview/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            if (data.success) {
                // Redirect to the preview page
                window.location.href = data.preview_url;
            } else {
                alert('Error creating preview: ' + data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to create preview. Please try again.');
        }
    };

    // Add form submission handling
    quoteForm.addEventListener('submit', function(event) {
        event.preventDefault();
        console.log('Form submitted');
        
        // Validate form
        if (!document.getElementById('client').value) {
            alert('Please select a client.');
            return;
        }
        
        if (!document.getElementById('quote_title').value) {
            alert('Please enter a quote title.');
            return;
        }
        
        // Collect items data
        const items = [];
        document.querySelectorAll('.quote-item').forEach(item => {
            const description = item.querySelector('[name="items[][description]"]').value;
            const quantity = item.querySelector('[name="items[][quantity]"]').value;
            const unitPrice = item.querySelector('[name="items[][unit_price]"]').value;
            const discount = item.querySelector('[name="items[][discount]"]').value || 0;
            
            // Skip empty items
            if (description && quantity && unitPrice) {
                items.push({
                    description: description,
                    quantity: quantity,
                    unit_price: unitPrice,
                    discount: discount
                });
            }
        });
        
        if (items.length === 0) {
            alert('Please add at least one item to the quote.');
            return;
        }
        
        console.log('Collected items:', items);
        
        // Create the form data to submit
        const formData = new FormData(quoteForm);
        
        // Remove the individual item fields from the form data
        for (const [key, value] of [...formData.entries()]) {
            if (key.startsWith('items[')) {
                formData.delete(key);
            }
        }
        
        // Add items as a JSON string
        formData.set('items', JSON.stringify(items));
        
        // Log the form data for debugging
        console.log('Form data:');
        for (let [key, value] of formData.entries()) {
            console.log(`${key}: ${value}`);
        }
        
        // Submit the form
        fetch(quoteForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            console.log('Response status:', response.status);
            if (response.ok) {
                // Check if it's a redirect or a JSON response
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    return response.json().then(data => {
                        if (data.success) {
                            window.location.href = data.redirect_url;
                        } else {
                            throw new Error(data.error || 'An error occurred');
                        }
                    });
                } else {
                    // Handle redirect
                    window.location.href = response.url;
                }
            } else {
                return response.text().then(text => {
                    try {
                        const data = JSON.parse(text);
                        throw new Error(data.error || 'An error occurred');
                    } catch (e) {
                        throw new Error('Failed to create quote');
                    }
                });
            }
        })
        .catch(error => {
            console.error('Error submitting form:', error);
            alert('Error: ' + error.message);
        });
    });
}); 