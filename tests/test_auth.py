import pytest
# Replace 'app.auth' and 'login_user' with your actual module and function names
from app.authh import login_user

@pytest.mark.parametrize("username, password, expected_status", [
    ("valid_user", "correct_pass", 200),
    ("valid_user", "wrong_pass", 401),
    ("", "correct_pass", 400),
    ("valid_user", "", 400),
    ("' OR '1'='1", "' OR '1'='1", 400),  # SQL injection test
])
def test_login_scenarios(username, password, expected_status):
    response = login_user(username, password)
    assert response["status"] == expected_status