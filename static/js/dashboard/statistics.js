document.addEventListener('DOMContentLoaded', function() {
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    boxWidth: 12,
                    padding: 10,
                    font: {
                        size: 11
                    }
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    font: {
                        size: 10
                    },
                    maxRotation: 45,
                    minRotation: 45
                }
            },
            y: {
                beginAtZero: true,
                ticks: {
                    font: {
                        size: 10
                    }
                }
            }
        }
    };

    const quotesVsInvoicesChart = new Chart(
        document.getElementById('quotesVsInvoicesChart'),
        {
            type: 'bar',
            options: {
                ...chartOptions,
                scales: {
                    ...chartOptions.scales,
                    y: {
                        ...chartOptions.scales.y,
                        title: {
                            display: true,
                            text: 'Count',
                            font: {
                                size: 10
                            }
                        }
                    }
                }
            }
        }
    );

    const revenueVsExpenditureChart = new Chart(
        document.getElementById('revenueVsExpenditureChart'),
        {
            type: 'line',
            options: {
                ...chartOptions,
                scales: {
                    ...chartOptions.scales,
                    y: {
                        ...chartOptions.scales.y,
                        title: {
                            display: true,
                            text: 'Amount ($)',
                            font: {
                                size: 10
                            }
                        }
                    }
                }
            }
        }
    );

    function updateCharts(period) {
        fetch(`/dashboard/api/chart-data/?period=${period}`)
            .then(response => response.json())
            .then(data => {
                // Update Quotes vs Invoices Chart
                quotesVsInvoicesChart.data = {
                    labels: data.labels,
                    datasets: [
                        {
                            label: 'Quotes',
                            data: data.quotes_data,
                            backgroundColor: '#1976d2',
                        },
                        {
                            label: 'Invoices',
                            data: data.invoices_data,
                            backgroundColor: '#2e7d32',
                        }
                    ]
                };
                quotesVsInvoicesChart.update();

                // Update Revenue vs Expenditure Chart
                revenueVsExpenditureChart.data = {
                    labels: data.labels,
                    datasets: [
                        {
                            label: 'Revenue',
                            data: data.revenue_data,
                            borderColor: '#f57c00',
                            fill: false,
                        },
                        {
                            label: 'Expenditure',
                            data: data.expenditure_data,
                            borderColor: '#c62828',
                            fill: false,
                        }
                    ]
                };
                revenueVsExpenditureChart.update();
            });
    }

    // Handle period changes
    document.getElementById('timePeriod').addEventListener('change', function(e) {
        updateCharts(e.target.value);
    });

    // Initial load
    updateCharts('month');
}); 