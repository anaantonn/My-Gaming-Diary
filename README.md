# My Gaming Diary

Gaming Diary's dreams and aspirations are to keep a detailed track of Steam games you've played.

Track your Steam play sessions as they happen, no waiting for a yearly wrapped recap.
The script polls the Steam API in the background and automatically logs each session
(game, start time, end time, duration) to a PostgreSQL database.

## Status

Work in progress. Core tracking is functional, sessions are detected, logged to the
database, and queryable by day, month, and year. Flask foundation and Steam OpenID
authentication are in place. API routes are configured. Frontend dashoard next.

## How it works

Steam updates `playtime_forever` roughly every 30 minutes while a game is running AND
when you quit. The script polls the API every 60 seconds, detects changes in playtime,
and considers a session finished once no update has been seen for 35 minutes.

## Setup

### 1. Clone the repo and install dependencies

```bash
git clone https://github.com/anaantonn/My-Gaming-Diary.git
cd My-Gaming-Diary
pip install -r requirements.txt
```

### 2. Create a PostgreSQL database

```bash
psql -U postgres
```

```sql
CREATE DATABASE db_name;
\q
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials,
a database path should look like this:

```bash
DB_PATH=postgresql://postgres:yourpassword@localhost:5432/game_diary
```

```bash
cp .env.example .env
```

### 4. Run

```bash
python game_diary.py
```

The script creates the database tables and views automatically on first run.
Stop it at any time with `Ctrl+C` — active sessions are flushed to the database
before exit.

## Running the web server

```bash
python app.py
```

The server starts at `http://localhost:5000`.

| Route                | Description                                   |
| -------------------- | --------------------------------------------- |
| `GET /`              | Confirms the server is running                |
| `GET /health`        | Verifies the database connection is healthy   |
| `GET /auth/login`    | Redirects to Steam for authentication         |
| `GET /auth/callback` | Handles Steam's redirect and logs the user in |
| `GET /auth/logout`   | Clears the session and logs the user out      |

## Steam authentication

Login is handled via Steam OpenID 2.0. Clicking login redirects the user to
Steam's login page. After authenticating, Steam redirects back to `/auth/callback`
where the response is validated and the Steam ID is extracted. On first login
a new user row is created in the database; on subsequent logins the existing
row is returned. The Steam ID and internal user ID are stored in the Flask
session for the duration of the visit.

Profiles do not need to be public in this case, since each user authenticates
with their own Steam account, API calls are made on their behalf using
their own API key.

## Project structure

| File                 | Purpose                                                         |
| -------------------- | --------------------------------------------------------------- |
| `game_diary.py`      | Entry point —> wires everything together and runs the poll loop |
| `steam_client.py`    | Steam API wrapper                                               |
| `session_tracker.py` | Session state, timeout detection, flush logic                   |
| `database.py`        | Connection management, logging, transactions                    |
| `sql.py`             | Raw SQL queries and schema                                      |
| `config.py`          | Environment variable loading                                    |
| `logger.py`          | Logging setup (terminal + rotating file)                        |
| `app.py`             | Flask Application Factory as a web server entry point           |
| `auth.py`            | Steam OpenID login, callback and logout routes                  |
| `routes.py`          | API blueprint — JSON endpoints for sessions and playtime data   |

## Logs

Log files are written to the `logs/` directory, one file per module.
Terminal output shows `INFO` and above. Log files capture everything including `DEBUG`.

## API routes

All routes require an active session (login via Steam first).
Responses are JSON.

| Route                       | Description                                     |
| --------------------------- | ----------------------------------------------- |
| `GET /api/sessions`         | All play sessions, newest first                 |
| `GET /api/game-totals`      | Total playtime and session count per game       |
| `GET /api/playtime/daily`   | Playtime per game per day, plus daily total     |
| `GET /api/playtime/monthly` | Playtime per game per month, plus monthly total |
| `GET /api/playtime/yearly`  | Playtime per game per year, plus yearly total   |
