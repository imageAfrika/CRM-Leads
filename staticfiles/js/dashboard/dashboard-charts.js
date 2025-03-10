document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard charts loaded');

    // Set default Chart.js options
    Chart.defaults.font.family = "'Inter', 'Helvetica', 'Arial', sans-serif";
    Chart.defaults.font.size = 13;
    Chart.defaults.plugins.legend.position = 'bottom';

    // Initialize Quotes vs Invoices Chart
    const quotesVsInvoicesChart = document.getElementById('quotesVsInvoicesChart');
    if (quotesVsInvoicesChart) {
        const quotes = parseInt(quotesVsInvoicesChart.dataset.quotes) || 0;
        const invoices = parseInt(quotesVsInvoicesChart.dataset.invoices) || 0;
        
        new Chart(quotesVsInvoicesChart, {
            type: 'doughnut',
            data: {
                labels: ['Quotes', 'Invoices'],
                datasets: [{
                    data: [quotes, invoices],
                    backgroundColor: ['#60a5fa', '#34d399'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Quotes vs Invoices',
                        font: { size: 16, weight: 'bold' }
                    }
                }
            }
        });
    }

    // Initialize Revenue vs Expenditure Chart
    const revenueVsExpenditureChart = document.getElementById('revenueVsExpenditureChart');
    if (revenueVsExpenditureChart) {
        const revenue = parseFloat(revenueVsExpenditureChart.dataset.revenue) || 0;
        const expenditure = parseFloat(revenueVsExpenditureChart.dataset.expenditure) || 0;
        
        new Chart(revenueVsExpenditureChart, {
            type: 'bar',
            data: {
                labels: ['Revenue', 'Expenditure'],
                datasets: [{
                    data: [revenue, expenditure],
                    backgroundColor: ['#34d399', '#f87171'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Revenue vs Expenditure',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    // Initialize Expenses vs Purchases Chart
    const expensesVsPurchasesChart = document.getElementById('expensesVsPurchasesChart');
    if (expensesVsPurchasesChart) {
        const months = JSON.parse(expensesVsPurchasesChart.dataset.months || '[]');
        const expenses = JSON.parse(expensesVsPurchasesChart.dataset.expenses || '[]');
        const purchases = JSON.parse(expensesVsPurchasesChart.dataset.purchases || '[]');
        
        new Chart(expensesVsPurchasesChart, {
            type: 'line',
            data: {
                labels: months,
                datasets: [
                    {
                        label: 'Expenses',
                        data: expenses,
                        borderColor: '#f87171',
                        backgroundColor: 'rgba(248, 113, 113, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Purchases',
                        data: purchases,
                        borderColor: '#60a5fa',
                        backgroundColor: 'rgba(96, 165, 250, 0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Expenses vs Purchases Trends',
                        font: { size: 16, weight: 'bold' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    // Initialize Monthly Trends Chart
    const monthlyTrendsChart = document.getElementById('monthlyTrendsChart');
    if (monthlyTrendsChart) {
        const months = JSON.parse(monthlyTrendsChart.dataset.months || '[]');
        const revenue = JSON.parse(monthlyTrendsChart.dataset.revenue || '[]');
        const expenses = JSON.parse(monthlyTrendsChart.dataset.expenses || '[]');
        
        new Chart(monthlyTrendsChart, {
            type: 'line',
            data: {
                labels: months,
                datasets: [
                    {
                        label: 'Revenue',
                        data: revenue,
                        borderColor: '#34d399',
                        backgroundColor: 'rgba(52, 211, 153, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Expenses',
                        data: expenses,
                        borderColor: '#f87171',
                        backgroundColor: 'rgba(248, 113, 113, 0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Monthly Revenue vs Expenses',
                        font: { size: 16, weight: 'bold' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
});
