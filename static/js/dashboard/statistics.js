document.addEventListener('DOMContentLoaded', function() {
    // Modern chart configuration
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 1000,
            easing: 'easeInOutQuart'
        },
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    boxWidth: 12,
                    padding: 15,
                    font: {
                        size: 12,
                        family: "'Inter', sans-serif"
                    },
                    usePointStyle: true,
                    pointStyle: 'circle'
                }
            },
            tooltip: {
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                titleColor: '#1e293b',
                bodyColor: '#475569',
                borderColor: '#e2e8f0',
                borderWidth: 1,
                padding: 12,
                boxPadding: 6,
                usePointStyle: true,
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += new Intl.NumberFormat('en-US', {
                                style: 'currency',
                                currency: 'KES'
                            }).format(context.parsed.y);
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    font: {
                        size: 11,
                        family: "'Inter', sans-serif"
                    },
                    maxRotation: 45,
                    minRotation: 45,
                    color: '#64748b'
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: '#e2e8f0',
                    drawBorder: false
                },
                ticks: {
                    font: {
                        size: 11,
                        family: "'Inter', sans-serif"
                    },
                    color: '#64748b',
                    padding: 10,
                    callback: function(value) {
                        return 'KES ' + value.toLocaleString();
                    }
                }
            }
        }
    };

    // Create gradient backgrounds
    function createGradient(ctx, color1, color2) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, color1);
        gradient.addColorStop(1, color2);
        return gradient;
    }

    // Get canvas elements
    const quotesVsInvoicesCanvas = document.getElementById('quotesVsInvoicesChart');
    const revenueVsExpenditureCanvas = document.getElementById('revenueVsExpenditureChart');
    const purchasesVsSalesCanvas = document.getElementById('purchasesVsSalesChart');
    const monthlyTrendsCanvas = document.getElementById('monthlyTrendsChart');

    if (!quotesVsInvoicesCanvas || !revenueVsExpenditureCanvas || !purchasesVsSalesCanvas || !monthlyTrendsCanvas) {
        console.warn('One or more chart canvases not found');
        return;
    }

    // Get contexts
    const quotesCtx = quotesVsInvoicesCanvas.getContext('2d');
    const revenueCtx = revenueVsExpenditureCanvas.getContext('2d');
    const purchasesCtx = purchasesVsSalesCanvas.getContext('2d');
    const trendsCtx = monthlyTrendsCanvas.getContext('2d');

    // Create gradients
    const quoteGradient = createGradient(quotesCtx, 'rgba(37, 99, 235, 0.8)', 'rgba(37, 99, 235, 0.1)');
    const invoiceGradient = createGradient(quotesCtx, 'rgba(16, 185, 129, 0.8)', 'rgba(16, 185, 129, 0.1)');

    // Initialize charts with initial data
    const quotesVsInvoicesChart = new Chart(quotesCtx, {
        type: 'bar',
        data: {
            labels: ['Current Period'],
            datasets: [
                {
                    label: 'Quotes',
                    data: [quotesVsInvoicesCanvas.dataset.quotes || 0],
                    backgroundColor: quoteGradient,
                    borderRadius: 6,
                    borderSkipped: false,
                    barPercentage: 0.7,
                },
                {
                    label: 'Invoices',
                    data: [quotesVsInvoicesCanvas.dataset.invoices || 0],
                    backgroundColor: invoiceGradient,
                    borderRadius: 6,
                    borderSkipped: false,
                    barPercentage: 0.7,
                }
            ]
        },
        options: chartOptions
    });

    const revenueVsExpenditureChart = new Chart(revenueCtx, {
        type: 'line',
        data: {
            labels: JSON.parse(monthlyTrendsCanvas.dataset.months || '[]'),
            datasets: [
                {
                    label: 'Revenue',
                    data: [revenueVsExpenditureCanvas.dataset.revenue || 0],
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                },
                {
                    label: 'Expenditure',
                    data: [revenueVsExpenditureCanvas.dataset.expenditure || 0],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                }
            ]
        },
        options: chartOptions
    });

    const purchasesVsSalesChart = new Chart(purchasesCtx, {
        type: 'line',
        data: {
            labels: JSON.parse(purchasesVsSalesCanvas.dataset.months || '[]'),
            datasets: [
                {
                    label: 'Sales',
                    data: JSON.parse(purchasesVsSalesCanvas.dataset.sales || '[]'),
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                },
                {
                    label: 'Purchases',
                    data: JSON.parse(purchasesVsSalesCanvas.dataset.purchases || '[]'),
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                }
            ]
        },
        options: chartOptions
    });

    // Function to update the quotes vs invoices chart based on metric
    function updateQuotesVsInvoicesChart(metric) {
        let quotesData, invoicesData, chartTitle;
        
        // Set data based on selected metric
        switch(metric) {
            case 'amount':
                quotesData = [parseFloat(quotesVsInvoicesCanvas.dataset.quotesAmount) || 0];
                invoicesData = [parseFloat(quotesVsInvoicesCanvas.dataset.invoicesAmount) || 0];
                chartTitle = 'Quotes vs Invoices (By Amount)';
                break;
            case 'average':
                const quotesCount = parseInt(quotesVsInvoicesCanvas.dataset.quotes) || 1;
                const invoicesCount = parseInt(quotesVsInvoicesCanvas.dataset.invoices) || 1;
                const quotesAmount = parseFloat(quotesVsInvoicesCanvas.dataset.quotesAmount) || 0;
                const invoicesAmount = parseFloat(quotesVsInvoicesCanvas.dataset.invoicesAmount) || 0;
                
                quotesData = [quotesCount > 0 ? quotesAmount / quotesCount : 0];
                invoicesData = [invoicesCount > 0 ? invoicesAmount / invoicesCount : 0];
                chartTitle = 'Quotes vs Invoices (By Average Value)';
                break;
            default: // 'count'
                quotesData = [parseInt(quotesVsInvoicesCanvas.dataset.quotes) || 0];
                invoicesData = [parseInt(quotesVsInvoicesCanvas.dataset.invoices) || 0];
                chartTitle = 'Quotes vs Invoices (By Count)';
        }
        
        // Update chart data
        quotesVsInvoicesChart.data.datasets[0].data = quotesData;
        quotesVsInvoicesChart.data.datasets[1].data = invoicesData;
        
        // Update chart title
        document.querySelector('.chart-card h2').textContent = chartTitle;
        
        // Refresh chart
        quotesVsInvoicesChart.update();
    }
    
    // Add event listener for the metric dropdown
    const metricSelector = document.getElementById('quotesVsInvoicesMetric');
    if (metricSelector) {
        metricSelector.addEventListener('change', function(e) {
            updateQuotesVsInvoicesChart(e.target.value);
        });
    }

    // Function to update charts with new data
    function updateCharts(period) {
        fetch(`/dashboard/api/chart-data/?period=${period}`)
            .then(response => response.json())
            .then(data => {
                // Update Quotes vs Invoices Chart data attributes
                quotesVsInvoicesCanvas.dataset.quotes = data.quotes_data.reduce((sum, val) => sum + val, 0);
                quotesVsInvoicesCanvas.dataset.invoices = data.invoices_data.reduce((sum, val) => sum + val, 0);
                quotesVsInvoicesCanvas.dataset.quotesAmount = data.quotes_amount.reduce((sum, val) => sum + val, 0);
                quotesVsInvoicesCanvas.dataset.invoicesAmount = data.invoices_amount.reduce((sum, val) => sum + val, 0);
                
                // Get current selected metric and update the chart
                const currentMetric = document.getElementById('quotesVsInvoicesMetric')?.value || 'count';
                updateQuotesVsInvoicesChart(currentMetric);

                // Update Revenue vs Expenditure Chart
                revenueVsExpenditureChart.data.labels = data.labels;
                revenueVsExpenditureChart.data.datasets[0].data = data.revenue_data;
                revenueVsExpenditureChart.data.datasets[1].data = data.expenditure_data;
                revenueVsExpenditureChart.update();

                // Update Purchases vs Sales Chart
                purchasesVsSalesChart.data.labels = data.labels;
                purchasesVsSalesChart.data.datasets[0].data = data.revenue_data;
                purchasesVsSalesChart.data.datasets[1].data = data.monthly_purchases || [];
                purchasesVsSalesChart.update();
            })
            .catch(error => {
                console.error('Error fetching chart data:', error);
            });
    }

    // Handle period changes if the selector exists
    const periodSelector = document.getElementById('timePeriod');
    if (periodSelector) {
        periodSelector.addEventListener('change', function(e) {
        updateCharts(e.target.value);
    });
    }

    // Initial data load
    updateCharts('month');
}); 