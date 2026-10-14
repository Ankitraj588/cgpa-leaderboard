"""Flask application package."""

from flask import Flask, render_template, redirect, request, flash, g, make_response
from config import Config
# from cs50 import SQL
from app.extensions import db
from app.utils import parse_reg
from werkzeug.security import generate_password_hash, check_password_hash
from app.auth.jwt_utils import create_access_token, create_refresh_token
from app.auth.middleware import (
    set_auth_cookies, clear_auth_cookies,
    load_current_user, persist_refreshed_token, jwt_required,
)

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)


Config.validate()
app.config.from_object(Config)

app.before_request(load_current_user)
app.after_request(persist_refreshed_token)

# app.config["SECRET_KEY"] = os.environ.get(
#     "SECRET_KEY",
#     "dev-secret-key"
# )

# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"

# Session(app)

# db = SQL("sqlite:///cgpa.db")

# def parse_reg(reg):
#     reg = reg.lower().strip()

#     year = reg[:4]                  # 2023
#     program = reg[4:6]              # ug
#     branch = reg[6:8]               # me
#     roll = reg[8:]

#     program_full = {
#         "ug": "Undergraduate",
#         "pg": "Postgraduate"
#     }.get(program, "Unknown")

#     branch_full = {
#         "cs": "Computer Science",
#         "it": "Information Technology",
#         "me": "Mechanical",
#         "ce": "Civil",
#         "ec": "Electronics",
#         "ee": "Electrical"
#     }.get(branch, "Unknown")

#     return year, program_full, branch_full, roll


# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["POST"])
def signup():
    reg = request.form.get("reg")
    name = request.form.get("name")
    password = request.form.get("password")

    if not reg or not name or not password:
        flash("All fields are required")
        return redirect("/")

    user = db.execute("SELECT * FROM users WHERE reg = ?", reg)
    if user:
        flash("User already registered")
        return redirect("/")

    year, program, branch, roll = parse_reg(reg)
    hash_pass = generate_password_hash(password)

    db.execute(
        "INSERT INTO users (reg, name, password, year, program, branch, roll) VALUES (?, ?, ?, ?, ?, ?, ?)",
        reg, name, hash_pass, year, program, branch, roll
    )

    resp = make_response(redirect("/cgpa"))
    set_auth_cookies(resp, create_access_token(reg), create_refresh_token(reg))
    return resp


# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    reg = request.form.get("reg")
    password = request.form.get("pswd")

    user = db.execute("SELECT * FROM users WHERE reg = ?", reg)

    if not user:
        flash("User not found ❌")
        return redirect("/")

    if not check_password_hash(user[0]["password"], password):
        flash("Incorrect Password ❌ | Reset BRO")
        return redirect("/")

    flash("Login Successful 🎯")
    resp = make_response(redirect("/cgpa"))
    set_auth_cookies(resp, create_access_token(reg), create_refresh_token(reg))
    return resp


# ---------------- RESET PASSWORD ----------------
@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "GET":
        return render_template("reset.html")

    reg = request.form.get("reg")
    new_pass = request.form.get("password")

    user = db.execute("SELECT * FROM users WHERE reg = ?", reg)

    if not user:
        flash("Registration Number not found ❌")
        return redirect("/reset")

    db.execute(
        "UPDATE users SET password = ? WHERE reg = ?",
        generate_password_hash(new_pass),
        reg
    )

    flash("Password Reset Successful ✅ Please Login")
    return redirect("/")


# ---------------- CGPA PAGE ----------------
@app.route("/cgpa", methods=["GET", "POST"])
@jwt_required
def cgpa():
    # - if "user" not in session:
    # -     return redirect("/")

    if request.method == "POST":
        semester = request.form.get("semester").strip().lower()
        sgpa = request.form.get("sgpa")
        cgpa_value = request.form.get("cgpa")

        existing = db.execute(
            "SELECT * FROM results WHERE reg = ? AND lower(trim(semester)) = ?",
            g.user, semester
        )

        if existing:
            db.execute(
                "UPDATE results SET sgpa = ?, cgpa = ? WHERE reg = ? AND lower(trim(semester)) = ?",
                sgpa, cgpa_value, g.user, semester
            )
            flash("Updated Successfully 👍")
        else:
            db.execute(
                "INSERT INTO results (reg, semester, sgpa, cgpa) VALUES (?, ?, ?, ?)",
                g.user, semester, sgpa, cgpa_value
            )
            flash("Added Successfully 🎯")

    data = db.execute(
        "SELECT semester, sgpa, cgpa FROM results WHERE reg = ? ORDER BY semester",
        g.user
    )

    user = db.execute(
        "SELECT name, branch, year FROM users WHERE reg = ?",
        g.user
    )[0]

    return render_template("cgpa.html", data=data, user=user)


# leaderboard
@app.route("/leaderboard")
@jwt_required
def leaderboard():
    # - if "user" not in session:
    # -     return redirect("/")

    year = request.args.get("year")
    branch = request.args.get("branch")

    query = """
        SELECT users.name, users.reg, users.year, users.branch,
               MAX(results.cgpa) AS cgpa
        FROM users
        JOIN results ON users.reg = results.reg
    """

    conditions = []
    params = []

    if year and year.strip() != "":
        conditions.append("users.year = ?")
        params.append(year)

    if branch and branch.strip() != "":
        conditions.append("users.branch = ?")
        params.append(branch)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY users.reg ORDER BY cgpa DESC"

    rows = db.execute(query, *params)

    rank = 1
    prev = None
    user_rank = None

    for row in rows:
        if prev is None or row["cgpa"] != prev:
            current_rank = rank
        row["rank"] = current_rank

        if row["reg"] == g.user:
            user_rank = current_rank

        prev = row["cgpa"]
        rank += 1

    user = db.execute(
        "SELECT name, branch, year FROM users WHERE reg = ?",
        g.user
    )[0]

    years = db.execute("SELECT DISTINCT year FROM users WHERE year IS NOT NULL ORDER BY year ASC")
    branches = db.execute("SELECT DISTINCT branch FROM users WHERE branch IS NOT NULL ORDER BY branch ASC")

    return render_template(
        "leaderboard.html",
        rows=rows,
        user=user,
        years=years,
        branches=branches,
        selected_year=year,
        selected_branch=branch,
        user_rank=user_rank
    )


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
# -    session.clear()
# -    return redirect("/")
    resp = make_response(redirect("/"))
    clear_auth_cookies(resp)
    return resp