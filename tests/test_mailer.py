from app import mailer


class RecordingSMTP:
    def __init__(self, events):
        self.events = events

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def starttls(self):
        self.events.append("starttls")

    def login(self, username, password):
        self.events.append(("login", username, password))

    def send_message(self, message):
        self.events.append(("send", message["To"], message["Subject"]))


def test_send_email_uses_ssl_on_port_465(app, monkeypatch):
    events = []

    def smtp_ssl(server, port, timeout):
        events.append(("ssl", server, port, timeout))
        return RecordingSMTP(events)

    monkeypatch.setitem(app.config, "MAIL_PORT", 465)
    monkeypatch.setitem(app.config, "MAIL_USERNAME", "mailer@example.com")
    monkeypatch.setitem(app.config, "MAIL_PASSWORD", "test-password")
    monkeypatch.setattr(mailer.smtplib, "SMTP_SSL", smtp_ssl)

    with app.app_context():
        mailer.send_email("student@nitjsr.ac.in", "Test", "Hello")

    assert events == [
        ("ssl", app.config["MAIL_SERVER"], 465, 15),
        ("login", "mailer@example.com", "test-password"),
        ("send", "student@nitjsr.ac.in", "Test"),
    ]


def test_send_email_uses_starttls_on_other_ports(app, monkeypatch):
    events = []

    def smtp(server, port, timeout):
        events.append(("smtp", server, port, timeout))
        return RecordingSMTP(events)

    monkeypatch.setitem(app.config, "MAIL_PORT", 587)
    monkeypatch.setitem(app.config, "MAIL_USERNAME", "mailer@example.com")
    monkeypatch.setitem(app.config, "MAIL_PASSWORD", "test-password")
    monkeypatch.setattr(mailer.smtplib, "SMTP", smtp)

    with app.app_context():
        mailer.send_email("student@nitjsr.ac.in", "Test", "Hello")

    assert events == [
        ("smtp", app.config["MAIL_SERVER"], 587, 15),
        "starttls",
        ("login", "mailer@example.com", "test-password"),
        ("send", "student@nitjsr.ac.in", "Test"),
    ]