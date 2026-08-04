import pytest
from app.cgpa import calculate_cgpa

def test_cgpa_normal():
    courses = [
        {"credits": 4, "grade_point": 10},
        {"credits": 3, "grade_point": 8}
    ]
    # (4*10 + 3*8) / 7 = 64 / 7 = 9.14
    assert calculate_cgpa(courses) == 9.14

def test_cgpa_zero_credits():
    courses = [{"credits": 0, "grade_point": 10}]
    assert calculate_cgpa(courses) == 0.0

def test_cgpa_missing_grade():
    courses = [{"credits": 4, "grade_point": None}]
    # Should safely skip missing grades or return 0.0
    assert calculate_cgpa(courses) == 0.0