import hmac

from flask import (
    Blueprint, render_template, redirect, request, flash,
    make_response, current_app,
)
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.utils import parse_reg, reg_from_login_id, college_email
from app.auth.jwt_utils import (
    create_access_token, create_refresh_token,
    create_reset_token, read_reset_token, password_fingerprint, TokenError,
)
from app.auth.middleware import set_auth_cookies, clear_auth_cookies
from app.mailer import send_email
from app.ratelimit import allow_all

auth_bp = Blueprint("auth", __name__)

GENERIC_RESET_MSG = "If that account exists, a reset link has been sent to your college email."


def _login_response(reg):
    resp = make_response(redirect("/cgpa"))
    set_auth_cookies(resp, create_access_token(reg), create_refresh_token(reg))
    return resp


def _client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    return forwarded.split(",")[0].strip() or request.remote_addr or "unknown"


@auth_bp.route("/")
def index():
    return render_template("index.html")


@auth_bp.route("/signup", methods=["POST"])
def signup():
    reg = reg_from_login_id(request.form.get("email"))
    name = request.form.get("name")
    password = request.form.get("password") or ""

    if not reg:
        flash("Use your college email, like 2023ugme104@nitjsr.ac.in")
        return redirect("/")

    if not name or not password:
        flash("All fields are required")
        return redirect("/")
    if len(password) < 8:
        flash("Password must be at least 8 characters")
        return redirect("/")

    if db.execute("SELECT 1 FROM users WHERE lower(reg) = ?", reg):
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
    reg = reg_from_login_id(request.form.get("email"))
    password = request.form.get("pswd") or ""

    user = db.execute("SELECT * FROM users WHERE lower(reg) = ?", reg) if reg else []

    if not user or not check_password_hash(user[0]["password"], password):
        flash("Incorrect email or password")
        return redirect("/")

    flash("Login successful")
    return _login_response(user[0]["reg"])


@auth_bp.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "GET":
        return render_template("forgot.html")

    reg = reg_from_login_id(request.form.get("email"))

    rules = [(f"ip:{_client_ip()}", 10)]      # 10 requests per hour per IP
    if reg:
        rules.append((f"reg:{reg}", 3))       # 3 emails per hour per account
    allowed = allow_all(rules)

    rows = []
    if allowed and reg:
        rows = db.execute("SELECT reg, password FROM users WHERE lower(reg) = ?", reg)

    if rows:
        to = college_email(rows[0]["reg"])
        if to:
            token = create_reset_token(rows[0]["reg"], rows[0]["password"])
            base = current_app.config["SITE_URL"] or request.host_url.rstrip("/")
            body = (
                "Hi,\n\n"
                "Use this link to reset your CGPA Leaderboard password. "
                "It is valid for 15 minutes and works once:\n\n"
                f"{base}/reset/{token}\n\n"
                "If you did not ask for this, you can ignore this email."
            )
            try:
                send_email(to, "Reset your CGPA Leaderboard password", body)
            except Exception:
                current_app.logger.exception("Reset email failed")

    # Same reply whether or not the account exists, or the caller was throttled
    flash(GENERIC_RESET_MSG)
    return redirect("/")


def _user_for_reset_token(token):
    try:
        reg, fp = read_reset_token(token)
    except TokenError:
        return None

    rows = db.execute("SELECT reg, password FROM users WHERE reg = ?", reg)
    if not rows:
        return None

    # The link dies as soon as the password changes
    if not hmac.compare_digest(password_fingerprint(rows[0]["password"]), fp or ""):
        return None
    return rows[0]


@auth_bp.route("/reset/<token>", methods=["GET", "POST"])
def reset_with_token(token):
    user = _user_for_reset_token(token)
    if not user:
        flash("This reset link is invalid or has expired. Please request a new one.")
        return redirect("/forgot")

    if request.method == "GET":
        return render_template("reset.html")

    password = request.form.get("password") or ""
    confirm = request.form.get("confirm") or ""

    if len(password) < 8:
        flash("Password must be at least 8 characters")
        return redirect(request.path)
    if password != confirm:
        flash("Passwords do not match")
        return redirect(request.path)

    db.execute(
        "UPDATE users SET password = ? WHERE reg = ?",
        generate_password_hash(password), user["reg"],
    )

    flash("Password updated. Please log in.")
    resp = make_response(redirect("/"))
    clear_auth_cookies(resp)
    return resp


@auth_bp.route("/logout")
def logout():
    resp = make_response(redirect("/"))
    clear_auth_cookies(resp)
    return resp