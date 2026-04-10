document.addEventListener('DOMContentLoaded', () => {
    const map = L.map('map').setView([20, 0], 2);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { 
        attribution: '&copy; CARTO' 
    }).addTo(map);

    const btnCompute = document.getElementById('btnCompute');
    const globalScore = document.getElementById('globalScore');
    const centroids = { 
        'USA': [38, -97], 'IND': [20, 77], 'NGA': [9, 8], 
        'KEN': [0, 38], 'BRA': [-14, -51], 'CHN': [35, 105], 'ZAF': [-30, 25] 
    };

    const ctxForest = document.getElementById('forestChart').getContext('2d');
    const forestChart = new Chart(ctxForest, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Recalibrated HR',
                data: [],
                backgroundColor: '#a855f7',
                barThickness: 8
            }]
        },
        options: {
            indexAxis: 'y', responsive: true, maintainAspectRatio: false,
            scales: {
                x: { min: 0.5, max: 2.0, grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                y: { grid: { color: '#334155' }, ticks: { color: '#f8fafc' } }
            },
            plugins: { legend: { display: false } }
        }
    });

    const ctxRadar = document.getElementById('radarChart').getContext('2d');
    const radarChart = new Chart(ctxRadar, {
        type: 'radar',
        data: {
            labels: ['Age 65+', 'Urbanization', 'Health Exp', 'Beds'],
            datasets: [{
                label: 'Trial Population (USA)',
                data: [16.5, 82.0, 16.7, 2.8],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)'
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: {
                r: { angleLines: { color: '#334155' }, grid: { color: '#334155' }, pointLabels: { color: '#94a3b8' }, ticks: { display: false } }
            },
            plugins: { legend: { labels: { color: '#f8fafc' } } }
        }
    });

    const updateDashboard = (data) => {
        const sorted = [...data.map_data].sort((a, b) => a.recalibrated_hr - b.recalibrated_hr);
        
        forestChart.data.labels = sorted.map(d => d.iso3);
        forestChart.data.datasets[0].data = sorted.map(d => d.recalibrated_hr);
        forestChart.update();

        const avgProp = data.map_data.reduce((s, d) => s + d.transport_propensity, 0) / data.map_data.length;
        globalScore.textContent = (avgProp * 100).toFixed(0) + '%';
        globalScore.style.color = avgProp > 0.7 ? '#10b981' : avgProp > 0.4 ? '#fbbf24' : '#ef4444';

        data.map_data.forEach(c => {
            const coord = centroids[c.iso3];
            if (!coord) return;

            let color = c.transport_propensity > 0.7 ? '#10b981' : c.transport_propensity > 0.4 ? '#fbbf24' : '#ef4444';
            
            L.circleMarker(coord, {
                radius: 5 + (c.readiness_score / 10),
                fillColor: color, color: color, weight: 1, fillOpacity: 0.6
            }).addTo(map)
              .bindPopup(`
                <b>${c.iso3}</b><br>
                Propensity: ${(c.transport_propensity*100).toFixed(1)}%<br>
                Recalibrated HR: ${c.recalibrated_hr.toFixed(2)}<br>
                95% CI: [${c.hr_ci[0].toFixed(2)}, ${c.hr_ci[1].toFixed(2)}]<br>
                Health Readiness: ${c.readiness_score}%
              `).on('click', () => {
                  if(radarChart.data.datasets.length > 1) radarChart.data.datasets.pop();
                  radarChart.data.datasets.push({
                      label: `${c.iso3} Target`,
                      data: [c.covariates.pop_65plus, c.covariates.urbanization, c.covariates.health_exp, c.covariates.beds],
                      borderColor: '#a855f7',
                      backgroundColor: 'rgba(168, 85, 247, 0.1)'
                  });
                  radarChart.update();
              });
        });
    };

    btnCompute.addEventListener('click', async () => {
        const resp = await fetch('data/atlas_results.json');
        const data = await resp.json();
        updateDashboard(data);
    });

    btnCompute.click();
});
