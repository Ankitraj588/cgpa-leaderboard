def calculate_cgpa(courses):
    """Calculate CGPA from a list of course dictionaries."""
    total_weighted_points = 0.0
    total_credits = 0.0

    for course in courses or []:
        credits = course.get("credits", 0) or 0
        grade_point = course.get("grade_point")

        if not credits or grade_point is None:
            continue

        total_weighted_points += credits * grade_point
        total_credits += credits

    if total_credits == 0:
        return 0.0

    return round(total_weighted_points / total_credits, 2)
