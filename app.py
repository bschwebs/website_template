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
    
    # Initialize CLI commands
    from cli import init_cli
    init_cli(app)
    
    # Initialize migration manager
    from migrations.migration import migration_manager
    migration_manager.init_app(app)
    
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
    
    # Add analytics tracking middleware
    @app.before_request
    def track_page_views():
        """Track page views for analytics."""
        from flask import request, g
        from models import AnalyticsModel
        import re
        
        # Skip tracking for admin pages, static files, and API endpoints
        if (request.endpoint and 
            (request.endpoint.startswith('admin.') or 
             request.endpoint.startswith('static') or
             request.endpoint.startswith('auth.') or
             request.path.startswith('/admin/') or
             request.path.startswith('/static/') or
             request.path.endswith('.xml') or
             request.path.endswith('.txt') or
             request.path.endswith('.atom') or
             request.path.endswith('.json'))):
            return
        
        # Get request information
        url = request.url
        page_title = None
        user_agent = request.headers.get('User-Agent', '')
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        referrer = request.headers.get('Referer', '')
        post_id = None
        
        # Extract post ID from URL if this is a post view
        if request.endpoint == 'posts.view_post':
            post_id = request.view_args.get('post_id')
        elif request.endpoint == 'posts.view_post_by_slug':
            from models import PostModel
            slug = request.view_args.get('slug')
            if slug:
                post = PostModel.get_post_by_slug(slug)
                if post:
                    post_id = post['id']
                    page_title = post['title']
        
        # Set page title for other pages
        if not page_title:
            if request.endpoint == 'main.index':
                page_title = 'Home'
            elif request.endpoint == 'main.articles':
                page_title = 'Articles'
            elif request.endpoint == 'search.search_posts':
                page_title = 'Search'
            else:
                page_title = request.endpoint or 'Unknown'
        
        # Track the page view
        try:
            AnalyticsModel.track_page_view(
                url=url,
                page_title=page_title,
                user_agent=user_agent,
                ip_address=ip_address,
                referrer=referrer,
                post_id=post_id
            )
        except Exception as e:
            # Don't break the app if analytics fails
            app.logger.error(f"Analytics tracking error: {e}")
    
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
    
    app.run(debug=True, port=5001)