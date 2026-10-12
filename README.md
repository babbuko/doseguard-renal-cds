# doseguard-renal-cds
Clinical decision support engine using NLP and Cockcroft-Gault clearance calculations to prevent renal drug overdoses and eliminate hospital alert fatigue.
# DoseGuard-Pro: Intelligent Renal Decision Support & Alert Fatigue Mitigator

**Course:** ITAI 2372 - Artificial Intelligence Applications  
**Module:** Module 03 — AI in Healthcare  
**Student:** Kamron Robinson  
**Submission Format:** GitHub Repository URL & Technical Documentation  

---

## 1. Problem Formulation & Clinical Context
Hospital electronic health record (EHR) systems routinely suffer from severe **alert fatigue** As documented in the Module 03 Riverside General case study:
* **The Clinical Baseline:** A legacy medication monitoring system fired **11,400 alerts in a single month**, but **96% were dismissed or bypassed by clinicians**
* **The Root Cause:** Most tools fire intrusive pop-ups for minor interactions, conditioning physicians and pharmacists to click past warnings without reading them
* **The Consequence:** When a truly lethal prescribing error occurs (e.g., ordering full-dose vancomycin or metformin for a patient with compromised glomerular filtration), it gets dismissed along with the background noise

**DoseGuard-Pro** addresses this breakdown by implementing a **Calibrated Decision Support Engine** It utilizes Natural Language Processing (NLP) to parse clinical order notes, calculates individual kidney clearance in real time, and selectively escalates warnings only when verified physiological thresholds are exceeded

---

## 2. Technical Architecture & Decision Flow
[ Unstructured Physician Order Note ]
│
▼
[ NLP Entity Extraction Layer ] ────► Extracts: Age, Weight, SCr, Sex, Drug
│
▼
[ Physiology Computation Engine ] ──► Calculates Cockcroft-Gault CrCl (mL/min)
│
▼
[ Graded Decision Triage Gate ]
├── CrCl >= Cutoff ──► Suppress Interruptive Alert (Normal Clearance Verified)
├── CrCl < Cutoff ───► Level 2 Alert: Recommend Specific Renal Dose Reduction
└── CrCl < Critical ─► Level 1 Alert: Hard Contraindication Flag & Alternative Drug
│
▼
[ Human Gate (Clinician Review) ] ──► requires_human_confirmation: true (Prescriber signs)
3. Governance, Ethics, & Regulatory Compliance

### A. The "Which Error Hurts More?" Evaluation (Module 03 Slide 4)
* **False Negative (Missed Overdose):** Catastrophic. Administering unadjusted nephrotoxic medication to a patient in renal failure causes permanent tubular damage, dialysis dependence, or fatal lactic acidosis.
* **False Positive (Over-alerting):** Produces alert fatigue, driving clinicians to bypass safety checks systematically.
* **Calibrated Solution:** The system eliminates interruptive warnings for patients with confirmed normal creatinine clearance, reserving alerts exclusively for patients with documented impairment.

### B. Autonomy Dial Placement (Module 03 Slide 10)
* **Dial Position:** **"Recommends with Default"**.
* **Implementation:** The system enforces `requires_human_confirmation: true` on all flags. It does **not** autonomously alter the pharmacy dispensing system or cancel orders; it presents an actionable recommendation that the prescriber or pharmacist must verify and sign.

### C. FDA & HIPAA Compliance (Module 03 Slide 12)
* **FDA SaMD Exemption:** Under Section 3060 of the 21st Century Cures Act, clinical decision support software is exempt from Class II medical device regulation **if** the clinician can independently review the basis of the recommendation. DoseGuard-Pro complies by explicitly printing the calculated CrCl value, formula variables, and pharmacokinetic rationale alongside every warning.
* **HIPAA Data Governance:** Runs on synthetic test records; production deployment requires encrypted transit inside the hospital boundary protected by a signed Business Associate Agreement (BAA).

---

