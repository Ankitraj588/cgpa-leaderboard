import jwt
from datetime import datetime, timezone
from flask import current_app


class TokenError(Exception):
    pass


def _encode(sub, token_type, delta):
    cfg = current_app.config
    now = datetime.now(timezone.utc)
    payload = {"sub": sub, "type": token_type, "iat": now, "exp": now + delta}
    return jwt.encode(payload, cfg["JWT_SECRET_KEY"], algorithm=cfg["JWT_ALGORITHM"])


def create_access_token(reg):
    return _encode(reg, "access", current_app.config["ACCESS_TOKEN_EXPIRES"])


def create_refresh_token(reg):
    return _encode(reg, "refresh", current_app.config["REFRESH_TOKEN_EXPIRES"])


def decode_token(token, expected_type):
    cfg = current_app.config
    try:
        payload = jwt.decode(token, cfg["JWT_SECRET_KEY"], algorithms=[cfg["JWT_ALGORITHM"]])
    except jwt.ExpiredSignatureError:
        raise TokenError("expired")
    except jwt.InvalidTokenError:
        raise TokenError("invalid")
    if payload.get("type") != expected_type or not payload.get("sub"):
        raise TokenError("wrong type or missing subject")
    return payload["sub"]