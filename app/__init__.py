"""Flask application package."""

from flask import Flask
from config import Config
from app.auth.middleware import load_current_user, persist_refreshed_token

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static",
)

Config.validate()
app.config.from_object(Config)

app.before_request(load_current_user)
app.after_request(persist_refreshed_token)

from app.auth.routes import auth_bp
from app.cgpa.routes import cgpa_bp
from app.leaderboard.routes import leaderboard_bp

app.register_blueprint(auth_bp)
app.register_blueprint(cgpa_bp)
app.register_blueprint(leaderboard_bp)