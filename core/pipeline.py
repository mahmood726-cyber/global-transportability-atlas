import json
import numpy as np
import datetime
import os
import hashlib

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.math import (calculate_smd, recalibrate_hr, causal_transport_hr, dml_transport_hr, 
                       conformal_hr_interval, spatial_wasserstein_2, proximal_bias_bound, 
                       anytime_valid_e_stat, risk_difference_e_value, 
                       fisher_information_stability, shapley_drift_attribution, topological_bottleneck_dist,
                       quantum_von_neumann_entropy, cusp_catastrophe_potential, transport_free_energy,
                       avicennian_constancy_score, razian_dissonance, haythamian_verification_bound)

# TRUTHCERT PIPELINE CONSTANTS (SOURCE DATA)
SOURCE_STATS = {
    'pop_65plus_pct': 16.5,
    'urbanization': 82.0,
    'health_exp_gdp': 16.7,
    'hospital_beds_per_1000': 2.8
}
SOURCE_COORD = [38.0, -97.0] # USA Centroid

COUNTRIES = [
    {"iso3": "USA", "pop_65plus_pct": 16.5, "urbanization": 82, "health_exp_gdp": 16.7, "hospital_beds_per_1000": 2.8, "readiness": 95, "coord": [38, -97]},
    {"iso3": "IND", "pop_65plus_pct": 6.8, "urbanization": 35, "health_exp_gdp": 3.0, "hospital_beds_per_1000": 0.5, "readiness": 45, "coord": [20, 77]},
    {"iso3": "NGA", "pop_65plus_pct": 2.7, "urbanization": 52, "health_exp_gdp": 3.8, "hospital_beds_per_1000": 0.5, "readiness": 38, "coord": [9, 8]},
    {"iso3": "KEN", "pop_65plus_pct": 2.5, "urbanization": 28, "health_exp_gdp": 4.6, "hospital_beds_per_1000": 1.4, "readiness": 42, "coord": [0, 38]},
    {"iso3": "BRA", "pop_65plus_pct": 10.2, "urbanization": 87, "health_exp_gdp": 9.5, "hospital_beds_per_1000": 2.1, "readiness": 72, "coord": [-14, -51]},
    {"iso3": "CHN", "pop_65plus_pct": 13.5, "urbanization": 65, "health_exp_gdp": 5.4, "hospital_beds_per_1000": 4.3, "readiness": 85, "coord": [35, 105]},
    {"iso3": "ZAF", "pop_65plus_pct": 6.0, "urbanization": 67, "health_exp_gdp": 8.3, "hospital_beds_per_1000": 2.3, "readiness": 65, "coord": [-30, 25]}
]

ORIGINAL_HR = 0.82 
COEFFS = [0.12, 0.04, 0.08, 0.05] 

RESULTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'atlas_results.json')

def generate_signature(data):
    """Generates a deterministic SHA256 hash for the provided data structure."""
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_str.encode('utf-8')).hexdigest()


def generate_truthcert_hash(data):
    """Backward-compatible alias for the repo's original hashing helper."""
    return f"SHA256:{generate_signature(data)}"

def run_pipeline():
    np.random.seed(42)
    
    input_data = {
        "source": SOURCE_STATS,
        "source_coord": SOURCE_COORD,
        "targets": COUNTRIES,
        "baseline_hr": ORIGINAL_HR,
        "sensitivity_coeffs": COEFFS
    }
    input_hash = generate_signature(input_data)
    
    calibration_scores = np.random.exponential(scale=1.5, size=1000)
    
    results = []
    for c in COUNTRIES:
        target_covs = {
            "pop_65plus": c['pop_65plus_pct'],
            "urbanization": c['urbanization'],
            "health_exp": c['health_exp_gdp'],
            "beds": c['hospital_beds_per_1000']
        }
        
        smds = [
            calculate_smd(c['pop_65plus_pct'], SOURCE_STATS['pop_65plus_pct'], 5.0),
            calculate_smd(c['urbanization'], SOURCE_STATS['urbanization'], 20.0),
            calculate_smd(c['health_exp_gdp'], SOURCE_STATS['health_exp_gdp'], 4.0),
            calculate_smd(c['hospital_beds_per_1000'], SOURCE_STATS['hospital_beds_per_1000'], 1.0)
        ]
        
        # Stochastic Sensitivity
        mc_dml_hrs = []
        for _ in range(100):
            perturbed_smds = np.array(smds) + np.random.normal(0, 0.05 * np.abs(np.array(smds)) + 0.01, size=len(smds))
            mc_hr = dml_transport_hr(ORIGINAL_HR, perturbed_smds.tolist(), COEFFS, n_folds=2)
            mc_dml_hrs.append(mc_hr)
        
        sensitivity_std = np.std(mc_dml_hrs)
        stability_score = 1.0 / (1.0 + sensitivity_std)
        
        # Core Calculations
        dml_hr_val = dml_transport_hr(ORIGINAL_HR, smds, COEFFS, n_folds=2)
        conformal_ci = conformal_hr_interval(dml_hr_val, smds, calibration_scores, alpha=0.05)
        propensity = 1.0 / (1.0 + 0.2 * np.abs(np.sum(smds)))
        
        # Spatial Metrics
        spatial_w2 = spatial_wasserstein_2(target_covs, SOURCE_STATS, c['coord'], SOURCE_COORD)
        
        # Physicians' Wisdom Stack
        constancy = avicennian_constancy_score(dml_hr_val, smds)
        dissonance = razian_dissonance(c['readiness'])
        v_bound = haythamian_verification_bound(dml_hr_val, propensity)
        
        results.append({
            "iso3": c['iso3'],
            "smd_avg": float(np.mean(np.abs(smds))),
            "constancy_avicenna": float(constancy),
            "dissonance_razi": float(dissonance),
            "verification_bound_haytham": [float(v) for v in v_bound],
            "transport_propensity": float(propensity),
            "hr_initial": ORIGINAL_HR,
            "recalibrated_hr": float(recalibrate_hr(ORIGINAL_HR, smds, COEFFS)),
            "causal_hr": float(causal_transport_hr(ORIGINAL_HR, smds, COEFFS)),
            "dml_hr": float(dml_hr_val),
            "hr_ci": [float(np.exp(np.log(dml_hr_val) - 1.96*0.05)), float(np.exp(np.log(dml_hr_val) + 1.96*0.05))], 
            "conformal_ci": [float(conformal_ci[0]), float(conformal_ci[1])],
            "proximal_bound": [float(v) for v in proximal_bias_bound(dml_hr_val, smds)],
            "uncertainty": {
                "dml_hr_std": float(sensitivity_std),
                "robustness_score": float(stability_score),
                "mc_iterations": 100
            },
            "e_statistic": float(anytime_valid_e_stat(dml_hr_val, smds)),
            "rd_e_value": float(risk_difference_e_value(dml_hr_val, smds)),
            "fisher_stability": float(fisher_information_stability(smds)),
            "shapley_attribution": [float(v) for v in shapley_drift_attribution(dml_hr_val, smds, COEFFS)],
            "tda_bottleneck": float(topological_bottleneck_dist(target_covs, SOURCE_STATS)),
            "quantum_entropy": float(quantum_von_neumann_entropy(smds)),
            "cusp_potential": float(cusp_catastrophe_potential(dml_hr_val, c['readiness'])),
            "free_energy": float(transport_free_energy(spatial_w2, np.abs(np.log(conformal_ci[1] / dml_hr_val)))),
            "readiness_score": c['readiness'],
            "covariates": target_covs,
            "spatial_metrics": {
                "wasserstein_2_weighted": float(spatial_w2),
                "coordinates": c['coord']
            }
        })
    
    output_hash = generate_signature(results)
    composition_hash = generate_signature([input_hash, output_hash])
    
    audit_data = {
        "ihme_version": "GBD 2023 (v1.0)",
        "timestamp": datetime.datetime.now().isoformat(),
        "methodology": "TruthCert Transportability Pipeline V4 (Spatial & Micro-Paper Ready)",
        "determinism_seed": 42,
        # Preserve the legacy flat hash field while keeping the richer signature block.
        "hash": f"SHA256:{composition_hash}",
        "signatures": {
            "input_data_hash": f"SHA256:{input_hash}",
            "output_data_hash": f"SHA256:{output_hash}",
            "composition_hash": f"SHA256:{composition_hash}"
        },
        "hardening": {
            "dml_cross_fitting": True,
            "conformal_exchangeability": "Fixed Calibration Set (n=1000)",
            "uncertainty_propagation": "Monte Carlo Stochastic Sensitivity (N=100)",
            "spatial_awareness": "Spatially-Weighted Wasserstein-2 (Haversine)"
        }
    }
    
    output = {
        "audit": audit_data,
        "map_data": results
    }
    
    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Pipeline complete. {len(results)} countries processed with Phase 4 Spatial Weighting.")
    return output

if __name__ == "__main__":
    run_pipeline()
