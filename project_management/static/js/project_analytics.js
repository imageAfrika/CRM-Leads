/**
 * Project Analytics Dashboard JavaScript
 * This script handles the rendering of charts and data visualizations for project financial analytics
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts when the DOM is fully loaded
    initializeCharts();
    
    // Set up event listeners for filters
    setupFilterListeners();
});

/**
 * Initialize all charts in the analytics dashboard
 */
function initializeCharts() {
    renderOverviewChart();
    renderDistributionChart();
    renderTrendChart();
    renderProjectComparisonTable();
}

/**
 * Main overview chart - Budget vs. Invoices vs. Expenses vs. Purchases
 */
function renderOverviewChart() {
    const ctx = document.getElementById('overview-chart').getContext('2d');
    
    // Sample data - In a real application, this would come from an API
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    const data = {
        labels: months,
        datasets: [
            {
                label: 'Budget',
                data: [50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000],
                borderColor: getComputedStyle(document.documentElement).getPropertyValue('--budget-color'),
                backgroundColor: 'transparent',
                borderWidth: 3,
                pointBackgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--budget-color'),
                pointRadius: 4,
                type: 'line',
                tension: 0.1,
                order: 0
            },
            {
                label: 'Invoices',
                data: [45000, 48000, 46000, 49000, 53000, 51000, 55000, 54000, 52000, 58000, 56000, 60000],
                backgroundColor: hexToRGBA(getComputedStyle(document.documentElement).getPropertyValue('--invoices-color'), 0.7),
                borderColor: getComputedStyle(document.documentElement).getPropertyValue('--invoices-color'),
                borderWidth: 1,
                order: 1
            },
            {
                label: 'Expenses',
                data: [30000, 32000, 31000, 34000, 33000, 36000, 35000, 37000, 38000, 39000, 41000, 40000],
                backgroundColor: hexToRGBA(getComputedStyle(document.documentElement).getPropertyValue('--expenses-color'), 0.7),
                borderColor: getComputedStyle(document.documentElement).getPropertyValue('--expenses-color'),
                borderWidth: 1,
                order: 2
            },
            {
                label: 'Purchases',
                data: [10000, 11000, 9000, 12000, 13000, 11500, 14000, 12500, 13500, 15000, 14500, 16000],
                backgroundColor: hexToRGBA(getComputedStyle(document.documentElement).getPropertyValue('--purchases-color'), 0.7),
                borderColor: getComputedStyle(document.documentElement).getPropertyValue('--purchases-color'),
                borderWidth: 1,
                order: 3
            }
        ]
    };
    
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false // We're using our custom legend
            },
            tooltip: {
                mode: 'index',
                intersect: false
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: '#f0f0f0'
                },
                ticks: {
                    callback: function(value) {
                        return '$' + formatNumber(value);
                    }
                }
            }
        }
    };
    
    new Chart(ctx, {
        type: 'bar', // We'll use the type property in datasets for mixed charts
        data: data,
        options: options
    });
}

/**
 * Distribution pie chart for cost breakdown
 */
function renderDistributionChart() {
    const ctx = document.getElementById('distribution-chart').getContext('2d');
    
    // Sample data
    const data = {
        labels: ['Labor', 'Materials', 'Services', 'Equipment', 'Other'],
        datasets: [{
            data: [40, 25, 20, 10, 5],
            backgroundColor: [
                '#4a6fdc',
                '#3498db',
                '#2ecc71',
                '#f39c12',
                '#e74c3c'
            ],
            borderWidth: 1,
            borderColor: '#ffffff'
        }]
    };
    
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    boxWidth: 12,
                    padding: 15
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = context.parsed || 0;
                        return label + ': ' + value + '%';
                    }
                }
            }
        }
    };
    
    new Chart(ctx, {
        type: 'pie',
        data: data,
        options: options
    });
}

/**
 * Trend chart for monthly progression
 */
function renderTrendChart() {
    const ctx = document.getElementById('trend-chart').getContext('2d');
    
    // Sample data
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    const data = {
        labels: months,
        datasets: [{
            label: 'Profit Margin',
            data: [5, 8, 7, 9, 10, 8, 11, 10, 9, 12, 10, 13],
            borderColor: '#2ecc71',
            backgroundColor: hexToRGBA('#2ecc71', 0.1),
            fill: true,
            tension: 0.4
        }]
    };
    
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return 'Profit Margin: ' + context.parsed.y + '%';
                    }
                }
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: '#f0f0f0'
                },
                ticks: {
                    callback: function(value) {
                        return value + '%';
                    }
                }
            }
        }
    };
    
    new Chart(ctx, {
        type: 'line',
        data: data,
        options: options
    });
}

/**
 * Project comparison table with dynamic bars
 */
function renderProjectComparisonTable() {
    // Sample projects data
    const projects = [
        { id: 1, name: 'Office Renovation', budget: 120000, invoiced: 110000, expenses: 85000, purchases: 70000 },
        { id: 2, name: 'Website Redesign', budget: 50000, invoiced: 45000, expenses: 30000, purchases: 25000 },
        { id: 3, name: 'Marketing Campaign', budget: 80000, invoiced: 75000, expenses: 60000, purchases: 50000 },
        { id: 4, name: 'Mobile App Development', budget: 100000, invoiced: 90000, expenses: 75000, purchases: 60000 },
        { id: 5, name: 'Product Launch', budget: 150000, invoiced: 140000, expenses: 120000, purchases: 100000 }
    ];
    
    const tableBody = document.getElementById('project-comparison-body');
    if (!tableBody) return;
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    // Add new rows
    projects.forEach(project => {
        const invoicedPercent = (project.invoiced / project.budget * 100).toFixed(1);
        const expensesPercent = (project.expenses / project.budget * 100).toFixed(1);
        const purchasesPercent = (project.purchases / project.budget * 100).toFixed(1);
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <div class="project-name">${project.name}</div>
            </td>
            <td>$${formatNumber(project.budget)}</td>
            <td class="project-progress">
                <div class="progress-container">
                    <div class="progress-fill fill-invoices" style="width: ${invoicedPercent}%"></div>
                </div>
                <div class="progress-text">$${formatNumber(project.invoiced)} (${invoicedPercent}%)</div>
            </td>
            <td class="project-progress">
                <div class="progress-container">
                    <div class="progress-fill fill-expenses" style="width: ${expensesPercent}%"></div>
                </div>
                <div class="progress-text">$${formatNumber(project.expenses)} (${expensesPercent}%)</div>
            </td>
            <td class="project-progress">
                <div class="progress-container">
                    <div class="progress-fill fill-purchases" style="width: ${purchasesPercent}%"></div>
                </div>
                <div class="progress-text">$${formatNumber(project.purchases)} (${purchasesPercent}%)</div>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Set up event listeners for filter controls
 */
function setupFilterListeners() {
    // Filter form submission
    const filterForm = document.getElementById('analytics-filter-form');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Here you would typically fetch new data based on filters
            // For demo purposes, we'll just refresh the charts
            initializeCharts();
            
            // Show success notification
            showNotification('Filters applied successfully');
        });
    }
    
    // Export button
    const exportButton = document.getElementById('export-button');
    if (exportButton) {
        exportButton.addEventListener('click', function() {
            showNotification('Exporting data... Download will start shortly.');
            // In a real application, this would trigger a file download
        });
    }
}

/**
 * Show a notification message
 */
function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.innerHTML = message;
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.add('active');
    }, 10);
    
    // Animate out and remove
    setTimeout(() => {
        notification.classList.remove('active');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

/**
 * Helper function to format numbers with commas
 */
function formatNumber(number) {
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Helper function to convert hex colors to rgba for transparency
 */
function hexToRGBA(hex, alpha) {
    hex = hex.trim();
    // Remove the '#' if it exists
    if (hex.charAt(0) === '#') {
        hex = hex.substr(1);
    }
    
    // Parse the hex values
    let r, g, b;
    if (hex.length === 3) {
        r = parseInt(hex.charAt(0) + hex.charAt(0), 16);
        g = parseInt(hex.charAt(1) + hex.charAt(1), 16);
        b = parseInt(hex.charAt(2) + hex.charAt(2), 16);
    } else {
        r = parseInt(hex.substr(0, 2), 16);
        g = parseInt(hex.substr(2, 2), 16);
        b = parseInt(hex.substr(4, 2), 16);
    }
    
    // Return the rgba color string
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
} 