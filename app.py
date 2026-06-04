import os

from flask import Flask, jsonify, render_template, session
from sqlalchemy import text
from dotenv import load_dotenv

from config import load_db_config
from database import DiaryDatabase
from logger import get_logger
from routes import routes
from auth import auth

logger = get_logger(__name__)


def create_app():
    """Factory function to create and configure the Flask app."""
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")
    app.config["STEAM_API_KEY"] = os.getenv("STEAM_API_KEY")

    if not app.secret_key:
        raise RuntimeError("SECRET_KEY is not set in .env")

    # Load database configuration and initialize connection
    db_url = load_db_config()
    app.extensions["db"] = DiaryDatabase(db_url)
    logger.info("Flask app created and database connected.")

    @app.route("/")
    def index():
        return render_template("index.html")

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

    _register_blueprints(app)

    return app

def _register_blueprints(app):
    """Register all blueprints with the Flask app."""
    app.register_blueprint(auth)
    app.register_blueprint(routes)

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
