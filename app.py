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
    
    @app.template_filter('format_date')
    def format_date(date_string, format_type='short'):
        """Format date string for display."""
        if not date_string:
            return 'Unknown'
        
        try:
            from datetime import datetime
            # Handle string dates from database
            if isinstance(date_string, str):
                # Try different formats
                for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S.%f'):
                    try:
                        date_obj = datetime.strptime(date_string, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    # Fallback to just the date part
                    return date_string[:10] if len(date_string) >= 10 else date_string
            else:
                date_obj = date_string
            
            if format_type == 'short':
                return date_obj.strftime('%b %d, %Y')
            elif format_type == 'long':
                return date_obj.strftime('%B %d, %Y')
            else:
                return date_obj.strftime('%Y-%m-%d')
        except:
            # Fallback for any parsing errors
            return date_string[:10] if isinstance(date_string, str) and len(date_string) >= 10 else str(date_string)
    
    @app.template_filter('take')
    def take_filter(iterable, count):
        """Take first N items from iterable."""
        return list(iterable)[:count]
    
    # Add utility functions to template globals
    from utils import (
        calculate_reading_time, 
        get_category_color_class, 
        truncate_content_smart, 
        get_card_size_class,
        get_tag_size,
        get_tag_icon,
        get_tag_description
    )
    
    app.jinja_env.globals.update(
        calculate_reading_time=calculate_reading_time,
        get_category_color_class=get_category_color_class,
        truncate_content_smart=truncate_content_smart,
        get_card_size_class=get_card_size_class,
        get_tag_size=get_tag_size,
        get_tag_icon=get_tag_icon,
        get_tag_description=get_tag_description
    )
    
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