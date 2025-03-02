document.addEventListener('DOMContentLoaded', function() {
    // Get data from the data div
    const reportData = document.querySelector('.report-data');
    if (!reportData) return;
    
    // Parse JSON data
    const categories = JSON.parse(reportData.dataset.categories || '[]');
    const categoryAmounts = JSON.parse(reportData.dataset.categoryAmounts || '[]');
    const months = JSON.parse(reportData.dataset.months || '[]');
    const monthlyAmounts = JSON.parse(reportData.dataset.monthlyAmounts || '[]');
    
    // Initialize charts if data exists
    if (categories.length > 0 && categoryAmounts.length > 0) {
        initCategoryChart(categories, categoryAmounts);
    }
    
    if (months.length > 0 && monthlyAmounts.length > 0) {
        initTrendChart(months, monthlyAmounts);
    }
    
    // Set up filter form to submit on change
    const periodSelect = document.getElementById('period');
    if (periodSelect) {
        periodSelect.addEventListener('change', function() {
            document.getElementById('report-filter-form').submit();
        });
    }
});

function initCategoryChart(categories, amounts) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    // Generate colors for each category
    const backgroundColors = generateColors(categories.length, 0.7);
    const borderColors = generateColors(categories.length, 1);
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: categories,
            datasets: [{
                data: amounts,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 15,
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${formatCurrency(value)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function initTrendChart(months, amounts) {
    const ctx = document.getElementById('trendChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Monthly Purchases',
                data: amounts,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Amount: ${formatCurrency(context.raw)}`;
                        }
                    }
                }
            }
        }
    });
}

function generateColors(count, alpha) {
    const colors = [];
    const hueStep = 360 / count;
    
    for (let i = 0; i < count; i++) {
        const hue = i * hueStep;
        colors.push(`hsla(${hue}, 70%, 60%, ${alpha})`);
    }
    
    return colors;
}

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'KES',
        minimumFractionDigits: 2
    }).format(value);
} 