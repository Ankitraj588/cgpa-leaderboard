from app.utils import college_email, reg_from_login_id


def test_college_email_formats_valid_registration():
    assert college_email(" 2023ugme104 ") == "2023ugme104@nitjsr.ac.in"


def test_college_email_rejects_invalid_registration():
    assert college_email("2023ugme104\r\nBcc:attacker@example.com") is None
    assert college_email("not-a-registration") is None


def test_reg_from_login_id_accepts_registration_or_college_email():
    assert reg_from_login_id("2023ugme104") == "2023ugme104"
    assert reg_from_login_id(" 2023UGME104@NITJSR.AC.IN ") == "2023ugme104"


def test_reg_from_login_id_rejects_other_domains_and_header_injection():
    assert reg_from_login_id("2023ugme104@example.com") is None
    assert reg_from_login_id("2023ugme104\r\nBcc:attacker@example.com@nitjsr.ac.in") is None