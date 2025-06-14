let chart = null;

function formatAmount(amount) {
    return new Intl.NumberFormat('en-US').format(amount) + ' RWF';
}

function updateTable(transactions) {
    const tbody = document.querySelector('#transactions-table tbody');
    tbody.innerHTML = '';
    
    transactions.forEach(tx => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${tx.type}</td>
            <td>${formatAmount(tx.amount)}</td>
            <td>${tx.date}</td>
            <td>${tx.name || 'N/A'}</td>
            <td><details><summary>Show Details</summary>
                <div class="transaction-details">
                    <p><strong>Message:</strong> ${tx.body}</p>
                    <p><strong>Address:</strong> ${tx.address}</p>
                    <p><strong>Readable Date:</strong> ${tx.readable_date}</p>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function updateChart(chartData) {
    if (chart) {
        chart.destroy();
    }

    const ctx = document.getElementById('chart').getContext('2d');
    const colorMap = {
        'incoming': '#FF6384',
        'payment': '#36A2EB',
        'transfer': '#FFCE56',
        'deposit': '#4BC0C0',
        'airtime': '#9966FF',
    //     'cash_power': '#FF9F40',
    //     'withdrawal': '#2ECC71',
    //     'other': '#7F8C8D'
    // };

    // const backgroundColor = chartData.labels.map(label => colorMap[label] || '#FF6384');

    // chart = new Chart(ctx, {
    //     type: 'pie',
    //     data: {
    //         labels: chartData.labels,
            datasets: [{
                data: chartData.values,
                backgroundColor: backgroundColor
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        generateLabels: function(chart) {
                            const data = chart.data;
                            return data.labels.map((label, i) => ({
                                text: `${label} (${data.datasets[0].data[i]})`,
                                fillStyle: data.datasets[0].backgroundColor[i],
                                hidden: isNaN(data.datasets[0].data[i]) || data.datasets[0].data[i] === 0,
                                lineCap: 'butt',
                                lineDash: [],
                                lineDashOffset: 0,
                                lineJoin: 'miter',
                                lineWidth: 1,
                                strokeStyle: '#fff',
                                pointStyle: 'circle',
                                rotation: 0
                            }));
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Transaction Distribution'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const amount = chartData.amounts[context.dataIndex] || 0;
                            return [
                                `${label}: ${value} transactions`,
                                `Total: ${formatAmount(amount)}`
                            ];
                        }
                    }
                }
            }
        }
    });
}

function updateStats(totalCount, totalAmount) {
    document.getElementById('total-count').textContent = totalCount;
    document.getElementById('total-amount').textContent = formatAmount(totalAmount);
}

function populateNameFilter(names) {
    const nameFilter = document.getElementById('filter-name');
    const currentValue = nameFilter.value; // Store current selection
    
    // Clear existing options except the first one
    while (nameFilter.options.length > 1) {
        nameFilter.remove(1);
    }
    
    // Sort names alphabetically
    names.sort();
    
    // Add new options
    names.forEach(name => {
        if (name) {  // Only add non-null and non-empty names
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            nameFilter.appendChild(option);
        }
    });

    // Restore previous selection if it still exists
    if (currentValue && names.includes(currentValue)) {
        nameFilter.value = currentValue;
    }
}

async function fetchData() {
    try {
        const type = document.getElementById('filter-type').value;
        const name = document.getElementById('filter-name').value;
        
        // Show loading state
        document.body.classList.add('loading');
        
        const response = await fetch(`/data?type=${encodeURIComponent(type)}&name=${encodeURIComponent(name)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            console.error('Server error:', data.error);
            return;
        }
        
        // Update all visualizations
        updateTable(data.transactions);
        updateChart(data.chart_data);
        updateStats(data.total_count, data.total_amount);
        
        // Update name filter options
        if (data.names && data.names.length > 0) {
            populateNameFilter(data.names);
        }
    } catch (error) {
        console.error('Error fetching data:', error);
    } finally {
        // Remove loading state
        document.body.classList.remove('loading');
    }
}

// Add debounce function to prevent too many rapid requests
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Use debounced version of fetchData for filter changes
const debouncedFetchData = debounce(fetchData, 250);

document.getElementById('filter-type').addEventListener('change', debouncedFetchData);
document.getElementById('filter-name').addEventListener('change', debouncedFetchData);

// Initial load
fetchData();
