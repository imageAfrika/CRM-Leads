// Products App JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize any components or functionality
    initializeFormsets();
    initializeDeleteConfirmation();
    initializeProductSearch();
});

// Initialize formsets for purchase items
function initializeFormsets() {
    const formsetContainer = document.querySelector('.formset-container');
    if (!formsetContainer) return;

    const addButton = document.querySelector('.add-formset-row');
    if (addButton) {
        addButton.addEventListener('click', function() {
            const forms = formsetContainer.querySelectorAll('.formset-row');
            const totalForms = document.querySelector('#id_items-TOTAL_FORMS');
            
            // Clone the first form
            const newForm = forms[0].cloneNode(true);
            
            // Update form index
            const formCount = forms.length;
            newForm.innerHTML = newForm.innerHTML.replace(/-0-/g, `-${formCount}-`);
            
            // Clear input values
            newForm.querySelectorAll('input, select').forEach(input => {
                if (input.type !== 'hidden' || !input.name.includes('id')) {
                    input.value = '';
                }
            });
            
            // Add delete button if it doesn't exist
            if (!newForm.querySelector('.delete-row')) {
                const deleteButton = document.createElement('button');
                deleteButton.type = 'button';
                deleteButton.className = 'btn btn-sm btn-danger delete-row';
                deleteButton.innerHTML = '<i class="fas fa-trash"></i>';
                deleteButton.addEventListener('click', function() {
                    this.closest('.formset-row').remove();
                    updateFormIndices();
                });
                
                newForm.appendChild(deleteButton);
            }
            
            // Add the new form
            formsetContainer.appendChild(newForm);
            
            // Update total forms
            totalForms.value = forms.length + 1;
            
            // Initialize event listeners for the new row
            initializeFormsetRow(newForm);
        });
    }
    
    // Initialize existing rows
    document.querySelectorAll('.formset-row').forEach(row => {
        initializeFormsetRow(row);
    });
    
    // Add delete functionality to existing delete buttons
    document.querySelectorAll('.delete-row').forEach(button => {
        button.addEventListener('click', function() {
            this.closest('.formset-row').remove();
            updateFormIndices();
        });
    });
}

// Initialize a single formset row
function initializeFormsetRow(row) {
    // Product selection change
    const productSelect = row.querySelector('select[name$="-product"]');
    if (productSelect) {
        productSelect.addEventListener('change', function() {
            // You could fetch product details via AJAX here
            // and update price fields automatically
        });
    }
    
    // Calculate total price when quantity or unit price changes
    const quantityInput = row.querySelector('input[name$="-quantity"]');
    const unitPriceInput = row.querySelector('input[name$="-unit_price"]');
    const totalPriceInput = row.querySelector('input[name$="-total_price"]');
    
    if (quantityInput && unitPriceInput && totalPriceInput) {
        const calculateTotal = function() {
            const quantity = parseFloat(quantityInput.value) || 0;
            const unitPrice = parseFloat(unitPriceInput.value) || 0;
            totalPriceInput.value = (quantity * unitPrice).toFixed(2);
        };
        
        quantityInput.addEventListener('input', calculateTotal);
        unitPriceInput.addEventListener('input', calculateTotal);
    }
}

// Update form indices after deletion
function updateFormIndices() {
    const formsetContainer = document.querySelector('.formset-container');
    const totalForms = document.querySelector('#id_items-TOTAL_FORMS');
    
    if (formsetContainer && totalForms) {
        const forms = formsetContainer.querySelectorAll('.formset-row');
        totalForms.value = forms.length;
    }
}

// Initialize delete confirmation modals
function initializeDeleteConfirmation() {
    const deleteModal = document.getElementById('deleteModal');
    if (!deleteModal) return;
    
    const cancelButton = deleteModal.querySelector('.btn-cancel');
    if (cancelButton) {
        cancelButton.addEventListener('click', function() {
            deleteModal.style.display = 'none';
        });
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === deleteModal) {
            deleteModal.style.display = 'none';
        }
    });
    
    // Close modal when pressing Escape
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && deleteModal.style.display === 'block') {
            deleteModal.style.display = 'none';
        }
    });
    
    // Setup delete buttons
    document.querySelectorAll('[data-toggle="delete-modal"]').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.dataset.id;
            const itemName = this.dataset.name;
            
            // Update modal content
            const itemNameElement = deleteModal.querySelector('.item-name');
            if (itemNameElement) {
                itemNameElement.textContent = itemName;
            }
            
            // Update form action
            const form = deleteModal.querySelector('form');
            if (form) {
                form.action = form.dataset.baseUrl.replace('0', itemId);
            }
            
            // Show modal
            deleteModal.style.display = 'block';
        });
    });
}

// Initialize product search functionality
function initializeProductSearch() {
    const searchForm = document.querySelector('.search-form');
    if (!searchForm) return;
    
    const searchInput = searchForm.querySelector('input[name="search"]');
    const clearButton = searchForm.querySelector('.clear-search');
    
    if (clearButton && searchInput) {
        // Show/hide clear button based on input
        searchInput.addEventListener('input', function() {
            clearButton.style.display = this.value ? 'block' : 'none';
        });
        
        // Initialize on page load
        clearButton.style.display = searchInput.value ? 'block' : 'none';
        
        // Clear search
        clearButton.addEventListener('click', function() {
            searchInput.value = '';
            clearButton.style.display = 'none';
            searchForm.submit();
        });
    }
    
    // Filter dropdowns
    const filterDropdowns = document.querySelectorAll('.filter-dropdown');
    filterDropdowns.forEach(dropdown => {
        dropdown.addEventListener('change', function() {
            searchForm.submit();
        });
    });
} 