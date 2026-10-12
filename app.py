"""
Interactive Clinical Decision Support CLI
Module 03 Project: DoseGuard-Pro
"""

import json
from clinical_nlp_engine import evaluate_order, RENAL_FORMULARY

def run():
    print("=" * 80)
    print(" DoseGuard-Pro: Intelligent Renal Decision Support & Alert Fatigue Mitigator ")
    print(" ITAI 2372: Module 03 Applied AI System                                      ")
    print("=" * 80)

    print("\nSupported High-Risk Renally-Cleared Formulary:")
    for drug, data in RENAL_FORMULARY.items():
        print(f"  • {data['display_name']} (Cutoff: < {data['warning_crcl']} mL/min)")

    print("\nEnter a free-text physician order or clinical intake note below.")
    print("Example: '72yo male, 68 kg, cr 2.1. Start vancomycin 1000mg q12h for bacteremia.'\n")

    user_note = input("Clinical Note: ").strip()
    if not user_note:
        user_note = "72yo male, 68 kg, cr: 2.1. Start vancomycin 1000mg q12h."
        print(f"Using default test scenario note: \"{user_note}\"")

    patient_id = input("Patient ID [Default P-412]: ").strip() or "P-412"

    result = evaluate_order(patient_id=patient_id, clinical_text=user_note)

    print("\n" + "=" * 80)
    print(f" CLINICAL DECISION SUPPORT OUTPUT: {result['patient_id']} ")
    print("=" * 80)
    print(json.dumps(result, indent=2))
    print("=" * 80)

if __name__ == "__main__":
    run()
