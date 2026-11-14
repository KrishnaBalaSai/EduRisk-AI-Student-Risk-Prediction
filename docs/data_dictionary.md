# EduRisk AI — Data Dictionary

| Table | Column | Type | Nullable | Description | Allowed Values / Format |
|---|---|---|---|---|---|
| `students` | `id` | VARCHAR(32) | No | Unique deterministic Student ID | `STU-2026-000001` |
| `students` | `first_name` | VARCHAR(64) | No | Student legal given name | Free text |
| `students` | `last_name` | VARCHAR(64) | No | Student legal family name | Free text |
| `students` | `email` | VARCHAR(128) | No | Institutional email address | `name.id@edurisk.edu` |
| `students` | `cohort` | VARCHAR(32) | No | Cohort designation | `Cohort 2026-A`, `B`, `C` |
| `students` | `status` | VARCHAR(32) | No | Matriculation lifecycle state | `Active`, `Withdrawn`, `Graduated`, `Suspended` |
| `students` | `enrollment_date` | DATE | No | Date student initially enrolled | ISO YYYY-MM-DD |
| `students` | `withdrawal_date` | DATE | Yes | Date student withdrew | ISO YYYY-MM-DD or NULL |
| `courses` | `id` | VARCHAR(32) | No | Course catalog primary key | `CRS-000001` |
| `courses` | `code` | VARCHAR(32) | No | Course registry code | `CS101`, `MATH101`, etc. |
| `courses` | `title` | VARCHAR(128) | No | Course canonical title | Free text |
| `courses` | `department` | VARCHAR(64) | No | Academic department | `Computer Science`, `Data Science`, etc. |
| `courses` | `credits` | INT | No | Credit unit weight | 1 to 5 |
| `courses` | `semester` | VARCHAR(32) | No | Academic offering semester | `Fall 2026`, `Spring 2027` |
| `enrollments` | `id` | VARCHAR(64) | No | Composite enrollment identifier | `ENR-{student_id}-{course_id}` |
| `enrollments` | `status` | VARCHAR(32) | No | Course enrollment state | `Enrolled`, `Completed`, `Withdrawn`, `Dropped` |
| `attendance_events`| `id` | VARCHAR(96) | No | Attendance session record ID | `ATT-{enr_id}-{session_date}` |
| `attendance_events`| `status` | VARCHAR(32) | No | Student attendance status | `Present`, `Late`, `Absent_Approved`, `Absent_Unapproved` |
| `assessments` | `id` | VARCHAR(48) | No | Milestone assessment ID | `ASM-{course_id}-{seq}` |
| `assessments` | `assessment_type`| VARCHAR(32) | No | Assessment category | `Quiz`, `Assignment`, `Midterm`, `Final Exam`, `Project` |
| `assessments` | `weight` | FLOAT | No | Relative grade weight | 0.05 to 0.40 |
| `assessment_results`| `score` | FLOAT | Yes | Student numerical score (0-100) | 0.0 to 100.0 or NULL (missing) |
| `assessment_results`| `status` | VARCHAR(32) | No | Submission status | `Graded`, `Submitted`, `Late`, `Missing`, `Excused` |
| `lms_activities` | `activity_type`| VARCHAR(32) | No | Portal interaction type | `Login`, `Content_View`, `Assignment_Submit`, `Forum_Post`, `Quiz_Attempt` |
| `support_cases` | `status` | VARCHAR(32) | No | Triage lifecycle status | `Open`, `Assigned`, `In Progress`, `Resolved`, `Closed`, `Escalated` |
| `support_cases` | `priority` | VARCHAR(32) | No | Triage urgency tier | `Low`, `Medium`, `High`, `Critical` |
| `interventions` | `intervention_type`| VARCHAR(64) | No | Supported evidence-based protocol | 7 types (see schema) |
| `interventions` | `status` | VARCHAR(32) | No | Intervention execution state | `Scheduled`, `In Progress`, `Completed`, `Cancelled`, `No Show` |
| `outcomes` | `outcome_label` | VARCHAR(64) | No | Ground-truth derived outcome | `Improved academic performance`, `Continued academic risk`, `Successful recovery`, `Course withdrawal`, `Course completion` |
| `outcomes` | `is_recovery` | BOOLEAN | No | True if student achieved measurable recovery | `0` or `1` |

