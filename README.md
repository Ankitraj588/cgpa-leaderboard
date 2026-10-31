# CGPA Leaderboard

A web app where NIT Jamshedpur students register with their college email, record their semester-wise SGPA/CGPA, and see where they stand on a leaderboard filtered by year and branch.

**Live:** https://cgpa-leaderboard-eight.vercel.app/

## Features

- Sign up and log in with your college email (`2023ugme104@nitjsr.ac.in`); year, program, branch and roll are read from the registration number
- Add or update SGPA/CGPA for each semester
- Leaderboard with year and branch filters and tie-aware ranking; your own row is highlighted
- JWT authentication: short-lived access token plus a refresh token, both in httpOnly cookies, with silent renewal
- Password reset by emailed link: valid for 15 minutes, works once, and the same reply is shown whether or not the account exists
- Rate limiting on reset requests, per account and per IP
- Responsive layout with light and dark themes

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Python, Flask, PyJWT, CS50 SQL library |
| Database | PostgreSQL (Neon); SQLite for local development |
| Frontend | HTML, CSS, Bootstrap, Jinja templates |
| Email | Gmail SMTP |
| Deployment | Vercel |
| Testing | pytest |

## How authentication works

1. On login or signup the server sets two httpOnly cookies: an **access token** (15 minutes) and a **refresh token** (7 days).
2. A `before_request` hook reads the access cookie on every request and sets `g.user`.
3. If the access token has expired, the hook falls back to the refresh token and issues a new access token, so the user stays signed in.
4. Routes are protected with the `@jwt_required` decorator.
5. Each token carries a `type` claim (`access`, `refresh` or `reset`), so one kind can never be used as another.

Password reset uses a third token type. The token holds a short fingerprint of the current password hash, so the link stops working as soon as the password changes.

## Project structure

```
app/
├── __init__.py          # app factory, request hooks, blueprints
├── extensions.py        # database connection
├── utils.py             # registration-number parsing, college email helpers
├── mailer.py            # sends email over SMTP
├── ratelimit.py         # database-backed rate limiting
├── auth/                # login, signup, reset (routes, jwt_utils, middleware)
├── cgpa/                # semester results
└── leaderboard/         # ranking and filters
api/index.py             # Vercel entrypoint
config.py                # configuration from environment variables
static/                  # style.css, main.js
templates/               # Jinja templates
tests/                   # pytest suite
```

## Database schema

### `users`

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| reg | TEXT | Registration number (unique) |
| name | TEXT | Student name |
| password | TEXT | Hashed password |
| year | TEXT | Admission year |
| program | TEXT | Program (e.g. Undergraduate) |
| branch | TEXT | Branch (e.g. Mechanical) |
| roll | TEXT | Roll number |

### `results`

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| reg | TEXT | Registration number (`users.reg`) |
| semester | TEXT | Semester |
| sgpa | REAL | Semester GPA |
| cgpa | REAL | Cumulative GPA |

### `reset_requests`

| Field | Type | Description |
|-------|------|-------------|
| bucket | TEXT | Rate-limit key, e.g. `reg:2023ugme104` or `ip:1.2.3.4` |
| ts | BIGINT | Unix time of the request |

<details>
<summary>SQL to create the tables (PostgreSQL)</summary>

```sql
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  reg TEXT UNIQUE NOT NULL,
  name TEXT,
  password TEXT,
  year TEXT,
  program TEXT,
  branch TEXT,
  roll TEXT
);

CREATE TABLE IF NOT EXISTS results (
  id SERIAL PRIMARY KEY,
  reg TEXT NOT NULL,
  semester TEXT,
  sgpa REAL,
  cgpa REAL
);

CREATE TABLE IF NOT EXISTS reset_requests (
  bucket TEXT NOT NULL,
  ts BIGINT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_reset_requests_bucket_ts ON reset_requests (bucket, ts);
```

For SQLite, use `id INTEGER PRIMARY KEY` instead of `SERIAL PRIMARY KEY`.

</details>

## Environment variables

| Name | Required | Purpose |
|---|---|---|
| `SECRET_KEY` | yes | Flask secret key |
| `JWT_SECRET_KEY` | yes | Signs the JWTs. Use a different value from `SECRET_KEY` |
| `DATABASE_URL` | yes | `postgresql://...` for Neon, or `sqlite:///cgpa.db` locally |
| `COOKIE_SECURE` | production | Set to `1` on HTTPS so cookies are only sent securely |
| `MAIL_USERNAME` | for reset email | Gmail address used to send mail |
| `MAIL_PASSWORD` | for reset email | Gmail **app password** (not your normal password) |
| `SITE_URL` | for reset email | Base URL used in reset links, no trailing slash |
| `MAIL_PORT` | no | `465` by default; `587` if your network blocks 465 |
| `JWT_ACCESS_TOKEN_MINUTES` | no | Default `15` |
| `JWT_REFRESH_TOKEN_DAYS` | no | Default `7` |

The app refuses to start if `SECRET_KEY` or `JWT_SECRET_KEY` is missing. Generate secrets with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Never commit secrets or database files. `.gitignore` excludes `*.db`.

## Running locally

```bash
git clone https://github.com/Ankitraj588/cgpa-leaderboard.git
cd cgpa-leaderboard
pip install -r requirements.txt
```

Set the environment variables, then start the app.

**PowerShell**

```powershell
$env:SECRET_KEY = "local-secret"
$env:JWT_SECRET_KEY = "local-jwt-secret"
$env:DATABASE_URL = "sqlite:///cgpa.db"
$env:SITE_URL = "http://127.0.0.1:5000"
flask --app app run --debug
```

**Bash**

```bash
export SECRET_KEY=local-secret
export JWT_SECRET_KEY=local-jwt-secret
export DATABASE_URL=sqlite:///cgpa.db
export SITE_URL=http://127.0.0.1:5000
flask --app app run --debug
```

The SQLite file must already contain the tables above. Without `MAIL_USERNAME` and `MAIL_PASSWORD`, debug mode prints the reset link in the terminal instead of emailing it.

## Running the tests

```bash
python -m pytest tests -q
```

The tests always run against a temporary SQLite database and never touch a real one. They cover token creation and expiry, token-type misuse, protected routes, the silent refresh, the password reset flow and its rate limit, and the CGPA and ranking logic.

## Deployment (Vercel)

1. Create the tables in your Neon database (SQL above).
2. In Vercel, add the environment variables from the table, with `COOKIE_SECURE=1`.
3. Push to `main`. Vercel deploys from `api/index.py`.
4. Variables added after a deployment only apply to the next one, so redeploy after changing them.