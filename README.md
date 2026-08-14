## 🛠️ Tech Stack

### Backend
- Python
- Flask
- PostgreSQL (Neon)
- CS50 SQL Library

### Frontend
- HTML
- CSS
- Bootstrap

### Deployment
- Vercel

## 🏗️ Database Schema

### `users`
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary Key |
| reg | TEXT | Registration Number |
| name | TEXT | Student Name |
| password | TEXT | Hashed Password |
| year | TEXT | Admission Year |
| program | TEXT | UG Program |
| branch | TEXT | Branch |
| roll | TEXT | Roll Number |

---

### `results`
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary Key |
| reg | TEXT | Foreign Key (users.reg) |
| semester | TEXT | Semester |
| sgpa | REAL | Semester GPA |
| cgpa | REAL | Cumulative GPA |

---

## ▶️ Running the Project

### 1️⃣ Clone Repository
```bash
git clone <repo-link>
cd project
