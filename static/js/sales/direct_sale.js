document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('sale-form');
    const itemsList = document.getElementById('items-list');
    const addItemBtn = document.getElementById('add-item');
    const notification = document.getElementById('notification');
    const TAX_RATE = 15; // 15%

    function formatCurrency(number) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(number);
    }

    function formatNumber(number) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(number);
    }

    function formatPercent(number) {
        return new Intl.NumberFormat('en-US', {
            style: 'percent',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(number/100);
    }

    function parseCurrency(value) {
        if (!value) return 0;
        return parseFloat(value.replace(/[$,\s]/g, '')) || 0;
    }

    function showNotification(message, isError = false) {
        notification.textContent = message;
        notification.style.backgroundColor = isError ? '#dc2626' : '#16a34a';
        notification.style.display = 'block';
        setTimeout(() => notification.style.display = 'none', 3000);
    }

    function validateInput(input) {
        const value = parseCurrency(input.value);
        const errorDiv = input.parentElement.querySelector('.error-message');
        
        if (input.hasAttribute('required') && !input.value.trim()) {
            input.classList.add('error');
            errorDiv.textContent = input.dataset.error;
            errorDiv.style.display = 'block';
            return false;
        }

        if (input.name === 'unit_price[]' && value <= 0) {
            input.classList.add('error');
            errorDiv.textContent = 'Price must be greater than 0';
            errorDiv.style.display = 'block';
            return false;
        }

        if (input.name === 'quantity[]' && value < 1) {
            input.classList.add('error');
            errorDiv.textContent = 'Quantity must be at least 1';
            errorDiv.style.display = 'block';
            return false;
        }

        input.classList.remove('error');
        errorDiv.style.display = 'none';
        return true;
    }

    function calculateItemTotal(item) {
        const quantity = parseCurrency(item.querySelector('input[name="quantity[]"]').value);
        const unitPrice = parseCurrency(item.querySelector('input[name="unit_price[]"]').value);
        const discount = parseCurrency(item.querySelector('input[name="discount[]"]').value);
        
        const subtotal = quantity * unitPrice;
        const discountAmount = subtotal * (discount / 100);
        const total = subtotal - discountAmount;
        
        item.querySelector('.item-total').textContent = formatCurrency(total);
        return total;
    }

    function updateTotals() {
        const items = document.querySelectorAll('.item');
        let subtotal = 0;
        
        items.forEach(item => {
            const quantity = parseCurrency(item.querySelector('input[name="quantity[]"]').value);
            const unitPrice = parseCurrency(item.querySelector('input[name="unit_price[]"]').value);
            const discount = parseCurrency(item.querySelector('input[name="discount[]"]').value);
            
            const itemTotal = calculateItemTotal(item);
            item.querySelector('.item-total').textContent = formatCurrency(itemTotal);
            subtotal += itemTotal;
        });
        
        document.getElementById('subtotal').textContent = formatCurrency(subtotal);
        const includeTax = document.querySelector('input[name="include_tax"]:checked').value === 'true';
        const taxAmount = includeTax ? subtotal * 0.16 : 0;  // 16% VAT if included
        document.getElementById('tax').textContent = formatCurrency(taxAmount);
        document.getElementById('total').textContent = formatCurrency(subtotal + taxAmount);
    }

    // Format input values on blur
    itemsList.addEventListener('blur', function(e) {
        if (e.target.matches('input[name="quantity[]"]')) {
            const value = parseCurrency(e.target.value);
            e.target.value = formatNumber(value);
        }
        if (e.target.matches('input[name="unit_price[]"]')) {
            const value = parseCurrency(e.target.value);
            e.target.value = formatNumber(value);
        }
        if (e.target.matches('input[name="discount[]"]')) {
            const value = parseCurrency(e.target.value);
            e.target.value = formatNumber(value);
        }
    }, true);

    // Add new item
    addItemBtn.addEventListener('click', function() {
        const newItem = document.querySelector('.item').cloneNode(true);
        
        // Reset and initialize the new item
        newItem.querySelectorAll('input').forEach(input => {
            input.classList.remove('error');
            input.parentElement.querySelector('.error-message').style.display = 'none';
            
            if (input.name === 'quantity[]') {
                input.value = '1';
            } else if (input.name === 'unit_price[]') {
                input.value = '';
            } else if (input.name === 'discount[]') {
                input.value = '0';
            } else {
                input.value = '';
            }
        });

        newItem.querySelector('.item-total').textContent = formatCurrency(0);
        itemsList.appendChild(newItem);
        
        // Add validation listeners to new inputs
        newItem.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', function() {
                validateInput(this);
                updateTotals();
            });
        });
    });

    // Remove item
    itemsList.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-item')) {
            const items = document.querySelectorAll('.item');
            if (items.length > 1) {
                e.target.closest('.item').remove();
                updateTotals();
            }
        }
    });

    // Input validation and calculation
    itemsList.addEventListener('input', function(e) {
        if (e.target.matches('input')) {
            validateInput(e.target);
            updateTotals();
        }
    });

    // Add event listeners for VAT options
    document.querySelectorAll('input[name="include_tax"]').forEach(radio => {
        radio.addEventListener('change', updateTotals);
    });

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        let isValid = true;
        
        // Validate client selection
        const clientSelect = document.getElementById('client');
        if (!clientSelect.value) {
            isValid = false;
            clientSelect.classList.add('error');
            document.getElementById('client-error').textContent = 'Please select a client';
            document.getElementById('client-error').style.display = 'block';
        }

        // Validate all inputs in items
        document.querySelectorAll('.item input').forEach(input => {
            if (!validateInput(input)) {
                isValid = false;
            }
        });

        if (!isValid) {
            showNotification('Please fill in all required fields correctly', true);
            return;
        }

        const formData = {
            client_id: clientSelect.value,
            payment_method: document.getElementById('payment_method').value,
            payment_status: document.getElementById('payment_status').value,
            include_tax: document.querySelector('input[name="include_tax"]:checked').value === 'true',
            items: [],
            subtotal: parseCurrency(document.getElementById('subtotal').textContent),
            tax_amount: parseCurrency(document.getElementById('tax').textContent),
            total_amount: parseCurrency(document.getElementById('total').textContent)
        };

        // Gather items
        document.querySelectorAll('.item').forEach(item => {
            formData.items.push({
                description: item.querySelector('input[name="description[]"]').value.trim(),
                quantity: parseCurrency(item.querySelector('input[name="quantity[]"]').value),
                unit_price: parseCurrency(item.querySelector('input[name="unit_price[]"]').value),
                discount: parseCurrency(item.querySelector('input[name="discount[]"]').value)
            });
        });

        try {
            const response = await fetch('/sales/direct-sale/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            
            if (data.success) {
                showNotification('Sale completed successfully!');
                setTimeout(() => window.location.href = data.redirect_url, 1500);
            } else {
                showNotification(data.error || 'Error creating sale', true);
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('An error occurred while processing the sale', true);
        }
    });

    // Initialize validation listeners for initial inputs
    document.querySelectorAll('.item input').forEach(input => {
        input.addEventListener('input', function() {
            validateInput(this);
            updateTotals();
        });
    });

    // Initial calculation
    updateTotals();
}); 