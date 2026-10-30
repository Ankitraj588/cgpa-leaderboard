from config import _db_url
from app.utils import college_email, reg_from_login_id


def test_db_url_forces_psycopg2():
    assert _db_url("postgres://u:p@h/db") == "postgresql+psycopg2://u:p@h/db"
    assert _db_url("postgresql://u:p@h/db?sslmode=require") == "postgresql+psycopg2://u:p@h/db?sslmode=require"
    assert _db_url("postgresql+psycopg://u:p@h/db") == "postgresql+psycopg2://u:p@h/db"
    assert _db_url("sqlite:///cgpa.db") == "sqlite:///cgpa.db"


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