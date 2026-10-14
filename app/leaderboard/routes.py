from flask import Blueprint, render_template, request, g

from app.extensions import db
from app.auth.middleware import jwt_required

leaderboard_bp = Blueprint("leaderboard", __name__)


@leaderboard_bp.route("/leaderboard")
@jwt_required
def leaderboard():
    year = request.args.get("year")
    branch = request.args.get("branch")

    query = """
        SELECT users.name, users.reg, users.year, users.branch,
               MAX(results.cgpa) AS cgpa
        FROM users
        JOIN results ON users.reg = results.reg
    """
    conditions, params = [], []

    if year and year.strip():
        conditions.append("users.year = ?")
        params.append(year)
    if branch and branch.strip():
        conditions.append("users.branch = ?")
        params.append(branch)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += """
        GROUP BY users.reg, users.name, users.year, users.branch
        ORDER BY cgpa DESC
    """

    rows = db.execute(query, *params)

    rank, prev, current_rank, user_rank = 1, None, 1, None
    for row in rows:
        if prev is None or row["cgpa"] != prev:
            current_rank = rank
        row["rank"] = current_rank
        if row["reg"] == g.user:
            user_rank = current_rank
        prev = row["cgpa"]
        rank += 1

    user = db.execute(
        "SELECT name, branch, year FROM users WHERE reg = ?", g.user
    )[0]
    years = db.execute(
        "SELECT DISTINCT year FROM users WHERE year IS NOT NULL ORDER BY year ASC"
    )
    branches = db.execute(
        "SELECT DISTINCT branch FROM users WHERE branch IS NOT NULL ORDER BY branch ASC"
    )

    return render_template(
        "leaderboard.html",
        rows=rows, user=user, years=years, branches=branches,
        selected_year=year, selected_branch=branch, user_rank=user_rank,
    )