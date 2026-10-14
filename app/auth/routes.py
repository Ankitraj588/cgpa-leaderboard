from flask import Blueprint, render_template, redirect, request, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.utils import parse_reg
from app.auth.jwt_utils import create_access_token, create_refresh_token
from app.auth.middleware import set_auth_cookies, clear_auth_cookies

auth_bp = Blueprint("auth", __name__)


def _login_response(reg):
    resp = make_response(redirect("/cgpa"))
    set_auth_cookies(resp, create_access_token(reg), create_refresh_token(reg))
    return resp


@auth_bp.route("/")
def index():
    return render_template("index.html")


@auth_bp.route("/signup", methods=["POST"])
def signup():
    reg = request.form.get("reg")
    name = request.form.get("name")
    password = request.form.get("password")

    if not reg or not name or not password:
        flash("All fields are required")
        return redirect("/")

    if db.execute("SELECT 1 FROM users WHERE reg = ?", reg):
        flash("User already registered")
        return redirect("/")

    year, program, branch, roll = parse_reg(reg)

    db.execute(
        "INSERT INTO users (reg, name, password, year, program, branch, roll) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        reg, name, generate_password_hash(password), year, program, branch, roll,
    )
    return _login_response(reg)


@auth_bp.route("/login", methods=["POST"])
def login():
    reg = request.form.get("reg")
    password = request.form.get("pswd") or ""

    user = db.execute("SELECT * FROM users WHERE reg = ?", reg)

    if not user or not check_password_hash(user[0]["password"], password):
        flash("Incorrect registration number or password")
        return redirect("/")

    flash("Login successful")
    return _login_response(reg)


@auth_bp.route("/reset", methods=["GET", "POST"])
def reset():
    # Same behaviour as before on purpose. We'll harden this when you ask.
    if request.method == "GET":
        return render_template("reset.html")

    reg = request.form.get("reg")
    new_pass = request.form.get("password")

    if not db.execute("SELECT 1 FROM users WHERE reg = ?", reg):
        flash("Registration number not found")
        return redirect("/reset")

    db.execute(
        "UPDATE users SET password = ? WHERE reg = ?",
        generate_password_hash(new_pass), reg,
    )
    flash("Password reset successful. Please log in.")
    return redirect("/")


@auth_bp.route("/logout")
def logout():
    resp = make_response(redirect("/"))
    clear_auth_cookies(resp)
    return resp