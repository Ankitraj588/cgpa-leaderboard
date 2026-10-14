from flask import Blueprint, render_template, request, flash, g

from app.extensions import db
from app.auth.middleware import jwt_required

cgpa_bp = Blueprint("cgpa", __name__)


@cgpa_bp.route("/cgpa", methods=["GET", "POST"])
@jwt_required
def cgpa():
    if request.method == "POST":
        semester = request.form.get("semester", "").strip().lower()
        sgpa = request.form.get("sgpa")
        cgpa_value = request.form.get("cgpa")

        existing = db.execute(
            "SELECT 1 FROM results WHERE reg = ? AND lower(trim(semester)) = ?",
            g.user, semester,
        )

        if existing:
            db.execute(
                "UPDATE results SET sgpa = ?, cgpa = ? "
                "WHERE reg = ? AND lower(trim(semester)) = ?",
                sgpa, cgpa_value, g.user, semester,
            )
            flash("Updated successfully")
        else:
            db.execute(
                "INSERT INTO results (reg, semester, sgpa, cgpa) VALUES (?, ?, ?, ?)",
                g.user, semester, sgpa, cgpa_value,
            )
            flash("Added successfully")

    data = db.execute(
        "SELECT semester, sgpa, cgpa FROM results WHERE reg = ? ORDER BY semester",
        g.user,
    )
    user = db.execute(
        "SELECT name, branch, year FROM users WHERE reg = ?", g.user
    )[0]

    return render_template("cgpa.html", data=data, user=user)