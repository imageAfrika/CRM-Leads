document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    
    // Comprehensive logging and error handling
    try {
        // Ensure Chart.js is loaded
        if (typeof Chart === 'undefined') {
            throw new Error('Chart.js is not loaded');
        }

        // Verify chart data exists
        if (!window.chartData) {
            throw new Error('No chart data found in window object');
        }

        // Function to safely parse chart data
        function parseChartData(rawData) {
            if (typeof rawData === 'string') {
                try {
                    return JSON.parse(rawData);
                } catch (parseError) {
                    console.error('Failed to parse chart data:', parseError);
                    return null;
                }
            }
            return rawData;
        }

        // Fallback data with minimal structure
        const fallbackData = {
            labels: ['No Data'],
            datasets: [{
                label: 'No Data Available',
                data: [0],
                backgroundColor: 'rgba(200,200,200,0.5)'
            }]
        };

        // Safely extract and parse chart data
        const quotesInvoicesData = parseChartData(window.chartData.quotes_invoices_data) || fallbackData;
        const revenueExpenditureData = parseChartData(window.chartData.revenue_expenditure_data) || fallbackData;
        const purchasesSalesData = parseChartData(window.chartData.purchases_sales_data) || fallbackData;
        const monthlyTrendsData = parseChartData(window.chartData.monthly_trends_data) || fallbackData;

        // Consistent chart options
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: false
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
                        color: 'rgba(0,0,0,0.05)'
                    }
                }
            }
        };

        // Create charts with error handling
        function createChart(canvasId, type, data) {
            const ctx = document.getElementById(canvasId);
            if (!ctx) {
                console.error(`Canvas ${canvasId} not found`);
                return null;
            }

            try {
                console.log(`Creating chart ${canvasId} with type ${type}`);
                return new Chart(ctx, {
                    type: type,
                    data: data,
                    options: defaultOptions
                });
            } catch (chartError) {
                console.error(`Error creating chart ${canvasId}:`, chartError);
                return null;
            }
        }

        // Log parsed data for debugging
        console.log('Parsed Quotes vs Invoices Data:', quotesInvoicesData);
        console.log('Parsed Revenue vs Expenditure Data:', revenueExpenditureData);
        console.log('Parsed Purchases vs Sales Data:', purchasesSalesData);
        console.log('Parsed Monthly Trends Data:', monthlyTrendsData);

        // Attempt to create all charts
        const charts = {
            quotesInvoices: createChart('quotesInvoicesChart', 'pie', quotesInvoicesData),
            revenueExpenditure: createChart('revenueExpenditureChart', 'bar', revenueExpenditureData),
            purchasesSales: createChart('purchasesSalesChart', 'bar', purchasesSalesData),
            monthlyTrends: createChart('monthlyTrendsChart', 'line', monthlyTrendsData)
        };

        // Log chart creation results
        Object.entries(charts).forEach(([name, chart]) => {
            if (chart) {
                console.log(`${name} chart created successfully`);
            } else {
                console.error(`${name} chart failed to create`);
            }
        });

        console.log('Chart initialization complete');

    } catch (error) {
        console.error('Critical error in chart initialization:', error);
    }
});