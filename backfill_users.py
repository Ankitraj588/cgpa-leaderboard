import sys

from app.extensions import db
from app.utils import PROGRAM_MAP, BRANCH_MAP, parse_reg

APPLY = "--apply" in sys.argv

rows = db.execute("""
    SELECT reg, year, program, branch, roll FROM users
    WHERE year    IS NULL OR year    = ''
       OR program IS NULL OR program = ''
       OR branch  IS NULL OR branch  = ''
       OR roll    IS NULL OR roll    = ''
""")

print(f"{len(rows)} user(s) with missing details\n")
fixed = skipped = 0

for u in rows:
    reg = (u["reg"] or "").lower().strip()

    # Only trust registration numbers that really match the format
    if not (reg[:4].isdigit() and reg[4:6] in PROGRAM_MAP
            and reg[6:8] in BRANCH_MAP and reg[8:]):
        print(f"SKIP   {u['reg']}  (doesn't match the YYYYuuBBnnn format)")
        skipped += 1
        continue

    year, program, branch, roll = parse_reg(reg)

    # Fill only the blanks, never overwrite values that already exist
    new = {
        "year":    u["year"]    or year,
        "program": u["program"] or program,
        "branch":  u["branch"]  or branch,
        "roll":    u["roll"]    or roll,
    }
    print(f"FIX    {u['reg']}  ->  {new}")

    if APPLY:
        db.execute(
            "UPDATE users SET year = ?, program = ?, branch = ?, roll = ? WHERE reg = ?",
            new["year"], new["program"], new["branch"], new["roll"], u["reg"],
        )
    fixed += 1

print(f"\n{fixed} fixable, {skipped} skipped.")
print("Changes WRITTEN." if APPLY else "Dry run only. Re-run with --apply to save.")