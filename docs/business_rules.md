# EduRisk AI — Business Rules Specification

## 1. Risk Calculation Methodology

### 1.1 Formula & Factor Weights
$$ \text{Risk Score} = (0.35 \times \text{Attendance Risk}) + (0.30 \times \text{Assessment Risk}) + (0.20 \times \text{LMS Risk}) + (0.15 \times \text{Support Risk}) $$

- All individual factor scores are normalized to the interval $[0, 100]$.
- The composite Risk Score is bounded in $[0, 100]$.

### 1.2 Categorization Thresholds
- **0.0 – 34.0:** Low Risk (Satisfactory standing; proactive monitoring).
- **35.0 – 64.0:** Medium Risk (Early warning queue; advisor review).
- **65.0 – 100.0:** High Risk (Critical priority; automated triage and mandatory intervention recommendation).

### 1.3 Factor Derivation Logic
1. **Attendance Risk (35%):**
   - Calculated strictly over **eligible sessions**: $\text{Eligible Sessions} = \text{Total Sessions} - \text{Approved Absences}$.
   - Attendance rate $R = \frac{\text{Present} + (0.75 \times \text{Late})}{\text{Eligible Sessions}} \times 100$.
   - Unapproved absences incur an escalating penalty of $+3.0$ points each (up to $+20.0$).
2. **Assessment Risk (30%):**
   - Computed exclusively using **completed assessments**: $\text{Avg Grade} = \frac{\sum \text{Scores}}{\text{Completed Count}}$.
   - Missing assessments are explicitly represented as unknown ($score = \text{NULL}$), never silently substituted with $0.0$.
   - A missing submission adds a separate accountability penalty ($+8.0$ points per missing milestone).
3. **LMS Engagement Risk (20%):**
   - Evaluates digital footprint volume in the prior 30-day window relative to the baseline 30-60 day window.
   - Significant drop ($< -25\%$ trend) adds an urgency penalty.
4. **Support History Risk (15%):**
   - Evaluates active support tickets and historical escalations strictly preceding the observation timestamp.
   - Active Critical/Escalated case triggers $90.0$ support risk.

---

## 2. Temporal Data Leakage Prevention Rules

1. Every risk calculation accepts an explicit `observation_window_end` cutoff date.
2. The engine filters:
   - `attendance_events.session_date <= observation_window_end`
   - `assessments.due_date <= observation_window_end`
   - `lms_activities.timestamp <= cutoff_datetime`
   - `support_cases.opened_at <= cutoff_datetime`
3. Assessment results for future tests or final outcomes are completely omitted from risk calculation.

---

## 3. Intervention Lifecycle Rules

1. **Trigger Precedence:**
   - $\text{trigger\_timestamp} \le \text{scheduled\_date}$. An intervention cannot be scheduled prior to its initiating event.
2. **Completion Rule:**
   - $\text{completion\_date} \ge \text{scheduled\_date}$.
3. **No Duplicate Cases:**
   - A student with an open or in-progress case will have subsequent automated triggers appended to the existing ticket rather than creating duplicate open tickets.

---

## 4. Ground-Truth Outcome Derivation Rules

1. **Withdrawn:** If student status is `Withdrawn`, outcome label is derived as `Course withdrawal`.
2. **High Achiever:** If student maintained high performance, outcome label is `Course completion`.
3. **Successful Recovery:** If an at-risk student engaged in completed interventions and achieved $\ge 10\%$ GPA improvement, outcome is `Successful recovery` ($is\_recovery = \text{True}$).
4. **Continued Risk:** If an at-risk student failed to engage or grades continued declining, outcome is `Continued academic risk`.

