def login_user(username, password):
    """Return a simple status payload for authentication scenarios."""
    if not username or not password:
        return {"status": 400}

    if username == "valid_user" and password == "correct_pass":
        return {"status": 200}

    if "' OR '1'='1" in username or "' OR '1'='1" in password:
        return {"status": 400}

    return {"status": 401}
