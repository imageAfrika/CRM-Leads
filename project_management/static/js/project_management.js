// Project Management JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize select2 for multi-select fields if Select2 is available
    if (typeof $.fn.select2 !== 'undefined') {
        $('.select2').select2({
            theme: 'bootstrap4',
            width: '100%'
        });
    }
    
    // Initialize datepickers if Flatpickr is available
    if (typeof flatpickr !== 'undefined') {
        flatpickr('.datepicker', {
            dateFormat: 'Y-m-d',
            allowInput: true
        });
    }
    
    // Budget calculation in project form
    const budgetInput = document.getElementById('id_budget');
    const actualCostInput = document.getElementById('id_actual_cost');
    const budgetUtilizationElement = document.getElementById('budget-utilization');
    
    if (budgetInput && actualCostInput && budgetUtilizationElement) {
        const calculateBudgetUtilization = function() {
            const budget = parseFloat(budgetInput.value) || 0;
            const actualCost = parseFloat(actualCostInput.value) || 0;
            
            if (budget > 0) {
                const utilization = (actualCost / budget) * 100;
                budgetUtilizationElement.textContent = utilization.toFixed(1) + '%';
                
                // Update progress bar if exists
                const progressBar = document.getElementById('budget-progress');
                if (progressBar) {
                    progressBar.style.width = Math.min(utilization, 100) + '%';
                    if (utilization > 100) {
                        progressBar.classList.add('bg-danger');
                        progressBar.classList.remove('bg-success');
                    } else {
                        progressBar.classList.add('bg-success');
                        progressBar.classList.remove('bg-danger');
                    }
                }
            } else {
                budgetUtilizationElement.textContent = 'N/A';
            }
        };
        
        budgetInput.addEventListener('input', calculateBudgetUtilization);
        actualCostInput.addEventListener('input', calculateBudgetUtilization);
        
        // Initial calculation
        calculateBudgetUtilization();
    }
    
    // Completion percentage validation
    const completionInput = document.getElementById('id_completion_percentage');
    if (completionInput) {
        completionInput.addEventListener('input', function() {
            let value = parseInt(this.value) || 0;
            if (value < 0) value = 0;
            if (value > 100) value = 100;
            this.value = value;
        });
    }
    
    // Project deletion confirmation
    const deleteProjectForm = document.getElementById('delete-project-form');
    if (deleteProjectForm) {
        deleteProjectForm.addEventListener('submit', function(event) {
            if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
                event.preventDefault();
            }
        });
    }
    
    // Document/Note/Milestone deletion confirmation
    document.querySelectorAll('.delete-confirmation').forEach(function(element) {
        element.addEventListener('click', function(event) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                event.preventDefault();
            }
        });
    });
    
    // Project financial charts initialization if Chart.js is available
    if (typeof Chart !== 'undefined') {
        // Revenue vs Expenses Chart
        const revenueExpensesCanvas = document.getElementById('revenue-expenses-chart');
        if (revenueExpensesCanvas) {
            const ctx = revenueExpensesCanvas.getContext('2d');
            
            // Get data from data attributes or API
            const revenue = parseFloat(revenueExpensesCanvas.dataset.revenue) || 0;
            const expenses = parseFloat(revenueExpensesCanvas.dataset.expenses) || 0;
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Revenue', 'Expenses'],
                    datasets: [{
                        label: 'Amount',
                        data: [revenue, expenses],
                        backgroundColor: [
                            'rgba(0, 123, 255, 0.7)',
                            'rgba(220, 53, 69, 0.7)'
                        ],
                        borderColor: [
                            'rgba(0, 123, 255, 1)',
                            'rgba(220, 53, 69, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // Transaction History Chart
        const transactionHistoryCanvas = document.getElementById('transaction-history-chart');
        if (transactionHistoryCanvas) {
            const ctx = transactionHistoryCanvas.getContext('2d');
            
            // In a real application, this data would come from your API
            // This is just placeholder data
            const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
            const deposits = [1000, 1500, 800, 1200, 1800, 1300];
            const withdrawals = [500, 800, 1200, 600, 400, 900];
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Revenue',
                            data: deposits,
                            borderColor: 'rgba(40, 167, 69, 1)',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: 'Expenses',
                            data: withdrawals,
                            borderColor: 'rgba(220, 53, 69, 1)',
                            backgroundColor: 'rgba(220, 53, 69, 0.1)',
                            tension: 0.4,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }
    
    // AJAX form submissions with fetch API
    document.querySelectorAll('.ajax-form').forEach(function(form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const formData = new FormData(this);
            const submitButton = this.querySelector('[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            const feedbackElement = document.getElementById(this.dataset.feedback);
            
            // Show loading state
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="loading-spinner"></span> Processing...';
            
            if (feedbackElement) {
                feedbackElement.innerHTML = '';
                feedbackElement.classList.remove('alert-success', 'alert-danger');
                feedbackElement.classList.add('d-none');
            }
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                // Restore button state
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
                
                if (feedbackElement) {
                    feedbackElement.classList.remove('d-none');
                    
                    if (data.success) {
                        feedbackElement.classList.add('alert-success');
                        feedbackElement.innerHTML = data.message || 'Operation completed successfully.';
                        
                        // Reset form if operation was successful
                        if (!this.dataset.noReset) {
                            this.reset();
                        }
                        
                        // Reload page or redirect if specified
                        if (data.redirect) {
                            window.location.href = data.redirect;
                        } else if (this.dataset.reload) {
                            window.location.reload();
                        }
                    } else {
                        feedbackElement.classList.add('alert-danger');
                        feedbackElement.innerHTML = data.message || 'An error occurred. Please try again.';
                        
                        // Show field errors if any
                        if (data.errors) {
                            for (const field in data.errors) {
                                const errorElement = document.getElementById(`error-${field}`);
                                const inputElement = document.getElementById(`id_${field}`);
                                
                                if (errorElement) {
                                    errorElement.innerHTML = data.errors[field].join('<br>');
                                    errorElement.classList.remove('d-none');
                                }
                                
                                if (inputElement) {
                                    inputElement.classList.add('is-invalid');
                                }
                            }
                        }
                    }
                }
            })
            .catch(error => {
                // Restore button state
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
                
                if (feedbackElement) {
                    feedbackElement.classList.remove('d-none');
                    feedbackElement.classList.add('alert-danger');
                    feedbackElement.innerHTML = 'A network error occurred. Please try again.';
                }
                
                console.error('Error:', error);
            });
        });
    });
}); 