import os

from flask import Flask, send_from_directory
from flask_cors import CORS
from .database import db

def create_app():
    # serve frontend from build directory if it exists
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
    app = Flask(__name__, static_folder=static_dir, static_url_path="")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Initialize database
    db.init_db()
    
    CORS(app)

    from .routes import api
    app.register_blueprint(api)

    @app.get("/health")
    def health():
        return {"status": "ok", "database": "sqlite"}

    # basic root route for convenience (when dist not built)
    @app.get("/")
    def index():
        if app.static_folder and os.path.exists(os.path.join(app.static_folder, "index.html")):
            return send_from_directory(app.static_folder, "index.html")
        return {"message": "Driver AI Co-Pilot API is running with SQLite database. Use /api/..."}

    # catch-all route to serve frontend files
    @app.route('/<path:path>')
    def static_proxy(path):
        if app.static_folder and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')

    return app
