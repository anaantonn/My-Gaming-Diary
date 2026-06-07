# My Gaming Diary

Gaming Diary's dreams and aspirations are to keep a detailed track of Steam games you've played.

Track your Steam play sessions as they happen, no waiting for a yearly wrapped recap.
The script polls the Steam API in the background and automatically logs each session
(game, start time, end time, duration) to a PostgreSQL database.

## Status

Work in progress. Core tracking is functional, sessions are detected, logged to the
database, and queryable by day, month, and year. Flask foundation and Steam OpenID
authentication are in place. API routes are configured.
Frontend dashboard complete — three-page web application with a daily diary view,
monthly and yearly playtime charts, and an all-time overview with game and year breakdowns.

## How it works

Steam updates `playtime_forever` roughly every 30 minutes while a game is running AND
when you quit. The script polls the API every 60 seconds, detects changes in playtime,
and considers a session finished once no update has been seen for 35 minutes.

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/anaantonn/My-Gaming-Diary.git
cd My-Gaming-Diary
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
```

```bash
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a PostgreSQL database

```bash
psql -U postgres
```

```sql
CREATE DATABASE db_name;
\q
```

### 5. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials,
a database path should look like this:

```bash
DB_PATH=postgresql://postgres:yourpassword@localhost:5432/game_diary
```

```bash
cp .env.example .env
```

### 6. Run

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

| Route                | Description                                       |
| -------------------- | ------------------------------------------------- |
| `GET /`              | Homepage — daily diary or login prompt            |
| `GET /stats`         | Monthly and yearly playtime charts                |
| `GET /overview`      | All-time game breakdown and year-by-year overview |
| `GET /health`        | Verifies the database connection is healthy       |
| `GET /auth/login`    | Redirects to Steam for authentication             |
| `GET /auth/callback` | Handles Steam's redirect and logs the user in     |
| `GET /auth/logout`   | Clears the session and logs the user out          |

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

| File                      | Purpose                                                          |
| ------------------------- | ---------------------------------------------------------------- |
| `game_diary.py`           | Entry point — wires everything together and runs the poll loop   |
| `steam_client.py`         | Steam API wrapper                                                |
| `session_tracker.py`      | Session state, timeout detection, flush logic                    |
| `database.py`             | Connection management, logging, transactions                     |
| `sql.py`                  | Raw SQL queries and schema                                       |
| `config.py`               | Environment variable loading                                     |
| `logger.py`               | Logging setup (terminal + rotating file)                         |
| `app.py`                  | Flask Application Factory as a web server entry point            |
| `auth.py`                 | Steam OpenID login, callback and logout routes                   |
| `routes.py`               | API blueprint — JSON endpoints for sessions and playtime data    |
| `templates/base.html`     | Shared layout — navigation, Tailwind CSS v4, Chart.js            |
| `templates/index.html`    | Homepage — login prompt or daily diary entry                     |
| `templates/stats.html`    | Monthly and yearly playtime charts with period pickers           |
| `templates/overview.html` | All-time game breakdown, year-by-year, and genre doughnut charts |
| `static/js/nav.js`        | Shared navigation — highlights the active page in the nav bar    |
| `static/js/main.js`       | Homepage — date picker, session table population                 |
| `static/js/stats.js`      | Stats page — bar charts, month/year pickers, tab switching       |
| `static/js/overview.js`   | Overview page — all-time and yearly doughnut charts              |

## Logs

Log files are written to the `logs/` directory, one file per module.
Terminal output shows `INFO` and above. Log files capture everything including `DEBUG`.

## API routes

All routes require an active session (login via Steam first).
Responses are JSON.

| Route                        | Query params                           | Description                                        |
| ---------------------------- | -------------------------------------- | -------------------------------------------------- |
| `GET /api/sessions`          | `?date=YYYY-MM-DD`                     | Play sessions for a user, newest first             |
| `GET /api/game-totals`       | —                                      | All-time total playtime and session count per game |
| `GET /api/playtime/daily`    | `?date=YYYY-MM-DD` or `?month=YYYY-MM` | Playtime per game per day                          |
| `GET /api/playtime/monthly`  | `?year=YYYY`                           | Playtime per game per month                        |
| `GET /api/playtime/yearly`   | —                                      | Playtime per game per year                         |
| `GET /api/playtime/by-genre` | —                                      | Total playtime per genre across all sessions       |

## Frontend

The web interface is built with Jinja2 templates and styled with Tailwind CSS v4 (CDN).
Charts are rendered with Chart.js (CDN). Templates live in the `templates/` directory
and all extend `base.html`, which provides the shared gradient background, navigation
bar, and CDN script tags.

Unauthenticated users see a login prompt on the homepage and are redirected to `/`
from any other page. The nav bar is only rendered for logged-in users.
`nav.js` is loaded on every page and highlights the active nav item by reading
the page's root element ID (`homepage`, `statspage`, `overviewpage`).

### Pages

**Home (`/`)** — Shows the current day's play sessions in a table. A date picker
and a reset-to-today button let you browse any past day. Sessions are grouped by
game and show start time, end time, and duration in minutes.

**Stats (`/stats`)** — Two chart views selectable via a sliding tab:

- _Monthly_ — bar chart of the top 3 games per day for a chosen month.
  A month picker with arrow navigation and a month/year popover lets you scroll
  through any past month.
- _Yearly_ — bar chart of the top 5 games per month for a chosen year.
  A year picker with the same arrow and popover pattern.

**Overview (`/overview`)** — Three doughnut charts:

- _All-time by game_ — each game's share of total playtime ever recorded,
  top 8 shown individually with the remainder grouped as "Others".
- _Year by year_ — each calendar year's share of total playtime.
- _By genre_ — playtime broken down by Steam genre tag. A game contributes
  its minutes to every genre it belongs to. Genres are fetched from the Steam
  Store API on first load and cached in the database for subsequent visits.
