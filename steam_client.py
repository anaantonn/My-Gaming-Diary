from steam_web_api import Steam

from logger import get_logger

logger = get_logger(__name__)


class SteamClient:
    """
    Thin wrapper around the python-steam-api library.
    Handles all Steam API calls and formats responses into
    the shapes the rest of the app expects.
    If the underlying library or API changes, only this file needs updating.
    """

    def __init__(self, api_key, steam_id):
        try:
            self.steam = Steam(api_key)
            self.steam_id = steam_id
            logger.info(f"Steam client initialised for steam_id={steam_id}")
        except Exception as e:
            logger.error(f"Failed to initialise Steam client: {e}")
            raise

    def get_playtime_snapshot(self):
        """
        Fetch recently played games and return a snapshot of current playtime.

        Returns:
            {
                app_id (int): {
                    "game_name": str,
                    "playtime_forever": int  (total minutes ever played)
                },
                ...
            }
        Returns an empty dict if the API call fails, so the poll loop can
        continue rather than crash.
        """
        try:
            data = self.steam.users.get_user_recently_played_games(self.steam_id)
            snapshot = {
                game["appid"]: {
                    "game_name": game["name"],
                    "playtime_forever": game["playtime_forever"],
                }
                for game in data.get("games", [])
            }
            logger.debug(f"Snapshot fetched — {len(snapshot)} game(s) in recently played.")
            return snapshot
        except Exception as e:
            logger.warning(f"Failed to fetch playtime snapshot, returning empty: {e}")
            return {}

    def get_display_name(self):
        """
        Fetch the user's Steam display name.
        Used when creating a new user row in the database.
        Returns None if the call fails — display_name is optional.
        """
        try:
            data = self.steam.users.get_user_details(self.steam_id)
            name = data.get("player", {}).get("personaname")
            logger.debug(f"Display name fetched — {name}")
            return name
        except Exception as e:
            logger.warning(f"Failed to fetch display name: {e}")
            return None
