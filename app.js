document.addEventListener('DOMContentLoaded', () => {
    const map = L.map('map').setView([20, 0], 2);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { 
        attribution: '&copy; CARTO' 
    }).addTo(map);

    const btnCompute = document.getElementById('btnCompute');
    const modeSelector = document.getElementById('analysisMode');
    const globalScore = document.getElementById('globalScore');
    const centroids = { 
        'USA': [38, -97], 'IND': [20, 77], 'NGA': [9, 8], 
        'KEN': [0, 38], 'BRA': [-14, -51], 'CHN': [35, 105], 'ZAF': [-30, 25] 
    };

    let appData = null;
    let markers = [];

    const ctxForest = document.getElementById('forestChart').getContext('2d');
    const forestChart = new Chart(ctxForest, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Hazard Ratio',
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

    const updateDashboard = () => {
        if (!appData) return;
        const dataKey = modeSelector.value;
        const isDML = dataKey === 'dml_hr';
        const isCausal = dataKey === 'causal_hr';
        
        // Update Chart
        const sorted = [...appData.map_data].sort((a, b) => a[dataKey] - b[dataKey]);
        forestChart.data.labels = sorted.map(d => d.iso3);
        forestChart.data.datasets[0].data = sorted.map(d => d[dataKey]);
        forestChart.data.datasets[0].backgroundColor = isDML ? '#3b82f6' : (isCausal ? '#10b981' : '#a855f7');
        forestChart.update();

        // Update Score
        const avgProp = appData.map_data.reduce((s, d) => s + d.transport_propensity, 0) / appData.map_data.length;
        globalScore.textContent = (avgProp * 100).toFixed(0) + '%';
        
        // Update Markers
        markers.forEach(m => map.removeLayer(m));
        markers = [];

        appData.map_data.forEach(c => {
            const coord = centroids[c.iso3];
            if (!coord) return;

            let color = c.transport_propensity > 0.7 ? '#10b981' : c.transport_propensity > 0.4 ? '#fbbf24' : '#ef4444';
            
            const marker = L.circleMarker(coord, {
                radius: 5 + (c.readiness_score / 10),
                fillColor: color, color: color, weight: 1, fillOpacity: 0.6
            }).addTo(map)
              .bindPopup(`
                <b style="color:${isDML ? '#3b82f6' : (isCausal ? '#10b981' : '#a855f7')};">${c.iso3} | ${modeSelector.options[modeSelector.selectedIndex].text}</b><br>
                Niche Overlap (Ecol): ${(c.niche_overlap * 100).toFixed(1)}%<br>
                <b>HR: ${c[dataKey].toFixed(2)}</b> [${c.conformal_ci[0].toFixed(2)}, ${c.conformal_ci[1].toFixed(2)}]<br>
                <i>Eddington Corr (Astro): ${c.noise_corr_hr.toFixed(2)}</i><br>
                E-stat (Strength): ${c.e_statistic.toFixed(2)}<br>
                RD E-value (Abs Sens): ${c.rd_e_value.toFixed(2)}<br>
                <b style="color:#f87171;">Proximal Bound: [${c.proximal_bound[0].toFixed(2)}, ${c.proximal_bound[1].toFixed(2)}]</b><br>
                Health Readiness: ${c.readiness_score}%
              `).on('click', () => {
                  if(radarChart.data.datasets.length > 1) radarChart.data.datasets.pop();
                  radarChart.data.datasets.push({
                      label: `${c.iso3} Target`,
                      data: [c.covariates.pop_65plus, c.covariates.urbanization, c.covariates.health_exp, c.covariates.beds],
                      borderColor: isDML ? '#3b82f6' : (isCausal ? '#10b981' : '#a855f7'),
                      backgroundColor: 'rgba(168, 85, 247, 0.1)'
                  });
                  radarChart.update();
              });
            markers.push(marker);
        });
    };

    btnCompute.addEventListener('click', async () => {
        const resp = await fetch('data/atlas_results.json');
        appData = await resp.json();
        updateDashboard();
    });

    modeSelector.addEventListener('change', updateDashboard);

    btnCompute.click();
});
