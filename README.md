# My Gaming Diary

Gaming Dairy's dreams and aspirations are to keep a detailed track of Steam games you've played.

Track your Steam play sessions as they happen, no waiting for a yearly wrapped recap.
The script polls the Steam API in the background and automatically logs each session
(game, start time, end time, duration) to a PostgreSQL database.

## Status

Work in progress. Core tracking is functional, sessions are detected, logged to the
database, and queryable by day, month, and year. A web frontend is planned.

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

## Project structure

| File | Purpose |
| --- | --- |
| `game_diary.py` | Entry point —> wires everything together and runs the poll loop |
| `steam_client.py` | Steam API wrapper |
| `session_tracker.py` | Session state, timeout detection, flush logic |
| `database.py` | Connection management, logging, transactions |
| `sql.py` | Raw SQL queries and schema |
| `config.py` | Environment variable loading |
| `logger.py` | Logging setup (terminal + rotating file) |

## Logs

Log files are written to the `logs/` directory, one file per module.
Terminal output shows `INFO` and above. Log files capture everything including `DEBUG`.
