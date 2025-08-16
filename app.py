"""
Story Hub - A Flask blog application with admin functionality.
"""
import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import close_db, init_db


def create_app():
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register teardown handler
    app.teardown_appcontext(close_db)
    
    # Register blueprints
    from routes.main import main
    from routes.posts import posts
    from routes.auth import auth
    from routes.admin import admin
    from routes.search import search
    
    app.register_blueprint(main)
    app.register_blueprint(posts)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(search)
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Initialize database
    with app.app_context():
        init_db()
    
    app.run(debug=True)