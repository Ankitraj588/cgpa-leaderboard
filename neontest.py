import os
from cs50 import SQL

db = SQL(os.environ["DATABASE_URL"])

tables = db.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
print("tables:", sorted(t["table_name"] for t in tables))

cols = db.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'")
print("users columns:", sorted(c["column_name"] for c in cols))

print("users count:", db.execute("SELECT COUNT(*) AS n FROM users")[0]["n"])
print("login query:", len(db.execute("SELECT * FROM users WHERE lower(reg) = ?", "2023ugme104")), "row(s)")

try:
    db.execute("SELECT COUNT(*) AS n FROM reset_requests")
    print("reset_requests: ok")
except Exception as e:
    print("reset_requests: PROBLEM -", type(e).__name__)
