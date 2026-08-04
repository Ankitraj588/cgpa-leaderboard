import sqlite3
import random

conn = sqlite3.connect("cgpa.db")
cur = conn.cursor()

print("Seeding 100+ fake users & CGPA data...")

names = [
    "Aman", "Neha", "Ranjeet", "Ankit", "Priyanshu", "Aditya", "Piyush",
    "Rahul", "Kriti", "Deepak", "Sakshi", "Nikita", "Arjun", "Rohit",
    "Shivam", "Ishika", "Aditi", "Sumit", "Harsh", "Naman", "Aisha",
    "Riya", "Muskan", "Ayan", "Shreya", "Tanya", "Dev", "Aarav",
    "Ansh", "Anvi", "Anushka", "Aayush", "Divyansh", "Sarthak",
    "Pragati", "Tanmay", "Navya", "Sameer", "Pratik"
]

branches = ["CSE", "Mechanical", "Electrical", "Civil", "ECE", "IT"]
years = ["2022", "2023", "2024"]

students = []
roll = 100

# -------- USERS ----------
for i in range(100):
    name = random.choice(names) + " " + random.choice(["Raj", "Kumar", "Sharma", "Agarwal", "Verma", "Singh"])
    year = random.choice(years)
    branch = random.choice(branches)

    prefix = branch[:2].lower()
    reg = f"{year}ug{prefix}{roll}"
    roll += 1

    students.append((reg, name, "test", year, "UG", branch, str(roll)))

cur.executemany(
    "INSERT OR IGNORE INTO users (reg, name, password, year, program, branch, roll) VALUES (?, ?, ?, ?, ?, ?, ?)",
    students
)


print("Users inserted!")

# -------- RESULTS ----------
def random_sgpa():
    return round(random.uniform(6.0, 10.0), 2)

for s in students:
    reg = s[0]
    total = 0
    sem_count = random.randint(1, 6)

    for sem in range(1, sem_count + 1):
        sgpa = random_sgpa()
        total += sgpa
        cgpa = round(total / sem, 2)

        cur.execute(
            "INSERT INTO results (reg, semester, sgpa, cgpa) VALUES (?, ?, ?, ?)",
            (reg, f"Sem {sem}", sgpa, cgpa)
        )

conn.commit()
conn.close()

print("🎯 100+ Fake Students + CGPA Data Inserted Successfully!")
