from functools import wraps
from flask import g, request, redirect, flash, current_app
from app.auth.jwt_utils import create_access_token, decode_token, TokenError
def _set_cookie(resp, name, value, delta):
    cfg = current_app.config
    resp.set_cookie(name, value, max_age=int(delta.total_seconds()), httponly=True,
                    secure=cfg["COOKIE_SECURE"], samesite=cfg["COOKIE_SAMESITE"], path="/")


def set_auth_cookies(resp, access, refresh=None):
    cfg = current_app.config
    _set_cookie(resp, cfg["ACCESS_COOKIE_NAME"], access, cfg["ACCESS_TOKEN_EXPIRES"])
    if refresh:
        _set_cookie(resp, cfg["REFRESH_COOKIE_NAME"], refresh, cfg["REFRESH_TOKEN_EXPIRES"])


def clear_auth_cookies(resp):
    cfg = current_app.config
    resp.delete_cookie(cfg["ACCESS_COOKIE_NAME"], path="/")
    resp.delete_cookie(cfg["REFRESH_COOKIE_NAME"], path="/")

def load_current_user():
    g.user = None
    g._new_access_token = None
    cfg = current_app.config
    access = request.cookies.get(cfg["ACCESS_COOKIE_NAME"])
    refresh = request.cookies.get(cfg["REFRESH_COOKIE_NAME"])

    if access:
        try:
            g.user = decode_token(access, "access")
            return
        except TokenError:
            pass  # expired or invalid, try the refresh token

    if refresh:
        try:
            g.user = decode_token(refresh, "refresh")
            g._new_access_token = create_access_token(g.user)
        except TokenError:
            g.user = None


def persist_refreshed_token(resp):
    if getattr(g, "_new_access_token", None):
        cfg = current_app.config
        _set_cookie(resp, cfg["ACCESS_COOKIE_NAME"], g._new_access_token,
                    cfg["ACCESS_TOKEN_EXPIRES"])
    return resp


def jwt_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not getattr(g, "user", None):
            flash("Please log in to continue")
            return redirect("/")
        return view(*args, **kwargs)
    return wrapped