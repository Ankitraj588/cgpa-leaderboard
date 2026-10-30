import re
import pytest
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
import app.auth.routes as auth_routes

REG = "2023ugme104"
EMAIL = f"{REG}@nitjsr.ac.in"


@pytest.fixture()
def user(app):
    db.execute("CREATE TABLE IF NOT EXISTS reset_requests (bucket TEXT NOT NULL, ts BIGINT NOT NULL)")
    db.execute("DELETE FROM reset_requests")
    db.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, reg TEXT UNIQUE, "
        "name TEXT, password TEXT, year TEXT, program TEXT, branch TEXT, roll TEXT)"
    )
    db.execute("DELETE FROM users")
    db.execute(
        "INSERT INTO users (reg, name, password) VALUES (?, ?, ?)",
        REG, "Test", generate_password_hash("oldpassword1"),
    )
    yield REG
    db.execute("DELETE FROM users")


@pytest.fixture()
def outbox(monkeypatch):
    sent = []
    monkeypatch.setattr(auth_routes, "send_email", lambda to, subject, body: sent.append((to, body)))
    return sent


def _token(body):
    return re.search(r"/reset/(\S+)", body).group(1)


def test_forgot_emails_the_college_address(app, user, outbox):
    resp = app.test_client().post("/forgot", data={"email": EMAIL})
    assert resp.status_code == 302
    assert len(outbox) == 1
    assert outbox[0][0] == EMAIL


def test_unknown_user_gets_same_reply_and_no_email(app, user, outbox):
    client = app.test_client()
    known = client.post("/forgot", data={"email": EMAIL})
    unknown = client.post("/forgot", data={"email": "2020ugcs999@nitjsr.ac.in"})
    assert (known.status_code, known.headers["Location"]) == (unknown.status_code, unknown.headers["Location"])
    assert len(outbox) == 1


def test_reset_changes_password_and_link_works_once(app, user, outbox):
    client = app.test_client()
    client.post("/forgot", data={"email": EMAIL})
    token = _token(outbox[0][1])

    assert client.get(f"/reset/{token}").status_code == 200

    resp = client.post(f"/reset/{token}", data={"password": "newpassword1", "confirm": "newpassword1"})
    assert resp.status_code == 302

    stored = db.execute("SELECT password FROM users WHERE reg = ?", REG)[0]["password"]
    assert check_password_hash(stored, "newpassword1")

    again = client.get(f"/reset/{token}")
    assert again.status_code == 302
    assert again.headers["Location"] == "/forgot"


def test_tampered_token_rejected(app, user):
    resp = app.test_client().get("/reset/not.a.real.token")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/forgot"


def test_forgot_is_rate_limited_per_account(app, user, outbox):
    client = app.test_client()
    responses = [client.post("/forgot", data={"email": EMAIL}) for _ in range(5)]

    assert len(outbox) == 3
    replies = {(r.status_code, r.headers["Location"]) for r in responses}
    assert len(replies) == 1