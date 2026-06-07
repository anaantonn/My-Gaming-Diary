from sqlalchemy import text


class Sql:
    """SQL statements for database operations."""
    @staticmethod
    def init_db(conn):
        """Create tables if they do not already exist."""
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id           SERIAL PRIMARY KEY,
                open_id      VARCHAR(255) UNIQUE NOT NULL,
                display_name VARCHAR(255),
                created_at   TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS games (
                app_id    INTEGER PRIMARY KEY,
                game_name VARCHAR(255) NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sessions (
                id               SERIAL PRIMARY KEY,
                user_id          INTEGER NOT NULL REFERENCES users(id),
                app_id           INTEGER NOT NULL REFERENCES games(app_id),
                start_time       TIMESTAMPTZ NOT NULL,
                end_time         TIMESTAMPTZ NOT NULL,
                duration_minutes INTEGER NOT NULL
            )
        """))

    @staticmethod
    def init_views(conn):
        """Create or replace all aggregation views."""
        conn.execute(text("""
            CREATE OR REPLACE VIEW user_game_totals AS
            SELECT
                s.user_id,
                s.app_id,
                g.game_name,
                SUM(s.duration_minutes) AS total_duration_minutes,
                COUNT(*)                AS session_count
            FROM sessions s
            JOIN games g ON g.app_id = s.app_id
            GROUP BY s.user_id, s.app_id, g.game_name
        """))
        conn.execute(text("""
            CREATE OR REPLACE VIEW user_daily_playtime AS
            SELECT
                s.user_id,
                s.app_id,
                g.game_name,
                DATE(s.start_time)      AS play_date,
                SUM(s.duration_minutes) AS game_minutes,
                SUM(SUM(s.duration_minutes)) OVER (
                    PARTITION BY s.user_id, DATE(s.start_time)
                )                       AS day_total_minutes
            FROM sessions s
            JOIN games g ON g.app_id = s.app_id
            GROUP BY s.user_id, s.app_id, g.game_name, DATE(s.start_time)
        """))
        conn.execute(text("""
            CREATE OR REPLACE VIEW user_monthly_playtime AS
            SELECT
                s.user_id,
                s.app_id,
                g.game_name,
                DATE_TRUNC('month', s.start_time) AS play_month,
                SUM(s.duration_minutes)           AS game_minutes,
                SUM(SUM(s.duration_minutes)) OVER (
                    PARTITION BY s.user_id, DATE_TRUNC('month', s.start_time)
                )                                 AS month_total_minutes
            FROM sessions s
            JOIN games g ON g.app_id = s.app_id
            GROUP BY s.user_id, s.app_id, g.game_name, DATE_TRUNC('month', s.start_time)
        """))
        conn.execute(text("""
            CREATE OR REPLACE VIEW user_yearly_playtime AS
            SELECT
                s.user_id,
                s.app_id,
                g.game_name,
                DATE_TRUNC('year', s.start_time) AS play_year,
                SUM(s.duration_minutes)          AS game_minutes,
                SUM(SUM(s.duration_minutes)) OVER (
                    PARTITION BY s.user_id, DATE_TRUNC('year', s.start_time)
                )                                AS year_total_minutes
            FROM sessions s
            JOIN games g ON g.app_id = s.app_id
            GROUP BY s.user_id, s.app_id, g.game_name, DATE_TRUNC('year', s.start_time)
        """))

    @staticmethod
    def get_user(conn, open_id):
        """Return the user's id if they exist, otherwise None."""
        result = conn.execute(
            text("SELECT id FROM users WHERE open_id = :open_id"),
            {"open_id": open_id}
        )
        row = result.fetchone()
        return row[0] if row else None

    @staticmethod
    def create_user(conn, open_id, display_name):
        """Insert a new user and return their generated id."""
        result = conn.execute(
            text("""
                INSERT INTO users (open_id, display_name)
                VALUES (:open_id, :display_name)
                RETURNING id
            """),
            {"open_id": open_id, "display_name": display_name}
        )
        return result.fetchone()[0]

    @staticmethod
    def get_or_create_game(conn, app_id, game_name):
        """Register a game in the catalog if it is not already there.
        Does nothing if the app_id already exists.
        """
        conn.execute(
            text("""
                INSERT INTO games (app_id, game_name)
                VALUES (:app_id, :game_name)
                ON CONFLICT (app_id) DO NOTHING
            """),
            {"app_id": app_id, "game_name": game_name}
        )

    @staticmethod
    def save_session(conn, user_id, app_id, start_time, end_time, duration_minutes):
        """Insert a completed play session."""
        conn.execute(
            text("""
                INSERT INTO sessions
                    (user_id, app_id, start_time, end_time, duration_minutes)
                VALUES (:user_id, :app_id, :start_time, :end_time, :duration_minutes)
            """),
            {
                "user_id": user_id,
                "app_id": app_id,
                "start_time": start_time,
                "end_time": end_time,
                "duration_minutes": duration_minutes,
            }
        )

    @staticmethod
    def get_sessions_by_user(conn, user_id, date=None):
        """Return all sessions for a user with game name, newest first."""
        result = conn.execute(
            text("""
                SELECT
                    s.id,
                    s.app_id,
                    g.game_name,
                    s.start_time,
                    s.end_time,
                    s.duration_minutes
                FROM sessions s
                JOIN games g ON g.app_id = s.app_id
                WHERE s.user_id = :user_id
                AND (:date IS NULL OR DATE(s.start_time) = :date)
                ORDER BY s.start_time DESC
            """),
            {"user_id": user_id, "date": date}
        )
        return result.fetchall()

    @staticmethod
    def get_game_totals(conn, user_id):
        """Total playtime and session count per game for a user."""
        result = conn.execute(
            text("""
                SELECT app_id, game_name, total_duration_minutes, session_count
                FROM user_game_totals
                WHERE user_id = :user_id
                ORDER BY total_duration_minutes DESC
            """),
            {"user_id": user_id}
        )
        return result.fetchall()

    @staticmethod
    def get_daily_playtime(conn, user_id, date=None, month=None):
        """Playtime per game per day, plus the day total, for a user."""
        result = conn.execute(
            text("""
                SELECT app_id, game_name, play_date, game_minutes, day_total_minutes
                FROM user_daily_playtime
                WHERE user_id = :user_id
                AND (:date IS NULL OR play_date = :date)
                AND (:month IS NULL OR TO_CHAR(play_date, 'YYYY-MM') = :month)
                ORDER BY play_date ASC
            """),
            {"user_id": user_id, "date": date, "month": month}
        )
        return result.fetchall()

    @staticmethod
    def get_monthly_playtime(conn, user_id, year=None):
        """Playtime per game per month, plus the month total, for a user."""
        result = conn.execute(
            text("""
                SELECT app_id, game_name, play_month, game_minutes, month_total_minutes
                FROM user_monthly_playtime
                WHERE user_id = :user_id
                AND (:year IS NULL OR EXTRACT(YEAR FROM play_month) = :year)
                ORDER BY play_month ASC
            """),
            {"user_id": user_id, "year": year}
        )
        return result.fetchall()

    @staticmethod
    def get_yearly_playtime(conn, user_id):
        """Playtime per game per year, plus the year total, for a user."""
        result = conn.execute(
            text("""
                SELECT app_id, game_name, play_year, game_minutes, year_total_minutes
                FROM user_yearly_playtime
                WHERE user_id = :user_id
                ORDER BY play_year DESC
            """),
            {"user_id": user_id}
        )
        return result.fetchall()
