import re

PROGRAM_MAP = {"ug": "Undergraduate", "pg": "Postgraduate"}

BRANCH_MAP = {
    "cs": "Computer Science",
    "it": "Information Technology",
    "me": "Mechanical",
    "ce": "Civil",
    "ec": "Electronics",
    "ee": "Electrical",
}

REG_PATTERN = re.compile(r"[0-9]{4}(ug|pg)[a-z]{2}[0-9a-z]+")
COLLEGE_DOMAIN = "nitjsr.ac.in"


def parse_reg(reg):
    reg = reg.lower().strip()
    return (
        reg[:4],
        PROGRAM_MAP.get(reg[4:6], "Unknown"),
        BRANCH_MAP.get(reg[6:8], "Unknown"),
        reg[8:],
    )


def college_email(reg):
    """Return the college address for a reg number, or None if the format is off."""
    reg = (reg or "").lower().strip()
    if not REG_PATTERN.fullmatch(reg):
        return None
    return f"{reg}@{COLLEGE_DOMAIN}"


def reg_from_login_id(value):
    """Accept a college email or registration number and return the registration number."""
    value = (value or "").lower().strip()
    if "@" in value:
        local, _, domain = value.partition("@")
        if domain != COLLEGE_DOMAIN:
            return None
        value = local
    return value if REG_PATTERN.fullmatch(value) else None