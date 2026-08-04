import pytest
from app.leaderboard import filter_leaderboard

@pytest.fixture
def mock_students():
    return [
        {"name": "Alice", "cgpa": 9.5, "branch": "ME", "year": 2026},
        {"name": "Bob", "cgpa": 9.5, "branch": "CSE", "year": 2026},
        {"name": "Charlie", "cgpa": 8.8, "branch": "ME", "year": 2025},
    ]

def test_leaderboard_tied_scores(mock_students):
    result = filter_leaderboard(mock_students)
    # Ensure ties keep a secondary sort order (e.g., alphabetically by name)
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "Bob"

def test_leaderboard_empty_filters(mock_students):
    result = filter_leaderboard(mock_students, branch="", year=None)
    assert len(result) == 3

def test_leaderboard_no_matching_students(mock_students):
    result = filter_leaderboard(mock_students, branch="ECE", year=2024)
    assert result == []