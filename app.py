from flask import Flask, jsonify
from sqlalchemy import text

from config import load_db_config
from database import DiaryDatabase
from logger import get_logger

logger = get_logger(__name__)


def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)

    # Load database configuration and initialize connection
    db_url = load_db_config()
    app.extensions["db"] = DiaryDatabase(db_url)
    logger.info("Flask app created and database connected.")

    @app.route("/")
    def index():
        return jsonify(
            {
                "status": "ok",
                "message": "My Gaming Diary API is running."
            }
        )

    @app.route("/health")
    def health():
        try:
            # Simple query to check database connectivity
            db = app.extensions["db"]
            with db.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return jsonify(
                {
                    "status": "ok",
                    "message": "Database connection is healthy."
                }
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify(
                {
                    "status": "error",
                    "message": "Database connection failed."
                }
            ), 500

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
