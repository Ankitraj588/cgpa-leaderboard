import os
import tempfile

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()

# Forced on purpose: tests must never touch a real database
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key"
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"

import pytest
from app import app as flask_app


@pytest.fixture()
def app():
    flask_app.config.update(TESTING=True)
    return flask_app