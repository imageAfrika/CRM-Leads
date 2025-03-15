document.addEventListener('DOMContentLoaded', function() {
    /**
     * UTILITIES
     */
    
    // Format currency values
    const formatCurrency = (value) => {
        return new Intl.NumberFormat('en-KE', {
            style: 'currency',
            currency: 'KES'
        }).format(value);
    };

    // Safe JSON parse
    const safeJSONParse = (data, defaultValue = []) => {
        if (!data || data === '[]' || data === '' || data === 'null') return defaultValue;
        try {
            const parsed = JSON.parse(data);
            return parsed || defaultValue;
        } catch (e) {
            console.error('Error parsing JSON:', e, 'Raw data:', data);
            return defaultValue;
        }
    };

    // Modern chart configuration
    const commonOptions = {
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
                            label += formatCurrency(context.parsed.y);
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
                        return formatCurrency(value);
                    }
                }
            }
        }
    };

    // Show diagnostic overlay if no data
    const showNoDataOverlay = (canvas) => {
        const container = canvas.parentElement;
        container.style.position = 'relative';
        
        // Clear any existing diagnostics
        const existingDiagnostics = container.querySelectorAll('.diagnostic-overlay');
        existingDiagnostics.forEach(el => el.remove());
        
        // Create the diagnostic overlay
        const overlay = document.createElement('div');
        overlay.className = 'diagnostic-overlay';
        overlay.style.position = 'absolute';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.display = 'flex';
        overlay.style.alignItems = 'center';
        overlay.style.justifyContent = 'center';
        overlay.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
        overlay.style.color = '#ef4444';
        overlay.style.fontWeight = 'bold';
        overlay.style.zIndex = '10';
        overlay.textContent = 'No data available for this chart';
        
        container.appendChild(overlay);
    };

    // Create gradient backgrounds
    function createGradient(ctx, color1, color2) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, color1);
        gradient.addColorStop(1, color2);
        return gradient;
    }

    /**
     * CHARTS INITIALIZATION
     */
    
    // Store chart instances to prevent conflicts
    const chartInstances = {};
    
    // Helper to safely initialize a chart
    const initChart = (canvasId, type, data, options) => {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas not found: ${canvasId}`);
            return null;
        }
        
        // Destroy existing chart if any
        if (chartInstances[canvasId]) {
            chartInstances[canvasId].destroy();
            delete chartInstances[canvasId];
        }
        
        // Check for empty data
        if (!data.datasets || data.datasets.length === 0 || 
            !data.labels || data.labels.length === 0 ||
            data.datasets.every(ds => !ds.data || ds.data.every(val => val === 0 || val === null))) {
            showNoDataOverlay(canvas);
            return null;
        }
        
        // Create and store the chart
        const ctx = canvas.getContext('2d');
        chartInstances[canvasId] = new Chart(ctx, {
            type: type,
            data: data,
            options: options
        });
        
        return chartInstances[canvasId];
    };

    /**
     * REVENUE VS EXPENDITURE CHART
     */
    const setupRevenueVsExpenditureChart = () => {
        const canvas = document.getElementById('revenueVsExpenditureChart');
        if (!canvas) return;
        
        // Single values for pie chart
        const revenue = parseFloat(canvas.dataset.revenue || 0);
        const expenditure = parseFloat(canvas.dataset.expenditure || 0);
        
        const ctx = canvas.getContext('2d');
        const chartData = {
            labels: ['Revenue', 'Expenditure'],
            datasets: [{
                data: [revenue, expenditure],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.7)',
                    'rgba(239, 68, 68, 0.7)'
                ],
                borderColor: [
                    'rgb(16, 185, 129)',
                    'rgb(239, 68, 68)'
                ],
                borderWidth: 1
            }]
        };
        
        const options = {
            ...commonOptions,
            plugins: {
                ...commonOptions.plugins,
                legend: {
                    ...commonOptions.plugins.legend,
                    position: 'bottom'
                },
                tooltip: {
                    ...commonOptions.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                            return `${context.label}: ${formatCurrency(value)} (${percentage}%)`;
                        }
                    }
                }
            }
        };
        
        initChart('revenueVsExpenditureChart', 'pie', chartData, options);
    };

    /**
     * QUOTES VS INVOICES CHART
     */
    const setupQuotesVsInvoicesChart = () => {
        const canvas = document.getElementById('quotesVsInvoicesChart');
        if (!canvas) return;
        
        const updateChart = (metric) => {
            let data, labels;
            
        switch(metric) {
            case 'amount':
                    data = [
                        parseFloat(canvas.dataset.quotesAmount || 0),
                        parseFloat(canvas.dataset.invoicesAmount || 0)
                    ];
                    labels = ['Quotes Value', 'Invoices Value'];
                break;
            case 'average':
                    const quotesCount = parseInt(canvas.dataset.quotes || 1);
                    const invoicesCount = parseInt(canvas.dataset.invoices || 1);
                    const quotesAmount = parseFloat(canvas.dataset.quotesAmount || 0);
                    const invoicesAmount = parseFloat(canvas.dataset.invoicesAmount || 0);
                    
                    data = [
                        quotesCount > 0 ? quotesAmount / quotesCount : 0,
                        invoicesCount > 0 ? invoicesAmount / invoicesCount : 0
                    ];
                    labels = ['Average Quote', 'Average Invoice'];
                    break;
                default: // count
                    data = [
                        parseInt(canvas.dataset.quotes || 0),
                        parseInt(canvas.dataset.invoices || 0)
                    ];
                    labels = ['Quotes', 'Invoices'];
                break;
            }
            
            // Create gradients
            const ctx = canvas.getContext('2d');
            const quoteGradient = createGradient(ctx, 'rgba(37, 99, 235, 0.8)', 'rgba(37, 99, 235, 0.1)');
            const invoiceGradient = createGradient(ctx, 'rgba(16, 185, 129, 0.8)', 'rgba(16, 185, 129, 0.1)');
            
            const chartData = {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [quoteGradient, invoiceGradient],
                    borderRadius: 6,
                    borderSkipped: false,
                    barPercentage: 0.7
                }]
            };
            
            initChart('quotesVsInvoicesChart', 'bar', chartData, commonOptions);
            
            // Update chart title if needed
            const chartTitle = document.querySelector('.quotes-vs-invoices-title');
            if (chartTitle) {
                chartTitle.textContent = `Quotes vs Invoices - ${metric.charAt(0).toUpperCase() + metric.slice(1)}`;
            }
        };
        
        // Initialize with default metric
        updateChart('count');
        
        // Add event listener for metric change
    const metricSelector = document.getElementById('quotesVsInvoicesMetric');
    if (metricSelector) {
        metricSelector.addEventListener('change', function(e) {
                updateChart(e.target.value);
            });
        }
    };

    /**
     * INITIALIZE ALL CHARTS
     */
    const initializeAllCharts = () => {
        console.log('Initializing statistics page charts');
        
        // Disable any existing charts to prevent conflicts
        if (window.Chart) {
            Chart.helpers.each(Chart.instances, function(instance) {
                instance.destroy();
            });
        }
        
        setupQuotesVsInvoicesChart();
        setupRevenueVsExpenditureChart();
    };
    
    // Start chart initialization with a small delay to ensure DOM is fully loaded
    setTimeout(initializeAllCharts, 100);
}); 