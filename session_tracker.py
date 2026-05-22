from datetime import datetime

from logger import get_logger

logger = get_logger(__name__)

SESSION_TIMEOUT_MINUTES = 35 # Steam refreshes every ~ 30 minutes


class SessionTracker:
    """
    Tracks active play sessions based on playtime snapshots from the Steam API.
    Flushes completed sessions to the database once a session has been inactive
    for SESSION_TIMEOUT_MINUTES.
    """

    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id
        self.baseline = {}
        self.active_sessions = {}

    def initialise(self, snapshot):
        """
        Set the baseline from the first snapshot.
        No sessions are started here — we only begin tracking changes from this point.
        snapshot format: {app_id: {"game_name": str, "playtime_forever": int}}
        """
        for app_id, data in snapshot.items():
            self.baseline[app_id] = data["playtime_forever"]
        logger.info(f"Baseline set for {len(self.baseline)} game(s).")

    def update(self, snapshot, now):
        """
        Process a new snapshot and update active sessions accordingly.
        - If playtime increased for a game, start or update its session.
        - If a game appears for the first time, add it to the baseline.
        snapshot format: {app_id: {"game_name": str, "playtime_forever": int}}
        """
        for app_id, data in snapshot.items():
            game_name = data["game_name"]
            current_forever = data["playtime_forever"]
            previous_forever = self.baseline.get(app_id, current_forever)
            delta = current_forever - previous_forever

            if delta > 0:
                if app_id not in self.active_sessions:
                    self.active_sessions[app_id] = {
                        "game_name": game_name,
                        "start_time": now,
                        "last_activity": now,
                        "accumulated_minutes": delta,
                    }
                    logger.info(f"Session started — {game_name}")
                else:
                    self.active_sessions[app_id]["accumulated_minutes"] += delta
                    self.active_sessions[app_id]["last_activity"] = now
                    logger.debug(
                        f"Session updated — {game_name}, "
                        f"total={self.active_sessions[app_id]['accumulated_minutes']}min"
                    )
                self.baseline[app_id] = current_forever
            else:
                # New game seen but not yet played — add to baseline for future comparison
                self.baseline.setdefault(app_id, current_forever)

    def flush_timed_out(self, now: datetime) -> None:
        """
        Flush any sessions that have had no playtime update for SESSION_TIMEOUT_MINUTES.
        These are considered finished.
        """
        timed_out = [
            app_id
            for app_id, session in self.active_sessions.items()
            if (now - session["last_activity"]).total_seconds()
            > SESSION_TIMEOUT_MINUTES * 60
        ]
        for app_id in timed_out:
            self._flush(app_id, self.active_sessions.pop(app_id))

    def flush_all(self) -> None:
        """
        Flush all active sessions regardless of timeout.
        Called on shutdown to avoid losing in-progress session data.
        """
        if not self.active_sessions:
            return
        logger.info(f"Flushing {len(self.active_sessions)} active session(s) before shutdown...")
        for app_id, session in list(self.active_sessions.items()):
            self._flush(app_id, session)
        self.active_sessions.clear()

    def _flush(self, app_id: int, session: dict) -> None:
        """Write a single completed session to the database."""
        try:
            game_name = session["game_name"]
            start_time = session["start_time"]
            end_time = session["last_activity"]
            duration = session["accumulated_minutes"]

            self.db.get_or_create_game(app_id, game_name)
            self.db.save_session(self.user_id, app_id, start_time, end_time, duration)
            logger.info(
                f"Session flushed — {game_name} | "
                f"{start_time.strftime('%d-%m-%Y %H:%M')} → "
                f"{end_time.strftime('%d-%m-%Y %H:%M')} | "
                f"{duration}min"
            )
        except Exception as e:
            logger.error(f"Failed to flush session for app_id={app_id}: {e}")
            raise
