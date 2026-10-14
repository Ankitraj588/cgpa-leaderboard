PROGRAM_MAP = {"ug": "Undergraduate", "pg": "Postgraduate"}

BRANCH_MAP = {
    "cs": "Computer Science",
    "it": "Information Technology",
    "me": "Mechanical",
    "ce": "Civil",
    "ec": "Electronics",
    "ee": "Electrical",
}


def parse_reg(reg):
    reg = reg.lower().strip()
    return (
        reg[:4],                                  # year
        PROGRAM_MAP.get(reg[4:6], "Unknown"),     # program
        BRANCH_MAP.get(reg[6:8], "Unknown"),      # branch
        reg[8:],                                  # roll
    )