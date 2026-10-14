def filter_leaderboard(students, branch=None, year=None):
    """Filter and sort leaderboard rows by branch and year."""
    filtered = []

    for student in students or []:
        if branch and str(branch).strip() and str(student.get("branch", "")).upper() != str(branch).upper():
            continue

        if year is not None and year != "" and student.get("year") != year:
            continue

        filtered.append(student)

    filtered.sort(key=lambda item: (-item.get("cgpa", 0), str(item.get("name", ""))))
    return filtered