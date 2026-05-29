import time
from datetime import datetime, timezone

from config import load_config, load_db_config
from database import DiaryDatabase
from logger import get_logger
from session_tracker import SessionTracker, SESSION_TIMEOUT_MINUTES
from steam_client import SteamClient

logger = get_logger(__name__)

POLL_INTERVAL_SECONDS = 60  # how often to poll the Steam API, in seconds


def poll_loop(users):
    """Main polling loop. Runs until interrupted by Ctrl+C."""
    logger.info(f"Polling every {POLL_INTERVAL_SECONDS}s. "
                f"Session timeout: {SESSION_TIMEOUT_MINUTES}min.")

    try:
        while True:
            now = datetime.now(timezone.utc)
            logger.info(f"Polling at {now.astimezone().strftime('%H:%M:%S')} ...")
            for steam, tracker in users:
                snapshot = steam.get_playtime_snapshot()
                tracker.update(snapshot, now)
                tracker.flush_timed_out(now)
            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logger.info("Shutdown requested — flushing active sessions...")
        for _, tracker in users:
            tracker.flush_all()
        logger.info("Done.")


def main():
    # Load credentials and database URL from .env
    try:
        api_key, steam_ids = load_config()
        db_url = load_db_config()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise SystemExit(f"Configuration error: {e}")

    with DiaryDatabase(db_url) as db:
        # Set up schema on first run, no-op on subsequent runs
        db.init_db()
        db.init_views()

        users = []
        for steam_id in steam_ids:
            # Initialise Steam client
            try:
                steam = SteamClient(api_key, steam_id)
            except Exception:
                logger.error("Failed to initialise Steam client. " \
                                "Check your API key and Steam ID.")
                raise SystemExit("Failed to initialise Steam client. " \
                                    "Check your API key.")

            # Creates a new row on first run, returns existing id after
            display_name = steam.get_display_name()
            user_id = db.get_or_create_user(steam_id, display_name)
            logger.info(f"Logged in as {display_name} (user_id={user_id})")

            # Take the first snapshot to establish a baseline before tracking begins
            initial_snapshot = steam.get_playtime_snapshot()
            if not initial_snapshot:
                logger.error("Initial Steam API call returned no data. " \
                                "Check your Steam ID and API key.")
                raise SystemExit("Initial Steam API call returned no data. " \
                                    "Check your Steam ID and API key.")

            tracker = SessionTracker(db, user_id)
            tracker.initialise(initial_snapshot)
            users.append((steam, tracker))

        poll_loop(users)


if __name__ == "__main__":
    main()
