"""
Student, Course, and Enrollment Generators
Deterministic and realistic data generation with student archetypes.
"""

import random
from datetime import date, timedelta
from typing import List, Tuple, Dict, Any
from faker import Faker
from data.models.student import Student
from data.models.course import Course
from data.models.enrollment import Enrollment

DEPARTMENTS = [
    "Computer Science",
    "Data Science",
    "Information Technology",
    "Mathematics",
    "Electrical Engineering",
    "Business Analytics",
    "Software Engineering"
]

COURSE_TITLES = [
    ("CS101", "Introduction to Programming", "Computer Science", 4),
    ("CS102", "Data Structures & Algorithms", "Computer Science", 4),
    ("CS201", "Database Systems Design", "Computer Science", 3),
    ("CS202", "Computer Systems Architecture", "Computer Science", 3),
    ("DS201", "Statistical Learning & Inference", "Data Science", 4),
    ("DS202", "Data Wrangling & Pipeline Ops", "Data Science", 3),
    ("DS301", "Applied Machine Learning", "Data Science", 4),
    ("IT101", "Web Engineering Fundamentals", "Information Technology", 3),
    ("IT102", "Cloud Infrastructure & DevOps", "Information Technology", 3),
    ("IT201", "Cybersecurity & Access Control", "Information Technology", 3),
    ("MATH101", "Linear Algebra for Engineers", "Mathematics", 4),
    ("MATH102", "Calculus & Optimization", "Mathematics", 4),
    ("MATH201", "Probability & Stochastic Models", "Mathematics", 3),
    ("EE101", "Circuit Analysis & Logic", "Electrical Engineering", 3),
    ("EE102", "Embedded Systems & IoT", "Electrical Engineering", 4),
    ("BA101", "Business Analytics Foundations", "Business Analytics", 3),
    ("BA201", "Predictive Business Modeling", "Business Analytics", 3),
    ("BA301", "Executive Decision Analysis", "Business Analytics", 3),
    ("SE201", "Software Architecture Principles", "Software Engineering", 4),
    ("SE301", "Full-Stack System Engineering", "Software Engineering", 4),
]


def generate_students(count: int, seed: int = 20261022) -> Tuple[List[Student], Dict[str, str]]:
    """
    Generate deterministic student records and return archetype mapping.
    Archetypes:
    - High_Achiever (25%)
    - Steady_Average (40%)
    - At_Risk (20%)
    - Chronic_Struggling (10%)
    - Withdrawn (5%)
    """
    fake = Faker()
    Faker.seed(seed)
    rng = random.Random(seed)

    archetype_choices = ["High_Achiever", "Steady_Average", "At_Risk", "Chronic_Struggling", "Withdrawn"]
    archetype_weights = [0.25, 0.40, 0.20, 0.10, 0.05]

    students: List[Student] = []
    archetypes: Dict[str, str] = {}

    cohorts = ["Cohort 2026-A", "Cohort 2026-B", "Cohort 2026-C"]

    for i in range(1, count + 1):
        student_id = f"STU-2026-{i:06d}"
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}{i}@edurisk.edu"
        cohort = rng.choice(cohorts)

        arch = rng.choices(archetype_choices, weights=archetype_weights)[0]
        archetypes[student_id] = arch

        enroll_date = date(2026, 8, 25) + timedelta(days=rng.randint(0, 5))
        
        if arch == "Withdrawn":
            status = "Withdrawn"
            withdrawal_date = date(2026, 11, 15) + timedelta(days=rng.randint(0, 30))
        else:
            status = "Active"
            withdrawal_date = None

        student = Student(
            id=student_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            cohort=cohort,
            status=status,
            enrollment_date=enroll_date,
            withdrawal_date=withdrawal_date,
        )
        students.append(student)

    return students, archetypes


def generate_courses(count: int, seed: int = 20261022) -> List[Course]:
    """
    Generate deterministic course records across Fall 2026 and Spring 2026.
    """
    fake = Faker()
    Faker.seed(seed)
    rng = random.Random(seed)

    courses: List[Course] = []
    base_count = len(COURSE_TITLES)

    for i in range(1, count + 1):
        course_id = f"CRS-{i:06d}"
        template_idx = (i - 1) % base_count
        code_prefix, title_base, dept, credits_val = COURSE_TITLES[template_idx]
        
        semester = "Fall 2026" if (i % 2 != 0) else "Spring 2026"
        suffix = f"-{(i - 1) // base_count + 1}" if i > base_count else ""
        code = f"{code_prefix}{suffix}"
        title = f"{title_base}{f' Section {suffix}' if suffix else ''}"
        instructor = f"Prof. {fake.first_name()} {fake.last_name()}"

        course = Course(
            id=course_id,
            code=code,
            title=title,
            department=dept,
            credits=credits_val,
            instructor_name=instructor,
            semester=semester,
        )
        courses.append(course)

    return courses


def generate_enrollments(
    students: List[Student],
    courses: List[Course],
    target_count: int,
    archetypes: Dict[str, str],
    seed: int = 20261022
) -> List[Enrollment]:
    """
    Generate deterministic enrollments ensuring each student is enrolled in courses.
    """
    rng = random.Random(seed)
    enrollments: List[Enrollment] = []
    existing_pairs = set()

    fall_courses = [c for c in courses if c.semester == "Fall 2026"]
    spring_courses = [c for c in courses if c.semester == "Spring 2026"]
    if not fall_courses:
        fall_courses = courses
    if not spring_courses:
        spring_courses = courses

    # Initial pass: guarantee enrollments for every student
    avg_per_student = max(1, target_count // len(students))
    
    for s in students:
        arch = archetypes.get(s.id, "Steady_Average")
        # Withdrawn students might only take 1 or 2 courses
        n_courses = max(1, avg_per_student - (1 if arch == "Withdrawn" else 0))
        
        # Pick from fall and spring
        sampled_fall = rng.sample(fall_courses, min(len(fall_courses), max(1, n_courses // 2 + 1)))
        sampled_spring = rng.sample(spring_courses, min(len(spring_courses), max(1, n_courses - len(sampled_fall))))
        candidate_courses = sampled_fall + sampled_spring

        for c in candidate_courses[:n_courses]:
            pair = (s.id, c.id)
            if pair not in existing_pairs:
                existing_pairs.add(pair)
                enr_id = f"ENR-{s.id}-{c.id}"
                enr_status = "Withdrawn" if (s.status == "Withdrawn" and c.semester == "Spring 2026") else "Enrolled"
                
                enr = Enrollment(
                    id=enr_id,
                    student_id=s.id,
                    course_id=c.id,
                    status=enr_status,
                    enrollment_date=s.enrollment_date,
                    completion_date=None,
                    final_grade=None
                )
                enrollments.append(enr)

    # If target_count > len(enrollments), fill remainder deterministically
    student_cycle = 0
    while len(enrollments) < target_count and len(existing_pairs) < (len(students) * len(courses)):
        s = students[student_cycle % len(students)]
        student_cycle += 1
        c = rng.choice(courses)
        pair = (s.id, c.id)
        if pair not in existing_pairs:
            existing_pairs.add(pair)
            enr_id = f"ENR-{s.id}-{c.id}"
            enr_status = "Withdrawn" if s.status == "Withdrawn" else "Enrolled"
            enr = Enrollment(
                id=enr_id,
                student_id=s.id,
                course_id=c.id,
                status=enr_status,
                enrollment_date=s.enrollment_date,
                completion_date=None,
                final_grade=None
            )
            enrollments.append(enr)

    return enrollments

