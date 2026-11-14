# EduRisk AI — System Architecture Specification

## 1. Architectural Overview

EduRisk AI strictly enforces a **Three-Tier Architecture**:

```mermaid
flowchart TD
    subgraph Tier1["Tier 1 — Presentation Layer (Streamlit)"]
        UI_Dash["Executive Dashboard"]
        UI_Student["Student 360 Management"]
        UI_Risk["Risk Analysis & Cutoff Engine"]
        UI_Support["Support Case Management"]
        UI_Int["Intervention Management"]
        UI_Gen["Synthetic Data Generator"]
        UI_Val["Data Quality & Anomalies"]
        UI_Rep["Reports & Exports"]
    end

    subgraph Tier2["Tier 2 — Application / Business Logic Layer"]
        subgraph Services["Application Services"]
            S_Student["StudentService"]
            S_Risk["RiskService"]
            S_Int["InterventionService"]
            S_Sup["SupportService"]
            S_Analytics["AnalyticsService"]
            S_Out["OutcomeService"]
            S_Exp["ExportService"]
        end
        subgraph Engines["Domain Engines"]
            E_Risk["RiskEngine (Explainable Multi-Factor)"]
            E_Int["InterventionEngine (Recommendation)"]
            E_Out["OutcomeEngine (Rule Evaluation)"]
        end
        subgraph Validators["Validation Suite"]
            V_Integ["IntegrityValidator"]
            V_Temp["TemporalValidator (Leakage Check)"]
            V_Recon["ReconciliationValidator"]
            V_Life["LifecycleValidator"]
            V_Dup["DuplicateValidator"]
        end
    end

    subgraph Tier3["Tier 3 — Data Access & Database Layer"]
        subgraph Repositories["Repository Pattern"]
            R_Student["StudentRepository"]
            R_Course["CourseRepository"]
            R_Enr["EnrollmentRepository"]
            R_Att["AttendanceRepository"]
            R_Asm["AssessmentRepository"]
            R_LMS["LMSRepository"]
            R_Sup["SupportRepository"]
            R_Int["InterventionRepository"]
            R_Out["OutcomeRepository"]
            R_Risk["RiskRepository"]
        end
        subgraph Storage["Storage Engine (SQLAlchemy ORM)"]
            DB_MySQL["MySQL 8+ (PyMySQL Driver)"]
            DB_SQLite["SQLite Fallback (Development)"]
        end
    end

    Tier1 --> Services
    Services --> Engines
    Services --> Validators
    Services --> Repositories
    Repositories --> Storage
```

## 2. Tier Isolation Rules

1. **Presentation Layer Isolation:**
   - Streamlit pages never execute raw SQL or query tables directly.
   - All interactions go through `application.services`.
   - Business calculations, risk scoring, and data reconciliations remain entirely in Tier 2.

2. **Application Layer Responsibilities:**
   - Orchestrates domain engines and repository queries.
   - Enforces temporal cutoffs on risk observation windows to eliminate future data leakage.
   - Manages support case triage queues and status transitions.
   - Executes validation rules against raw records and injected fixtures.

3. **Data Layer Responsibilities:**
   - Repository pattern abstracts all SQLAlchemy queries.
   - Explicit session management via scoped sessions and transaction context managers (`session_scope()`).
   - Foreign key cascading and indexed queries for sub-second retrieval.

