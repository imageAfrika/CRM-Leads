/**
 * Debug script for quote preview functionality
 */
 
document.addEventListener('DOMContentLoaded', function() {
    console.log('Debug script loaded for quote preview');
    
    // Check if the preview button exists
    const previewButton = document.getElementById('preview-button');
    if (previewButton) {
        console.log('Preview button found');
        
        // Add a click listener for debugging
        previewButton.addEventListener('click', function() {
            console.log('Preview button clicked');
            debugPreviewQuote();
        });
    } else {
        console.error('Preview button not found in the DOM');
    }
    
    // Debug version of previewQuote
    window.debugPreviewQuote = async function() {
        console.log('Debug preview quote function called');
        
        try {
            // Check if the client is selected
            const clientSelect = document.getElementById('client');
            if (!clientSelect) {
                console.error('Client select element not found');
                return;
            }
            
            if (!clientSelect.value) {
                console.error('No client selected');
                alert('Please select a client.');
                return;
            }
            console.log('Client selected:', clientSelect.value);
            
            // Collect items
            const items = [];
            const itemElements = document.querySelectorAll('.quote-item');
            console.log('Found', itemElements.length, 'quote items');
            
            itemElements.forEach((item, index) => {
                try {
                    const descInput = item.querySelector('[name="items[][description]"]');
                    const qtyInput = item.querySelector('[name="items[][quantity]"]');
                    const priceInput = item.querySelector('[name="items[][unit_price]"]');
                    const discountInput = item.querySelector('[name="items[][discount]"]');
                    
                    if (!descInput || !qtyInput || !priceInput || !discountInput) {
                        console.error('Missing input field in item', index);
                        return;
                    }
                    
                    items.push({
                        description: descInput.value || 'No description',
                        quantity: parseFloat(qtyInput.value) || 1,
                        unit_price: parseFloat(priceInput.value) || 0,
                        discount: parseFloat(discountInput.value) || 0
                    });
                    
                    console.log('Added item:', items[items.length - 1]);
                } catch (itemError) {
                    console.error('Error processing item', index, itemError);
                }
            });
            
            // Get form data
            const quoteNumber = document.getElementById('quote_number').value || 'PREVIEW-001';
            const quoteTitle = document.getElementById('quote_title').value || 'Quote Preview';
            const description = document.getElementById('description').value || '';
            const validUntil = document.getElementById('valid_until').value;
            const terms = document.getElementById('terms').value || '';
            const taxRate = parseFloat(document.getElementById('tax_rate').value) || 16;
            const subtotal = parseFloat(document.getElementById('subtotal').value) || 0;
            const taxAmount = parseFloat(document.getElementById('tax_amount').value) || 0;
            const totalAmount = parseFloat(document.getElementById('total_amount').value) || 0;
            
            console.log('Quote data:', {
                quote_number: quoteNumber,
                title: quoteTitle,
                description,
                valid_until: validUntil,
                tax_rate: taxRate,
                subtotal,
                tax_amount: taxAmount,
                total_amount: totalAmount,
                items_count: items.length
            });
            
            // Get the CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            console.log('CSRF Token found:', csrfToken ? 'Yes' : 'No');
            
            // Test the preview endpoint
            console.log('Attempting to fetch preview from /documents/quote/preview/');
            const response = await fetch('/documents/quote/preview/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    client_id: clientSelect.value,
                    quote_number: quoteNumber,
                    title: quoteTitle,
                    description: description,
                    valid_until: validUntil || new Date().toISOString().split('T')[0],
                    terms: terms,
                    tax_rate: taxRate,
                    subtotal: subtotal,
                    tax_amount: taxAmount,
                    total_amount: totalAmount,
                    items: items
                })
            });
            
            console.log('Preview response status:', response.status);
            
            if (response.ok) {
                const responseData = await response.json();
                console.log('Preview response data:', responseData);
                
                if (responseData.success && responseData.redirect_url) {
                    // Open the preview template in a new tab
                    window.open(responseData.redirect_url, '_blank');
                    console.log('Preview opened in new tab');
                } else if (responseData.error) {
                    console.error('Preview error:', responseData.error);
                    alert('Failed to generate preview: ' + responseData.error);
                }
            } else {
                const errorText = await response.text();
                console.error('Preview failed:', errorText);
                alert('Failed to generate preview. See console for details.');
            }
            
        } catch (error) {
            console.error('Error in debugPreviewQuote:', error);
            alert('An error occurred while generating the preview: ' + error.message);
        }
    };
}); 