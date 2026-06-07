from sqlalchemy import create_engine

from logger import get_logger
from sql import Sql

logger = get_logger(__name__)


class DiaryDatabase:
    """
    Encapsulates all database interactions, including schema setup and queries.
    Holds a SQLAlchemy engine that manages a connection pool internally.
    Individual connections are borrowed per operation and returned automatically.
    pool_pre_ping=True silently reconnects if a connection has gone stale.
    """

    def __init__(self, db_url):
        try:
            self.engine = create_engine(db_url, pool_pre_ping=True)
            logger.info("Database engine created.")
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def init_db(self):
        """Create tables if they do not already exist."""
        try:
            with self.engine.connect() as conn:
                Sql.init_db(conn)
                conn.commit()
            logger.info("Database tables initialised.")
        except Exception as e:
            logger.error(f"Failed to initialise tables: {e}")
            raise

    def init_views(self):
        """Create or replace all aggregation views."""
        try:
            with self.engine.connect() as conn:
                Sql.init_views(conn)
                conn.commit()
            logger.info("Database views initialised.")
        except Exception as e:
            logger.error(f"Failed to initialise views: {e}")
            raise

    def get_or_create_user(self, open_id, display_name):
        """Return the user's id, creating a new row if they do not exist yet."""
        try:
            with self.engine.connect() as conn:
                user_id = Sql.get_user(conn, open_id)
                if user_id:
                    return user_id
                user_id = Sql.create_user(conn, open_id, display_name)
                conn.commit()
                logger.info(f"New user created — open_id={open_id}, id={user_id}")
                return user_id
        except Exception as e:
            logger.error(f"Failed to get or create user open_id={open_id}: {e}")
            raise

    def get_or_create_game(self, app_id, game_name):
        """Register a game in the catalog if it is not already there."""
        try:
            with self.engine.connect() as conn:
                Sql.get_or_create_game(conn, app_id, game_name)
                conn.commit()
                logger.debug(f"Game registered — app_id={app_id}, name={game_name}")
        except Exception as e:
            logger.error(f"Failed to register game app_id={app_id}: {e}")
            raise

    def save_session(
        self,
        user_id,
        app_id,
        start_time,
        end_time,
        duration_minutes,
    ):
        """Insert a completed play session."""
        try:
            with self.engine.connect() as conn:
                Sql.save_session(conn, user_id, app_id, start_time, end_time, duration_minutes)
                conn.commit()
                logger.info(
                    f"Session saved — user_id={user_id}, app_id={app_id}, "
                    f"duration={duration_minutes}min"
                )
        except Exception as e:
            logger.error(
                f"Failed to save session — user_id={user_id}, app_id={app_id}: {e}"
            )
            raise

    def get_sessions_by_user(self, user_id, date=None):
        """Return all sessions for a user with game name, newest first."""
        try:
            with self.engine.connect() as conn:
                return Sql.get_sessions_by_user(conn, user_id, date)
        except Exception as e:
            logger.error(f"Failed to fetch sessions for user_id={user_id}: {e}")
            raise

    def get_game_totals(self, user_id):
        """Total playtime and session count per game for a user."""
        try:
            with self.engine.connect() as conn:
                return Sql.get_game_totals(conn, user_id)
        except Exception as e:
            logger.error(f"Failed to fetch game totals for user_id={user_id}: {e}")
            raise

    def get_daily_playtime(self, user_id, date=None, month=None):
        """Playtime per game per day, plus the day total, for a user."""
        try:
            with self.engine.connect() as conn:
                return Sql.get_daily_playtime(conn, user_id, date, month)
        except Exception as e:
            logger.error(f"Failed to fetch daily playtime for user_id={user_id}: {e}")
            raise

    def get_monthly_playtime(self, user_id, year=None):
        """Playtime per game per month, plus the month total, for a user."""
        try:
            with self.engine.connect() as conn:
                return Sql.get_monthly_playtime(conn, user_id, year)
        except Exception as e:
            logger.error(f"Failed to fetch monthly playtime for user_id={user_id}: {e}")
            raise

    def get_yearly_playtime(self, user_id):
        """Playtime per game per year, plus the year total, for a user."""
        try:
            with self.engine.connect() as conn:
                return Sql.get_yearly_playtime(conn, user_id)
        except Exception as e:
            logger.error(f"Failed to fetch yearly playtime for user_id={user_id}: {e}")
            raise

    def get_missing_genre_app_ids(self, user_id):
        """Return app_ids the user has played that have no genres cached yet."""
        try:
            with self.engine.connect() as conn:
                return Sql.get_missing_genre_app_ids(conn, user_id)
        except Exception as e:
            logger.error(f"Failed to fetch missing genre app_ids for user_id={user_id}: {e}")
            raise

    def save_genres(self, app_id, genres):
        """Store genre tags for a game."""
        try:
            with self.engine.connect() as conn:
                Sql.save_genres(conn, app_id, genres)
                conn.commit()
            logger.debug(f"Genres saved — app_id={app_id}, genres={genres}")
        except Exception as e:
            logger.error(f"Failed to save genres for app_id={app_id}: {e}")
            raise

    def get_playtime_by_genre(self, user_id):
        """Total playtime per genre for a user."""
        try:
            with self.engine.connect() as conn:
                return Sql.get_playtime_by_genre(conn, user_id)
        except Exception as e:
            logger.error(f"Failed to fetch playtime by genre for user_id={user_id}: {e}")
            raise

    def close(self):
        """Dispose of the engine and release all pooled connections."""
        self.engine.dispose()
        logger.info("Database engine disposed.")
