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
    
    # Add custom template filters
    @app.template_filter('striptags')
    def strip_tags(text):
        """Remove HTML tags from text."""
        import re
        return re.sub('<[^<]+?>', '', text)
    
    @app.template_filter('image_position')
    def image_position(x, y):
        """Convert image position values to CSS background-position."""
        return f"{x} {y}"
    
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
    from routes.seo import seo
    
    app.register_blueprint(main)
    app.register_blueprint(posts)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(search)
    app.register_blueprint(seo)
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Initialize database
    with app.app_context():
        init_db()
    
    app.run(debug=True)