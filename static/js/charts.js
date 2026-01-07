const { jsx } = require("react/jsx-runtime");

document.addEventListener('DOMContentLoaded', function () {
    if (!window.chartData) return;

    const data = window.chartData;

    const moodCtx = document.getElementById('moodChart').getContext('2d');
    const moodLabels = Object.keys(data.mood_counts);
    const moodValues = Object.values(data.mood_counts);

    const moodColors = {
        'Happy': '#f6e05e',
        'Neutral': '#cbd5e0',
        'Stressed': '#fc8181',
        'Tired': '#90cdf4',
        'Sad': '#63b3ed'
    };

    const backgroundColors = moodLabels.map(label => moodColors[label] || '#cbd5e0');

    new Chart(moodCtx, {
        type: 'bar',
        data: {
            labels: moodLabels,
            datasets: [{
                label: 'Frequency',
                data: moodValues,
                backgroundColor: backgroundColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } }
            }
        }
    });

    const energyCtx = document.getElementById('energyChart').getContext('2d');
    new Chart(energyCtx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [{
                label: 'Energy Level',
                data: data.energies,
                borderColor: '#68d391',
                backgroundColor: 'rgba(104, 211, 145, 0.2)',
                tension: 0.3,
                fill: true,
                yAxisID: 'y'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 4,
                    ticks: {
                        callback: function (value) {
                            if (value === 1) return 'Low';
                            if (value === 2) return 'Medium';
                            if (value === 3) return 'High';
                            return '';
                        }
                    }
                }
            }
        }
    });
});