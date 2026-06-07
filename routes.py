from functools import wraps

from flask import Blueprint, current_app, jsonify, request, session

from logger import get_logger

logger = get_logger(__name__)
routes = Blueprint("routes", __name__, url_prefix="/api")


def login_required(f):
    """Decorator to ensure a user is authenticated before accessing a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Authentication required."}), 401
        return f(*args, **kwargs)
    return decorated_function

@routes.route("/sessions")
@login_required
def get_sessions():
    try:
        date_filter = request.args.get("date")
        db = current_app.extensions["db"]
        rows = db.get_sessions_by_user(session["user_id"], date_filter)
        return jsonify([
            {
                "id": row.id,
                "app_id": row.app_id,
                "game_name": row.game_name,
                "start_time": row.start_time.isoformat(),
                "end_time": row.end_time.isoformat(),
                "duration_minutes": row.duration_minutes,
            }
            for row in rows
        ])
    except Exception as e:
        logger.error(f"GET /api/sessions failed: {e}")
        return jsonify({"error": "Failed to fetch sessions."}), 500

@routes.route("/game-totals")
@login_required
def get_game_totals():
    try:
        db = current_app.extensions["db"]
        rows = db.get_game_totals(session["user_id"])
        return jsonify([
            {
                "app_id": row.app_id,
                "game_name": row.game_name,
                "total_duration_minutes": row.total_duration_minutes,
                "session_count": row.session_count,
            }
            for row in rows
        ])
    except Exception as e:
        logger.error(f"GET /api/game-totals failed: {e}")
        return jsonify({"error": "Failed to fetch game totals."}), 500

@routes.route("/playtime/daily")
@login_required
def get_daily_playtime():
    try:
        date_filter = request.args.get("date")
        month_filter = request.args.get("month")
        db = current_app.extensions["db"]
        rows = db.get_daily_playtime(
            session["user_id"],
            date_filter,
            month_filter
        )
        return jsonify([
            {
                "app_id": row.app_id,
                "game_name": row.game_name,
                "play_date": row.play_date.isoformat(),
                "game_minutes": row.game_minutes,
                "day_total_minutes": row.day_total_minutes,
            }
            for row in rows
        ])
    except Exception as e:
        logger.error(f"GET /api/playtime/daily failed: {e}")
        return jsonify({"error": "Failed to fetch daily playtime."}), 500

@routes.route("/playtime/monthly")
@login_required
def get_monthly_playtime():
    try:
        year_filter = request.args.get("year", type=int)
        db = current_app.extensions["db"]
        rows = db.get_monthly_playtime(session["user_id"], year_filter)
        return jsonify([
            {
                "app_id":                row.app_id,
                "game_name":             row.game_name,
                "play_month":            row.play_month.isoformat(),
                "game_minutes":          row.game_minutes,
                "month_total_minutes":   row.month_total_minutes,
            }
            for row in rows
        ])
    except Exception as e:
        logger.error(f"GET /api/playtime/monthly failed: {e}")
        return jsonify({"error": "Failed to fetch monthly playtime."}), 500


@routes.route("/playtime/yearly")
@login_required
def get_yearly_playtime():
    try:
        db = current_app.extensions["db"]
        rows = db.get_yearly_playtime(session["user_id"])
        return jsonify([
            {
                "app_id":                row.app_id,
                "game_name":             row.game_name,
                "play_year":             row.play_year.isoformat(),
                "game_minutes":          row.game_minutes,
                "year_total_minutes":    row.year_total_minutes,
            }
            for row in rows
        ])
    except Exception as e:
        logger.error(f"GET /api/playtime/yearly failed: {e}")
        return jsonify({"error": "Failed to fetch yearly playtime."}), 500
