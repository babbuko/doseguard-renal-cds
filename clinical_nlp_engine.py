"""
Clinical NLP & Renal Decision Support Engine
Course: ITAI 2372 - Artificial Intelligence Applications (Module 03)
Author: Kamron Robinson

Purpose:
Extracts clinical parameters from unformatted clinical notes using NLP regular expressions,
calculates Creatinine Clearance (CrCl) via the Cockcroft-Gault equation, and evaluates
orders against a high-risk nephrotoxic formulary to reduce alert fatigue.
"""

import re
from typing import Dict, Any, Optional

# ==============================================================================
# Clinical Knowledge Base: High-Risk Renally-Cleared Formulary
# ==============================================================================
RENAL_FORMULARY: Dict[str, Dict[str, Any]] = {
    "vancomycin": {
        "display_name": "Vancomycin IV",
        "category": "Glycopeptide Antibiotic / Nephrotoxic Agent",
        "warning_crcl": 50.0,
        "contraindicated_crcl": 20.0,
        "standard_regimen": "15-20 mg/kg every 8-12 hours",
        "adjusted_regimen": "15-20 mg/kg every 24-48 hours with serum trough level monitoring",
        "clinical_rationale": "Accumulation in renal proximal tubules causes acute tubular necrosis when clearance drops below 50 mL/min."
    },
    "metformin": {
        "display_name": "Metformin Oral",
        "category": "Biguanide Antidiabetic",
        "warning_crcl": 45.0,
        "contraindicated_crcl": 30.0,
        "standard_regimen": "500-1000 mg twice daily",
        "adjusted_regimen": "Maximum 500 mg daily if CrCl 30-45; discontinue if CrCl < 30",
        "clinical_rationale": "Impaired renal elimination dramatically elevates risk of severe, life-threatening lactic acidosis."
    },
    "lisinopril": {
        "display_name": "Lisinopril Oral",
        "category": "ACE Inhibitor / Antihypertensive",
        "warning_crcl": 30.0,
        "contraindicated_crcl": 10.0,
        "standard_regimen": "10-20 mg once daily",
        "adjusted_regimen": "Reduce starting dose to 2.5-5 mg daily; monitor potassium and serum creatinine",
        "clinical_rationale": "Efferent arteriolar vasodilation reduces intraglomerular filtration pressure, risking acute decompensation."
    },
    "ciprofloxacin": {
        "display_name": "Ciprofloxacin IV/Oral",
        "category": "Fluoroquinolone Antibiotic",
        "warning_crcl": 50.0,
        "contraindicated_crcl": 30.0,
        "standard_regimen": "400 mg IV every 12 hours",
        "adjusted_regimen": "400 mg IV every 24 hours (50% reduction in total daily dose)",
        "clinical_rationale": "High renal excretion fraction; drug retention lowers seizure threshold and risks prolonged QT interval."
    }
}


def extract_clinical_entities(clinical_text: str) -> Dict[str, Any]:
    """
    NLP Entity Extractor:
    Parses unstructured clinical notes to extract:
    - Age (years)
    - Weight (kg)
    - Serum Creatinine (mg/dL)
    - Biological sex (Male/Female)
    - Target medication name
    """
    text_lower = clinical_text.lower()

    # Extract Age
    age_match = re.search(r'(\d{1,3})\s*(?:yo|year|yr|-year-old)', text_lower)
    age = int(age_match.group(1)) if age_match else None

    # Extract Weight (kg or lbs converted to kg)
    wt_match = re.search(r'(\d{2,3}(?:\.\d+)?)\s*(kg|kilos|lbs|pounds)', text_lower)
    weight_kg = None
    if wt_match:
        val, unit = float(wt_match.group(1)), wt_match.group(2)
        weight_kg = round(val * 0.453592, 1) if "lb" in unit else val

    # Extract Serum Creatinine (SCr)
    scr_match = re.search(r'(?:scr|creatinine|cr)\s*[:=]?\s*(\d(?:\.\d+)?)', text_lower)
    scr = float(scr_match.group(1)) if scr_match else None

    # Extract Sex / Gender
    is_female = False
    if re.search(r'\b(female|woman|lady|she|her)\b', text_lower):
        is_female = True

    # Identify medication mentioned in text
    detected_med = None
    for drug in RENAL_FORMULARY.keys():
        if drug in text_lower:
            detected_med = drug
            break

    return {
        "age": age,
        "weight_kg": weight_kg,
        "scr": scr,
        "is_female": is_female,
        "medication": detected_med
    }


def calculate_cockcroft_gault(age: int, weight_kg: float, scr: float, is_female: bool) -> float:
    """
    Computes estimated Creatinine Clearance (CrCl) using Cockcroft-Gault equation:
    CrCl = [((140 - Age) * Weight_kg) / (72 * SCr)] * (0.85 if female)
    """
    if scr <= 0 or age <= 0 or weight_kg <= 0:
        raise ValueError("Physiological metrics must be strictly positive.")
    
    crcl = ((140 - age) * weight_kg) / (72 * scr)
    if is_female:
        crcl *= 0.85
    return round(crcl, 1)


def evaluate_order(patient_id: str, clinical_text: str) -> Dict[str, Any]:
    """
    Full Decision Support Pipeline:
    1. Extracts patient variables from free text via NLP.
    2. Calculates CrCl.
    3. Evaluates nephrotoxic thresholds.
    4. Emits graded clinical recommendations with clinical provenance.
    """
    entities = extract_clinical_entities(clinical_text)

    # Validate essential entity completeness
    missing = [k for k in ["age", "weight_kg", "scr", "medication"] if entities[k] is None]
    if missing:
        return {
            "patient_id": patient_id,
            "status": "INSUFFICIENT_DATA",
            "missing_fields": missing,
            "alert_banner": "DATA INCOMPLETE: CANNOT COMPUTE RENAL DOSE",
            "action": f"Manual chart review required. Missing parameters: {', '.join(missing)}.",
            "requires_human_confirmation": True
        }

    crcl = calculate_cockcroft_gault(
        entities["age"], entities["weight_kg"], entities["scr"], entities["is_female"]
    )
    drug_info = RENAL_FORMULARY[entities["medication"]]

    # Graded Alert Triage Logic (Alert Fatigue Mitigation)
    if crcl < drug_info["contraindicated_crcl"]:
        severity = "LEVEL_1_CONTRAINDICATED"
        banner = "CRITICAL ALERT: SEVERE RENAL DYSFUNCTION - CONTRAINDICATED"
        action = f"DO NOT ADMINISTER standard dose. Prescribe non-renal alternative or hold. ({drug_info['adjusted_regimen']})"
        requires_override = True
    elif crcl < drug_info["warning_crcl"]:
        severity = "LEVEL_2_DOSE_ADJUSTMENT_REQUIRED"
        banner = "WARNING: RENAL IMPAIRMENT - ADJUST DOSE"
        action = f"Adjust ordered regimen to: {drug_info['adjusted_regimen']}."
        requires_override = True
    else:
        severity = "LEVEL_3_NORMAL_CLEARANCE"
        banner = "STANDARD CLEARANCE CONFIRMED"
        action = f"Normal clearance verified ({drug_info['standard_regimen']}). No interruptive alert needed."
        requires_override = False

    return {
        "patient_id": patient_id,
        "status": "EVALUATED",
        "extracted_data": {
            "age": entities["age"],
            "weight_kg": entities["weight_kg"],
            "serum_creatinine": entities["scr"],
            "biological_sex": "Female" if entities["is_female"] else "Male",
            "medication": drug_info["display_name"]
        },
        "crcl_calculated_ml_min": crcl,
        "alert_level": severity,
        "alert_banner": banner,
        "recommended_action": action,
        "clinical_rationale": drug_info["clinical_rationale"],
        "requires_human_confirmation": requires_override,
        "governance_mode": "Clinical Decision Support (Decision Support Dial: Recommends with Default)"
    }
