import time

from app.extensions import db


def allow_all(rules, window=3600):
    """rules: list of (bucket, limit). Returns True and records the attempt only if
    every bucket is under its limit within the window. Blocked attempts are not
    recorded, so an attacker can't extend someone's lockout by hammering the form."""
    now = int(time.time())
    since = now - window

    db.execute("DELETE FROM reset_requests WHERE ts < ?", now - 86400)

    for bucket, limit in rules:
        count = db.execute(
            "SELECT COUNT(*) AS n FROM reset_requests WHERE bucket = ? AND ts > ?",
            bucket, since,
        )[0]["n"]
        if count >= limit:
            return False

    for bucket, _ in rules:
        db.execute("INSERT INTO reset_requests (bucket, ts) VALUES (?, ?)", bucket, now)
    return True
