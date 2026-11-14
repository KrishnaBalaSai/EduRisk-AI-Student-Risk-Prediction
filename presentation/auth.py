"""
Lightweight Demo Role Authentication Module
Provides synthetic accounts for role-based navigation demonstrations.
"""

from typing import Dict, Any, List

DEMO_ACCOUNTS = {
    "admin": {
        "username": "admin",
        "role": "Platform Administrator",
        "name": "Sarah Connor",
        "email": "sarah.connor@edurisk.edu",
        "allowed_pages": [
            "Executive Dashboard",
            "Student Management",
            "Risk Analysis",
            "Support Cases",
            "Interventions",
            "Data Generator",
            "Data Quality & Anomalies",
            "Reports & Exports",
        ],
    },
    "dean": {
        "username": "dean",
        "role": "Academic Administrator",
        "name": "Dr. Robert Langdon",
        "email": "robert.langdon@edurisk.edu",
        "allowed_pages": [
            "Executive Dashboard",
            "Student Management",
            "Risk Analysis",
            "Support Cases",
            "Interventions",
            "Reports & Exports",
        ],
    },
    "instructor": {
        "username": "instructor",
        "role": "Instructor",
        "name": "Prof. Alan Turing",
        "email": "alan.turing@edurisk.edu",
        "allowed_pages": [
            "Executive Dashboard",
            "Student Management",
            "Risk Analysis",
            "Support Cases",
        ],
    },
    "support": {
        "username": "support",
        "role": "Support Staff",
        "name": "Marcus Holloway",
        "email": "marcus.holloway@edurisk.edu",
        "allowed_pages": [
            "Student Management",
            "Risk Analysis",
            "Support Cases",
            "Interventions",
        ],
    },
    "student": {
        "username": "student",
        "role": "Learner",
        "name": "Alex Mercer",
        "email": "alex.mercer@edurisk.edu",
        "student_id": "STU-2026-000001",
        "allowed_pages": [
            "Student Management",
            "Risk Analysis",
        ],
    },
}


def get_demo_account(role_key: str) -> Dict[str, Any]:
    return DEMO_ACCOUNTS.get(role_key, DEMO_ACCOUNTS["admin"])

