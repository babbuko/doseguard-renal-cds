"""
Automated Clinical Test Battery
Validates accuracy of NLP parsing, Cockcroft-Gault calculation, and safety gates.
"""

from clinical_nlp_engine import evaluate_order, calculate_cockcroft_gault

def test_elderly_male_vancomycin_adjustment():
    note = "72yo male, 68 kg, admitted with fever. Serum cr 2.1. Prescribe vancomycin IV."
    res = evaluate_order("P-001", note)
    
    assert res["status"] == "EVALUATED"
    assert res["alert_level"] == "LEVEL_2_DOSE_ADJUSTMENT_REQUIRED"
    assert res["requires_human_confirmation"] is True
    assert 30.0 <= res["crcl_calculated_ml_min"] <= 31.5

def test_severe_renal_failure_metformin_contraindicated():
    note = "80-year-old female weighing 52 kg, baseline creatinine  2.8. Needs metformin."
    res = evaluate_order("P-002", note)
    
    assert res["status"] == "EVALUATED"
    assert res["alert_level"] == "LEVEL_1_CONTRAINDICATED"
    assert "DO NOT ADMINISTER" in res["recommended_action"]
    assert res["requires_human_confirmation"] is True

def test_normal_clearance_suppresses_interruptive_alert():
    note = "32yo male, weight 80 kg, cr 0.9. Started on ciprofloxacin for UTI."
    res = evaluate_order("P-003", note)
    
    assert res["status"] == "EVALUATED"
    assert res["alert_level"] == "LEVEL_3_NORMAL_CLEARANCE"
    assert res["requires_human_confirmation"] is False

def test_missing_data_triggers_safe_fallback():
    note = "45yo female, 60kg. Prescribe lisinopril 10mg."
    res = evaluate_order("P-004", note)
    
    assert res["status"] == "INSUFFICIENT_DATA"
    assert "scr" in res["missing_fields"]
    assert res["requires_human_confirmation"] is True

if __name__ == "__main__":
    test_elderly_male_vancomycin_adjustment()
    test_severe_renal_failure_metformin_contraindicated()
    test_normal_clearance_suppresses_interruptive_alert()
    test_missing_data_triggers_safe_fallback()
    print(" All clinical validation unit tests PASSED successfully!")
