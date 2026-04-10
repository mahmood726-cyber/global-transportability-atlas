import numpy as np

def calculate_smd(target_mean, source_mean, source_sd):
    """
    Standardized Mean Difference (SMD) for a single covariate.
    """
    return (target_mean - source_mean) / source_sd

def recalibrate_hr(original_hr, smds, coefficients):
    """
    Recalibrate Hazard Ratio based on covariate drift.
    Logic: log(HR_new) = log(HR_old) + sum(coef_i * smd_i)
    """
    log_hr = np.log(original_hr)
    drift = np.sum(np.array(coefficients) * np.array(smds))
    return np.exp(log_hr + drift)

def calculate_oe_ratio(recalibrated_hr, reference_hr=1.0):
    """
    Observed-to-Expected (O:E) Ratio proxy.
    """
    return recalibrated_hr / reference_hr

if __name__ == "__main__":
    # Example for USA -> IND transportability
    original_hr = 0.82
    # SMDs for Pop_65plus, Urbanization, Health_Exp
    smds = [3.16, -2.5, -1.8] 
    coeffs = [0.15, 0.05, 0.12] # Estimated sensitivity of HR to covariate drift
    
    new_hr = recalibrate_hr(original_hr, smds, coeffs)
    oe = calculate_oe_ratio(new_hr, original_hr)
    
    print(f"Original HR: {original_hr}")
    print(f"Recalibrated HR: {new_hr:.4f}")
    print(f"O:E Ratio Proxy: {oe:.4f}")
