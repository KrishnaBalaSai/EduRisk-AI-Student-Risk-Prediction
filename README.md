# EduRisk AI — Explainable Student Risk Prediction & Intervention Management System

**YottaFlex Associate AI Forward Deployed Engineer Hackathon Submission**

[![Tests](https://img.shields.io/badge/pytest-19%20passed-brightgreen.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-3--Tier%20Strict-blue.svg)]()
[![Seed](https://img.shields.io/badge/Seed-20261022%20Reproducible-purple.svg)]()
[![Database](https://img.shields.io/badge/Database-MySQL%208%2B%20%7C%20SQLAlchemy-orange.svg)]()

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Core Features](#3-core-features)
4. [Three-Tier Architecture](#4-three-tier-architecture)
5. [Technology Stack](#5-technology-stack)
6. [Project Directory Structure](#6-project-directory-structure)
7. [Database Entities and Relationships](#7-database-entities-and-relationships)
8. [Risk Calculation Methodology](#8-risk-calculation-methodology)
9. [Synthetic Data Generation Methodology](#9-synthetic-data-generation-methodology)
10. [Negative Scenarios & Anomaly Injection](#10-negative-scenarios--anomaly-injection)
11. [Validation Methodology](#11-validation-methodology)
12. [Reproducibility Methodology](#12-reproducibility-methodology)
13. [Installation Instructions](#13-installation-instructions)
14. [MySQL Setup Instructions](#14-mysql-setup-instructions)
15. [Environment Configuration](#15-environment-configuration)
16. [Dataset Generation Commands](#16-dataset-generation-commands)
17. [Application Startup Command](#17-application-startup-command)
18. [Test Execution Command](#18-test-execution-command)
19. [UI Screenshots & Walkthrough](#19-ui-screenshots--walkthrough)
20. [Limitations & Future Roadmap](#20-limitations--future-roadmap)

---

## 1. Project Overview

**EduRisk AI** is an enterprise-grade, explainable student retention and risk prediction intelligence system. It combines multi-signal educational data mining (attendance, assessment trends, LMS digital engagement, and support case history) with strict temporal cutoffs to predict student academic risk without data leakage. The platform provides automated case triage and evidence-based intervention planning across seven institutional protocols.

---

## 2. Problem Statement

Higher education institutions often struggle with fragmented academic data, leading to late identification of at-risk students and arbitrary interventions. Traditional black-box models frequently suffer from:
1. **Temporal Data Leakage:** Training or inference models looking ahead into future grades or outcomes.
2. **Lack of Explainability:** Academic advisors unable to explain why a student is flagged.
3. **Data Quality Anomalies:** Inaccurate attendance denominators, withdrawn students remaining active, and premature interventions.

EduRisk AI addresses each challenge through a rigorous three-tier architecture, deterministic synthetic modeling, explainable rule scoring, and comprehensive domain validation.

---

## 3. Core Features

- **Executive KPI Dashboard:** Real-time metrics across 10 institutional indicators and 7 interactive Plotly charts.
- **Student 360° Management:** Comprehensive longitudinal profile linking enrollments, attendance, assessment results, LMS activity, and support tickets.
- **Explainable Multi-Factor Risk Engine:** Transparent scoring based on 35% attendance, 30% assessment, 20% LMS, and 15% support history.
- **Strict Temporal Safety:** Interactive observation window cutoff preventing future-data leakage.
- **Automated Support Triage:** High-risk automated case creation, duplicate prevention, and staff assignments.
- **Intervention Management:** 7 evidence-based intervention protocols with chronological trigger validation.
- **Automated Validation Suite:** Detects all 5 mandatory negative scenarios against labelled fixtures.
- **Deterministic Reproducibility:** Fixed seed (`20261022`) guaranteeing bit-for-bit identical datasets.
- **Role-Based Demo Navigation:** Seamless switching between Platform Admin, Academic Administrator, Instructor, Support Staff, and Learner.
- **Comprehensive Data Exports:** Multi-format downloads (CSV, JSON, SQL seed dump).

---

## 4. Three-Tier Architecture

EduRisk AI enforces strict separation between presentation, business logic, and persistence:

- **Tier 1 — Presentation Layer (Streamlit):**
  - Interactive multi-page dashboard, Plotly visualizations, role-based demo navigation.
  - *Rule:* Never executes raw SQL or accesses database tables directly. Communicates exclusively via Tier 2 services.
- **Tier 2 — Application / Business Logic Layer (Python):**
  - Application services (`StudentService`, `RiskService`, `InterventionService`, `SupportService`, `AnalyticsService`, `OutcomeService`).
  - Domain engines (`RiskEngine`, `InterventionEngine`, `OutcomeEngine`).
  - Validation suite (`IntegrityValidator`, `TemporalValidator`, `ReconciliationValidator`, `LifecycleValidator`, `DuplicateValidator`).
- **Tier 3 — Data Access & Database Layer (MySQL 8+ / SQLAlchemy):**
  - ORM entity models for all 10 domain entities.
  - Repository pattern abstracting all CRUD operations and queries.
  - Safe transaction management and connection pooling.

---

## 5. Technology Stack

- **Frontend / Visualization:** Streamlit 1.35+, Plotly 5.22+
- **Backend / Application:** Python 3.11+, Pandas 2.2+, NumPy 1.26+, Scikit-learn 1.4+, Faker 25+
- **Database & ORM:** MySQL 8+ via PyMySQL 1.1+, SQLAlchemy 2.0+ (with SQLite zero-dependency fallback)
- **Testing:** Pytest 8.0+
- **Configuration & Utilities:** python-dotenv, hashlib, json, logging

---

## 6. Project Directory Structure

```text
EduRisk-AI/
├── app.py                              # Main application entry point
├── requirements.txt                    # Project dependencies
├── README.md                           # Master documentation
├── .env.example                        # Environment variable template
├── .env                                # Local configuration
├── .gitignore                          # Git exclusion rules
│
├── presentation/                       # Tier 1: Presentation Layer
│   ├── auth.py                         # Demo role authentication
│   ├── dashboard.py                    # Dashboard adapter
│   ├── components/                     # Header, styling, sidebar
│   └── pages/                          # Multi-page application views
│       ├── 01_Executive_Dashboard.py
│       ├── 02_Student_Management.py
│       ├── 03_Risk_Analysis.py
│       ├── 04_Support_Cases.py
│       ├── 05_Interventions.py
│       ├── 06_Data_Generator.py
│       ├── 07_Data_Quality.py
│       └── 08_Reports.py
│
├── application/                        # Tier 2: Business Logic Layer
│   ├── services/                       # Application services
│   ├── engines/                        # Risk, Intervention, and Outcome engines
│   └── validators/                     # Integrity, temporal, and reconciliation validators
│
├── data/                               # Tier 3: Data Access Layer
│   ├── database.py                     # SQLAlchemy engine & session management
│   ├── models/                         # 10 Domain ORM models + fixtures
│   └── repositories/                   # Repository pattern implementations
│
├── generators/                         # Synthetic Data Generation Engine
│   ├── master_generator.py             # Master orchestrator
│   ├── enrollment_generator.py         # Students, courses, enrollments
│   ├── attendance_generator.py         # Weekly attendance events
│   ├── assessment_generator.py         # Assessments & graded results
│   ├── lms_generator.py                # Digital activity timestamps
│   ├── support_generator.py            # Support case records
│   ├── intervention_generator.py       # Interventions & scheduling
│   ├── outcome_generator.py            # Ground truth outcomes
│   ├── anomaly_generator.py            # Injected negative scenarios
│   └── generate_all.py                 # CLI generator runner
│
├── exports/                            # Multi-format artifact outputs
│   ├── csv/
│   ├── json/
│   └── sql/
│
├── docs/                               # Architectural and technical documentation
│   ├── architecture.md
│   ├── data_dictionary.md
│   ├── database_schema.md
│   ├── business_rules.md
│   ├── validation_report.md
│   ├── reproducibility_report.json
│   └── source_manifest.json
│
├── tests/                              # Pytest test suite (19 test cases)
│   ├── conftest.py
│   ├── test_generators.py
│   ├── test_database_integrity.py
│   ├── test_risk_engine.py
│   ├── test_temporal_leakage.py
│   ├── test_interventions.py
│   ├── test_edge_cases.py
│   └── test_reproducibility.py
│
└── scripts/                            # Operational CLI utilities
    ├── initialize_database.py          # Schema creation
    ├── generate_dataset.py             # Dataset generator (starter/full)
    ├── validate_dataset.py             # Validation suite runner
    └── verify_reproducibility.py       # Bit-for-bit verification
```

---

## 7. Database Entities and Relationships

EduRisk AI implements all 10 required domain entities with deterministic ID conventions:

1. **Student** (`STU-2026-000001`): Demographic and enrollment state.
2. **Course** (`CRS-000001`): Catalog metadata, department, semester.
3. **Enrollment** (`ENR-{student_id}-{course_id}`): Bridge table linking students to registered courses.
4. **AttendanceEvent** (`ATT-{enrollment_id}-{date}`): Weekly session logs (`Present`, `Late`, `Absent_Approved`, `Absent_Unapproved`).
5. **Assessment** (`ASM-{course_id}-{seq}`): Milestone definitions (`Quiz`, `Midterm`, `Assignment`, `Project`).
6. **AssessmentResult** (`ASR-{assessment_id}-{student_id}`): Graded scores with explicit NULL handling for missing data.
7. **LMSActivity** (`LMS-2026-000001`): Digital footprint logs (`Login`, `Content_View`, `Assignment_Submit`, `Forum_Post`, `Quiz_Attempt`).
8. **SupportCase** (`CAS-2026-000001`): Triage tickets (`Open`, `Assigned`, `In Progress`, `Resolved`, `Closed`, `Escalated`).
9. **Intervention** (`INT-2026-000001`): 7 targeted intervention types with chronological validation.
10. **Outcome** (`OUT-2026-000001`): Ground truth post-intervention outcomes (`Improved academic performance`, `Continued academic risk`, `Successful recovery`, `Course withdrawal`, `Course completion`).

---

## 8. Risk Calculation Methodology

### Formula
$$ \text{Risk Score} = (0.35 \times \text{Attendance}) + (0.30 \times \text{Assessment}) + (0.20 \times \text{LMS}) + (0.15 \times \text{Support}) $$

- **Attendance Factor (35%):** Uses eligible sessions excluding approved absences. Unapproved absences incur penalty.
- **Assessment Factor (30%):** Calculated using completed assessments only; missing data is represented as unknown, not zero.
- **LMS Engagement Factor (20%):** Evaluates activity count and 30-day velocity trend.
- **Support History Factor (15%):** Evaluates active cases and prior escalation history.
- **Categories:** Low (0–34), Medium (35–64), High (65–100).

---

## 9. Synthetic Data Generation Methodology

- **Fixed Seed:** `20261022`.
- **Profiles:**
  - `starter`: 100 students, 20 courses, 300 enrollments, 1 academic year.
  - `full`: 5,000 students, 200 courses, 20,000 enrollments, 1 academic year.
- **Archetypes:** Correlated behavioral personas (High Achiever, Steady Average, At-Risk, Chronic Struggling, Withdrawn) ensure realistic cross-domain distributions.

---

## 10. Negative Scenarios & Anomaly Injection

All 5 required negative scenarios are injected into isolated, labelled fixtures and detected:

1. **Future Data Leakage:** Prediction timestamp precedes observation window cutoff (`RSK-ANOMALY-0001`).
2. **Wrong Attendance Denominator:** Duplicate session date induces denominator distortion (`ATT-ANOMALY-...`).
3. **Withdrawn Student Remains Active:** Withdrawn student holds active course enrollment (`ENR-ANOMALY-...`).
4. **Intervention Precedes Trigger:** Intervention scheduled date is earlier than trigger date (`INT-ANOMALY-0001`).
5. **Missing Data as Failure:** Missing assessment submission score hardcoded as 0.0 (`ASR-ANOMALY-...`).

---

## 11. Validation Methodology

`ValidationSuite` coordinates:
- `IntegrityValidator`: Primary key uniqueness and foreign key integrity.
- `TemporalValidator`: Enforces temporal cutoff safety.
- `ReconciliationValidator`: Attendance denominators and risk formulas.
- `LifecycleValidator`: Student status transitions and chronological ordering.
- `DuplicateValidator`: Unique constraints.

---

## 12. Reproducibility Methodology

- Run `python -m scripts.verify_reproducibility`.
- Generates dataset twice with seed `20261022`, excludes volatile timestamps, canonicalizes JSON, and calculates SHA-256 digests.
- Verified 100% bit-for-bit identical across all 10 domain entities.

---

## 13. Installation Instructions

```bash
# 1. Clone or navigate to the project directory
cd EduRisk-AI

# 2. Install dependencies
pip install -r requirements.txt
```

---

## 14. MySQL Setup Instructions

1. Start MySQL 8+ server on `localhost:3306`.
2. Create the target database:
   ```sql
   CREATE DATABASE edurisk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Update `.env` with your MySQL user and password:
   ```ini
   DB_TYPE=mysql
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=edurisk_db
   ```
4. Initialize schema:
   ```bash
   python -m scripts.initialize_database
   ```

*Note:* If MySQL is not running locally, EduRisk AI defaults cleanly to SQLite (`edurisk.db`) with zero downtime.

---

## 15. Environment Configuration

Copy `.env.example` to `.env`:

```ini
DB_TYPE=sqlite
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=edurisk_db
DB_SQLITE_PATH=edurisk.db
RANDOM_SEED=20261022
ENV=development
APP_PORT=8501
```

---

## 16. Dataset Generation Commands

```bash
# Generate Starter Profile (100 students, 20 courses, 300 enrollments)
python -m scripts.generate_dataset --profile starter

# Generate Full Production Profile (5,000 students, 200 courses, 20,000 enrollments)
python -m scripts.generate_dataset --profile full
```

---

## 17. Application Startup Command

```bash
streamlit run app.py
```

---

## 18. Test Execution Command

```bash
pytest -v
```

All 19 test suites run and pass across generator counts, integrity, risk formulas, temporal leakage, interventions, and edge cases.

---

## 19. UI Screenshots & Walkthrough

The application features 8 professional SaaS views:
1. **Executive Dashboard:** Macro institutional KPIs, attendance trends, and course risk rankings.
2. **Student 360° Profile:** Comprehensive academic history and radar charts.
3. **Risk Analysis:** Dynamic observation cutoff sliders and natural language explanations.
4. **Support Cases:** Kanban and triage management.
5. **Interventions:** Scheduling, completion logging, and efficacy analysis.
6. **Data Generator:** Scale selector and live progress persistence.
7. **Data Quality & Anomalies:** Negative scenario detection audit and export downloads.
8. **Reports & Exports:** Direct CSV, JSON, and SQL seed downloads.

---

## 20. Limitations & Future Roadmap

- **External SIS Connectors:** Planned OAuth2/LTI 1.3 integrations for Canvas and Blackboard.
- **Deep Sequence Models:** Future integration of LSTM/Transformer sequence architectures for weekly engagement trajectories.
- **Automated Communication:** Automated SMS and email notification webhooks for scheduled intervention reminders.

