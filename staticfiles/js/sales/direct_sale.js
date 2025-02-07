document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('directSaleForm');
    const addItemBtn = document.getElementById('addItemBtn');
    const saleItems = document.getElementById('saleItems');
    const TAX_RATE = 0.15; // 15% tax rate - adjust as needed

    // Add new item row
    addItemBtn.addEventListener('click', function() {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'sale-item';
        itemDiv.innerHTML = `
            <div class="form-group">
                <label>Description</label>
                <input type="text" name="items[][description]" required>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Quantity</label>
                    <input type="number" name="items[][quantity]" min="1" required>
                </div>
                <div class="form-group">
                    <label>Unit Price</label>
                    <input type="number" name="items[][unit_price]" step="0.01" required>
                </div>
                <div class="form-group">
                    <label>Discount %</label>
                    <input type="number" name="items[][discount]" min="0" max="100" value="0">
                </div>
            </div>
            <button type="button" class="remove-item btn btn-danger">Remove</button>
        `;
        saleItems.appendChild(itemDiv);
        
        // Add change listeners to new inputs
        itemDiv.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', updateTotals);
        });
    });

    // Remove item
    saleItems.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-item')) {
            e.target.closest('.sale-item').remove();
            updateTotals();
        }
    });

    // Update totals when inputs change
    function updateTotals() {
        let subtotal = 0;
        
        document.querySelectorAll('.sale-item').forEach(item => {
            const quantity = parseFloat(item.querySelector('[name="items[][quantity]"]').value) || 0;
            const unitPrice = parseFloat(item.querySelector('[name="items[][unit_price]"]').value) || 0;
            const discount = parseFloat(item.querySelector('[name="items[][discount]"]').value) || 0;
            
            const itemTotal = quantity * unitPrice * (1 - discount/100);
            subtotal += itemTotal;
        });
        
        const tax = subtotal * TAX_RATE;
        const total = subtotal + tax;
        
        document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
        document.getElementById('tax').textContent = `$${tax.toFixed(2)}`;
        document.getElementById('total').textContent = `$${total.toFixed(2)}`;
    }

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Gather items data
        const items = [];
        document.querySelectorAll('.sale-item').forEach(item => {
            items.push({
                description: item.querySelector('[name="items[][description]"]').value,
                quantity: item.querySelector('[name="items[][quantity]"]').value,
                unit_price: item.querySelector('[name="items[][unit_price]"]').value,
                discount: item.querySelector('[name="items[][discount]"]').value
            });
        });

        const formData = {
            client_id: document.getElementById('client').value,
            items: items,
            payment_method: form.querySelector('[name="payment_method"]').value,
            payment_status: form.querySelector('[name="payment_status"]').value,
            subtotal: parseFloat(document.getElementById('subtotal').textContent.replace('$', '')),
            tax_amount: parseFloat(document.getElementById('tax').textContent.replace('$', '')),
            total_amount: parseFloat(document.getElementById('total').textContent.replace('$', ''))
        };

        try {
            const response = await fetch('/sales/direct-sale/', {
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
                alert('Error creating sale: ' + data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to create sale. Please try again.');
        }
    });

    // Add change listeners to initial inputs
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', updateTotals);
    });
}); 