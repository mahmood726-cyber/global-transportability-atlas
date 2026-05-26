document.addEventListener("DOMContentLoaded", () => {
    const map = L.map("map").setView([20, 0], 2);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        attribution: "&copy; CARTO",
    }).addTo(map);

    const btnCompute = document.getElementById("btnCompute");
    const modeSelector = document.getElementById("analysisMode");
    const globalScore = document.getElementById("globalScore");

    const modeConfig = {
        effect_ratio: { label: "Effect Ratio", color: "#a855f7", min: 0, max: null },
        transportability_score: { label: "Transportability Score", color: "#10b981", min: 0, max: 1 },
        priority_score: { label: "Priority Score", color: "#f97316", min: 0, max: 100 },
    };

    let appData = null;
    let markers = [];

    const ctxForest = document.getElementById("forestChart").getContext("2d");
    const forestChart = new Chart(ctxForest, {
        type: "bar",
        data: {
            labels: [],
            datasets: [
                {
                    label: "Effect Ratio",
                    data: [],
                    backgroundColor: "#a855f7",
                    barThickness: 8,
                },
            ],
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { min: 0, grid: { color: "#334155" }, ticks: { color: "#94a3b8" } },
                y: { grid: { color: "#334155" }, ticks: { color: "#f8fafc" } },
            },
            plugins: { legend: { display: false } },
        },
    });

    const ctxRadar = document.getElementById("radarChart").getContext("2d");
    const radarChart = new Chart(ctxRadar, {
        type: "radar",
        data: {
            labels: ["Age 65+", "Life Exp", "Health Exp PC (k)", "Physicians / 1k"],
            datasets: [
                {
                    label: "Matrix Mean",
                    data: [0, 0, 0, 0],
                    borderColor: "#3b82f6",
                    backgroundColor: "rgba(59, 130, 246, 0.1)",
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: "#334155" },
                    grid: { color: "#334155" },
                    pointLabels: { color: "#94a3b8" },
                    ticks: { display: false },
                },
            },
            plugins: { legend: { labels: { color: "#f8fafc" } } },
        },
    });

    function toNumber(value, fallback = 0) {
        const parsed = Number(value);
        return Number.isFinite(parsed) ? parsed : fallback;
    }

    function formatValue(value, digits = 2) {
        const parsed = Number(value);
        return Number.isFinite(parsed) ? parsed.toFixed(digits) : "n/a";
    }

    function getRadarValues(covariates) {
        return [
            toNumber(covariates.age_65up),
            toNumber(covariates.life_exp),
            toNumber(covariates.hexp_pc) / 1000,
            toNumber(covariates.physicians),
        ];
    }

    function setReferenceProfile(profile) {
        if (!profile) {
            return;
        }
        radarChart.data.datasets[0].label = profile.label || "Matrix Mean";
        radarChart.data.datasets[0].data = [
            toNumber(profile.age_65up),
            toNumber(profile.life_exp),
            toNumber(profile.hexp_pc) / 1000,
            toNumber(profile.physicians),
        ];
        radarChart.update();
    }

    function updateDashboard() {
        if (!appData) {
            return;
        }

        const dataKey = modeSelector.value;
        const config = modeConfig[dataKey];
        const sorted = [...appData.map_data].sort((a, b) => toNumber(a[dataKey]) - toNumber(b[dataKey]));

        forestChart.data.labels = sorted.map((d) => d.iso3);
        forestChart.data.datasets[0].label = config.label;
        forestChart.data.datasets[0].data = sorted.map((d) => toNumber(d[dataKey]));
        forestChart.data.datasets[0].backgroundColor = config.color;
        forestChart.options.scales.x.min = config.min;
        if (config.max !== null) {
            forestChart.options.scales.x.max = config.max;
        } else {
            const maxValue = Math.max(...sorted.map((d) => toNumber(d[dataKey], 0)), 1);
            forestChart.options.scales.x.max = Math.ceil(maxValue * 1.15 * 100) / 100;
        }
        forestChart.update();

        const avgScore =
            appData.map_data.reduce((sum, row) => sum + toNumber(row.transportability_score), 0) /
            Math.max(appData.map_data.length, 1);
        globalScore.textContent = `${(avgScore * 100).toFixed(0)}%`;

        markers.forEach((marker) => map.removeLayer(marker));
        markers = [];

        appData.map_data.forEach((country) => {
            const coord = country.spatial_metrics && country.spatial_metrics.coordinates;
            if (!Array.isArray(coord) || coord.length !== 2) {
                return;
            }

            const score = toNumber(country.transportability_score);
            const gap = toNumber(country.evidence_gap);
            const priority = toNumber(country.priority_score);
            const color = score > 0.75 ? "#10b981" : score > 0.5 ? "#fbbf24" : "#ef4444";
            const radius = 5 + priority / 20;

            const marker = L.circleMarker(coord, {
                radius,
                fillColor: color,
                color,
                weight: 1,
                fillOpacity: 0.65,
            })
                .addTo(map)
                .bindPopup(`
                    <b style="color:${config.color};">${country.country_name} (${country.iso3})</b><br>
                    Region: ${country.region || "Unknown"}<br>
                    Transportability score: ${formatValue(score, 3)}<br>
                    Evidence gap: ${formatValue(gap, 3)}<br>
                    Priority score: ${formatValue(priority, 1)}<br>
                    Effect ratio: ${formatValue(country.effect_ratio, 2)}${
                        Array.isArray(country.effect_ci)
                            ? ` [${formatValue(country.effect_ci[0], 2)}, ${formatValue(country.effect_ci[1], 2)}]`
                            : ""
                    }<br>
                    E-value: ${formatValue(country.e_value, 2)}<br>
                    Population: ${formatValue(country.covariates.population / 1e6, 1)}M<br>
                    Health exp pc: ${formatValue(country.covariates.hexp_pc, 0)}<br>
                    Physicians / 1k: ${formatValue(country.covariates.physicians, 2)}
                `)
                .on("click", () => {
                    if (radarChart.data.datasets.length > 1) {
                        radarChart.data.datasets.pop();
                    }
                    radarChart.data.datasets.push({
                        label: `${country.iso3} profile`,
                        data: getRadarValues(country.covariates),
                        borderColor: config.color,
                        backgroundColor: "rgba(168, 85, 247, 0.1)",
                    });
                    radarChart.update();
                });

            markers.push(marker);
        });

        if (markers.length > 0) {
            const bounds = L.featureGroup(markers).getBounds();
            if (bounds.isValid()) {
                map.fitBounds(bounds.pad(0.2));
            }
        }
    }

    btnCompute.addEventListener("click", async () => {
        const response = await fetch("data/atlas_results.json");
        appData = await response.json();
        setReferenceProfile(appData.reference_profile);
        updateDashboard();
    });

    modeSelector.addEventListener("change", updateDashboard);

    btnCompute.click();
});
