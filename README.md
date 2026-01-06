# 🎓 CGPA Leaderboard — NIT Jamshedpur

A full-stack Flask web application that allows **NIT Jamshedpur students** to:

- Register & Log in securely  
- Submit Semester SGPA and Cumulative CGPA  
- View their academic records  
- Compete on a CGPA leaderboard  
- Filter leaderboard by **Year** and **Branch**  
- See **their personal rank**

Built as my **CS50 Final Project**.

---

## 🚀 Features

### 🔐 Authentication
• Student Signup  
• Secure Login  
• Password Hashing  
• Session Handling  
• Password Reset Support  

---

### 🎓 CGPA Management
Students can:
- Add Semester Name
- Add SGPA
- Add Cumulative CGPA  
- View Academic History  

Duplicate semester entries automatically update.

---

### 🏆 Leaderboard
Displays ranked students based on CGPA:




Includes:
- Overall Ranking  
- Branch Filter  
- Year Filter  
- Combined Filter  
- Rank ties handled correctly  
- Shows **Your Rank** at top  

---

## 🎨 UI & UX
- Modern Dark Theme  
- Clean Responsive Layout  
- Auto-Hide Flash Messages  
- Custom Logo Branding  

---

## 🛠️ Tech Stack

### Backend
- Python
- Flask
- SQLite
- CS50 SQL Library

### Frontend
- HTML
- CSS
- Bootstrap

---

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
