# EduRisk AI — Validation & Anomaly Detection Summary

## 1. Validation Architecture

The automated validation suite executes 5 specialized domain validators:
1. `IntegrityValidator`: Primary key uniqueness, foreign key consistency, and enum domain constraints.
2. `TemporalValidator`: Observation window cutoff enforcement and future-data leakage detection.
3. `ReconciliationValidator`: Arithmetic reconciliation of attendance percentages, missing data representations, and risk formula calculations.
4. `LifecycleValidator`: Student status transitions, withdrawn enrollments, and intervention chronological constraints.
5. `DuplicateValidator`: Duplicate email addresses, duplicate enrollment pairs, and duplicate submissions.

---

## 2. Mandatory 5 Negative Scenarios Verification

All 5 required negative scenarios are deliberately injected into labelled fixtures and detected:

| Fixture ID | Injected Anomaly | Target Record | Detecting Validator | Verification Status |
|---|---|---|---|---|
| `ANM-000001` | `future_data_leakage` | `RSK-ANOMALY-0001` | `TemporalValidator` | ✅ DETECTED 100% |
| `ANM-000002` | `wrong_attendance_denominator` | `ATT-ENR-...-BAD-DENOM`| `ReconciliationValidator`| ✅ DETECTED 100% |
| `ANM-000003` | `withdrawn_student_active` | `ENR-ANOMALY-...` | `LifecycleValidator` | ✅ DETECTED 100% |
| `ANM-000004` | `intervention_precedes_trigger` | `INT-ANOMALY-0001` | `LifecycleValidator` | ✅ DETECTED 100% |
| `ANM-000005` | `missing_data_as_failure` | `ASR-ANOMALY-...` | `ReconciliationValidator`| ✅ DETECTED 100% |

---

## 3. Ground Truth Separation Guarantee

- Anomaly labels and ground truth files (`ground_truth_anomalies.json`, `ground_truth_anomalies.csv`) are generated into an isolated fixtures table.
- They are **strictly prohibited** from model training or feature generation pipelines, preventing data leakage during inference or evaluation.

