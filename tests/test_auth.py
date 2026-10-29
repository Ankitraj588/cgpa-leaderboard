import pytest
from datetime import timedelta
from flask import g

from app.auth.jwt_utils import (
    create_access_token, create_refresh_token, create_reset_token,
    read_reset_token, decode_token, password_fingerprint, TokenError,
)
from app.auth.middleware import load_current_user


# ---------- token creation / verification ----------

def test_access_token_round_trip(app):
    with app.app_context():
        token = create_access_token("2023ugcs104")
        assert decode_token(token, "access") == "2023ugcs104"


def test_refresh_token_round_trip(app):
    with app.app_context():
        token = create_refresh_token("2023ugcs104")
        assert decode_token(token, "refresh") == "2023ugcs104"


def test_access_token_cannot_be_used_as_refresh(app):
    with app.app_context():
        with pytest.raises(TokenError):
            decode_token(create_access_token("x"), "refresh")


def test_refresh_token_cannot_be_used_as_access(app):
    with app.app_context():
        with pytest.raises(TokenError):
            decode_token(create_refresh_token("x"), "access")


def test_garbage_token_rejected(app):
    with app.app_context():
        with pytest.raises(TokenError):
            decode_token("not.a.real.token", "access")


def test_expired_token_rejected(app, monkeypatch):
    monkeypatch.setitem(app.config, "ACCESS_TOKEN_EXPIRES", timedelta(seconds=-1))
    with app.app_context():
        token = create_access_token("x")
        with pytest.raises(TokenError):
            decode_token(token, "access")


def test_reset_token_round_trip(app):
    password_hash = "stored-password-hash"
    with app.app_context():
        token = create_reset_token("2023ugcs104", password_hash)
        reg, fingerprint = read_reset_token(token)

    assert reg == "2023ugcs104"
    assert fingerprint == password_fingerprint(password_hash)


def test_reset_token_cannot_be_used_as_access_token(app):
    with app.app_context():
        token = create_reset_token("2023ugcs104", "stored-password-hash")
        with pytest.raises(TokenError):
            decode_token(token, "access")


def test_access_token_cannot_be_used_as_reset_token(app):
    with app.app_context():
        token = create_access_token("2023ugcs104")
        with pytest.raises(TokenError):
            read_reset_token(token)


def test_expired_reset_token_rejected(app, monkeypatch):
    monkeypatch.setitem(app.config, "RESET_TOKEN_EXPIRES", timedelta(seconds=-1))
    with app.app_context():
        token = create_reset_token("2023ugcs104", "stored-password-hash")
        with pytest.raises(TokenError):
            read_reset_token(token)


# ---------- middleware: who is this request? ----------

def test_valid_access_cookie_sets_user(app):
    with app.app_context():
        token = create_access_token("2023ugcs104")
    with app.test_request_context("/", headers={"Cookie": f"access_token={token}"}):
        load_current_user()
        assert g.user == "2023ugcs104"
        assert g._new_access_token is None


def test_expired_access_falls_back_to_refresh(app, monkeypatch):
    # Only a valid refresh cookie -> user stays logged in, new access token minted.
    with app.app_context():
        refresh = create_refresh_token("2023ugcs104")
    with app.test_request_context("/", headers={"Cookie": f"refresh_token={refresh}"}):
        load_current_user()
        assert g.user == "2023ugcs104"
        assert g._new_access_token is not None


def test_no_cookies_means_no_user(app):
    with app.test_request_context("/"):
        load_current_user()
        assert g.user is None


def test_access_token_in_refresh_cookie_is_rejected(app):
    with app.app_context():
        access = create_access_token("2023ugcs104")
    with app.test_request_context("/", headers={"Cookie": f"refresh_token={access}"}):
        load_current_user()
        assert g.user is None


# ---------- route protection ----------

@pytest.mark.parametrize("path", ["/cgpa", "/leaderboard"])
def test_protected_routes_redirect_when_logged_out(app, path):
    client = app.test_client()
    resp = client.get(path)
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/"