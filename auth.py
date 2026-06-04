import re

import requests as http
from flask import (Blueprint, current_app, jsonify,
                    redirect, request, session, url_for)
from urllib.parse import urlencode

from logger import get_logger

logger = get_logger(__name__)
auth = Blueprint("auth", __name__, url_prefix="/auth")
STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
STEAM_API_SUMMARY = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"


@auth.route("/login")
def login():
    params = {
        "openid.ns":         "http://specs.openid.net/auth/2.0",
        "openid.mode":       "checkid_setup",
        "openid.return_to":  url_for("auth.callback", _external=True),
        "openid.realm":      request.host_url,
        "openid.identity":   "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
    }
    logger.info("Redirecting user to Steam OpenID for authentication.")
    return redirect(f"{STEAM_OPENID_URL}?{urlencode(params)}")

@auth.route("/callback")
def callback():
    # Take all params Steam sent back and swap mode to verify
    params = request.args.to_dict()
    params["openid.mode"] = "check_authentication"

    response = http.post(STEAM_OPENID_URL, data=params)
    if "is_valid:true" not in response.text:
        logger.warning("Steam OpenID validation failed.")
        return jsonify({"error": "Steam authentication failed."}), 401

    # Extract Steam ID from openid.claimed_id
    # Format: https://steamcommunity.com/openid/id/<steam_id>
    claimed_id = request.args.get("openid.claimed_id", "")
    match = re.search(r"steamcommunity\.com/openid/id/(\d+)", claimed_id)
    if not match:
        logger.warning(f"Could not extract Steam ID from: {claimed_id}")
        return jsonify({"error": "Could not extract Steam ID."}), 400

    steam_id = match.group(1)
    display_name = _get_display_name(steam_id)

    db = current_app.extensions["db"]
    user_id = db.get_or_create_user(steam_id, display_name)
    logger.info(f"User logged in — steam_id={steam_id}, user_id={user_id}")

    session["user_id"] = user_id
    session["steam_id"] = steam_id

    return redirect(url_for("index"))

@auth.route("/logout")
def logout():
    session.clear()
    logger.info("User logged out.")
    return redirect(url_for("index"))

def _get_display_name(steam_id):
    """Fetch the Steam display name for a given Steam ID."""
    try:
        api_key = current_app.config.get("STEAM_API_KEY")
        response = http.get(
            STEAM_API_SUMMARY,
            params={
                "key": api_key,
                "steamids": steam_id,
            }
        )
        players = response.json()["response"]["players"]
        if players:
            return players[0]["personaname"]
    except Exception as e:
        logger.warning(f"Could not fetch display name for steam_id={steam_id}: {e}")
    return None
