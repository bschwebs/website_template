"""
Database models and functions for the Story Hub application.
"""
import sqlite3
from flask import g, current_app
from werkzeug.security import generate_password_hash


def get_db():
    """Get database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(current_app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db


def close_db(exception):
    """Close database connection."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize the database using the migration system."""
    from migrations.migration import migration_manager
    
    # Apply all pending migrations
    results = migration_manager.migrate_up()
    
    # Create default data if needed
    _create_default_data()
    
    return results


def init_db_old():
    """OLD Initialize the database with tables and default data."""
    with current_app.app_context():
        db = get_db()
        db.executescript('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                excerpt TEXT,
                image_filename TEXT,
                image_position_x TEXT DEFAULT 'center',
                image_position_y TEXT DEFAULT 'center',
                post_type TEXT NOT NULL DEFAULT 'article',
                category_id INTEGER,
                slug TEXT,
                featured BOOLEAN DEFAULT 0,
                status TEXT DEFAULT 'published',
                publish_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                template_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL,
                FOREIGN KEY (template_id) REFERENCES post_templates (id) ON DELETE SET NULL
            );
            
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS post_tags (
                post_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (post_id, tag_id),
                FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS email_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                smtp_server TEXT NOT NULL,
                smtp_port INTEGER NOT NULL DEFAULT 587,
                smtp_username TEXT NOT NULL,
                smtp_password TEXT NOT NULL,
                from_email TEXT NOT NULL,
                to_email TEXT NOT NULL,
                use_tls BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS social_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                icon_class TEXT NOT NULL,
                display_order INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS about_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                bio TEXT,
                image_filename TEXT,
                website_url TEXT,
                github_url TEXT,
                linkedin_url TEXT,
                twitter_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS post_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                content_template TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS image_gallery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                alt_text TEXT,
                caption TEXT,
                file_size INTEGER,
                width INTEGER,
                height INTEGER,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                author TEXT NOT NULL,
                source TEXT,
                language TEXT DEFAULT 'en',
                is_active BOOLEAN DEFAULT 1,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS page_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                page_title TEXT,
                user_agent TEXT,
                ip_address TEXT,
                referrer TEXT,
                post_id INTEGER,
                view_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE SET NULL
            );
            
            CREATE TABLE IF NOT EXISTS daily_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL UNIQUE,
                total_views INTEGER DEFAULT 0,
                unique_visitors INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS post_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                views_count INTEGER DEFAULT 0,
                unique_views INTEGER DEFAULT 0,
                last_viewed TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                UNIQUE(post_id)
            );
        ''')
        
        # Create default admin user if none exists
        admin_exists = db.execute('SELECT COUNT(*) FROM admin_users').fetchone()[0]
        if admin_exists == 0:
            admin_password_hash = generate_password_hash('admin123')
            db.execute('INSERT INTO admin_users (username, password_hash) VALUES (?, ?)', 
                      ('admin', admin_password_hash))
        
        # Migration: Add image position columns if they don't exist
        try:
            db.execute('SELECT image_position_x FROM posts LIMIT 1')
        except sqlite3.OperationalError:
            # Columns don't exist, add them
            db.execute('ALTER TABLE posts ADD COLUMN image_position_x TEXT DEFAULT "center"')
            db.execute('ALTER TABLE posts ADD COLUMN image_position_y TEXT DEFAULT "center"')
        
        # Migration: Add category_id column if it doesn't exist
        try:
            db.execute('SELECT category_id FROM posts LIMIT 1')
        except sqlite3.OperationalError:
            # Column doesn't exist, add it
            db.execute('ALTER TABLE posts ADD COLUMN category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL')
        
        # Migration: Add new post fields if they don't exist
        try:
            db.execute('SELECT status FROM posts LIMIT 1')
        except sqlite3.OperationalError:
            db.execute('ALTER TABLE posts ADD COLUMN status TEXT DEFAULT "published"')
        
        try:
            db.execute('SELECT publish_date FROM posts LIMIT 1')
        except sqlite3.OperationalError:
            db.execute('ALTER TABLE posts ADD COLUMN publish_date TIMESTAMP')
            # Set default value for existing posts
            db.execute('UPDATE posts SET publish_date = created_at WHERE publish_date IS NULL')
        
        try:
            db.execute('SELECT template_id FROM posts LIMIT 1')
        except sqlite3.OperationalError:
            db.execute('ALTER TABLE posts ADD COLUMN template_id INTEGER')
        
        # Migration: Add SEO fields if they don't exist
        try:
            db.execute('SELECT meta_description FROM posts LIMIT 1')
        except sqlite3.OperationalError:
            db.execute('ALTER TABLE posts ADD COLUMN meta_description TEXT')
        
        try:
            db.execute('SELECT meta_keywords FROM posts LIMIT 1')
        except sqlite3.OperationalError:
            db.execute('ALTER TABLE posts ADD COLUMN meta_keywords TEXT')
        
        try:
            db.execute('SELECT canonical_url FROM posts LIMIT 1')
        except sqlite3.OperationalError:
            db.execute('ALTER TABLE posts ADD COLUMN canonical_url TEXT')
        
        # Create default categories for articles
        categories_exist = db.execute('SELECT COUNT(*) FROM categories').fetchone()[0]
        if categories_exist == 0:
            default_categories = [
                ('History', 'history', 'Historical events and periods in Japanese history'),
                ('Culture', 'culture', 'Japanese traditions, customs, and cultural practices'),
                ('Art', 'art', 'Traditional and modern Japanese arts and crafts'),
                ('Religion', 'religion', 'Shintoism, Buddhism, and spiritual practices in Japan'),
                ('Politics', 'politics', 'Government, politics, and political history of Japan'),
                ('Society', 'society', 'Social structures, daily life, and modern Japanese society')
            ]
            for name, slug, description in default_categories:
                db.execute('INSERT INTO categories (name, slug, description) VALUES (?, ?, ?)', 
                          (name, slug, description))
        
        # Create default post templates if none exist
        templates_exist = db.execute('SELECT COUNT(*) FROM post_templates').fetchone()[0]
        if templates_exist == 0:
            default_templates = [
                ('Basic Article', 'Standard article template with introduction, body, and conclusion', 
                 '<h2>Introduction</h2>\n<p>[Write your introduction here]</p>\n\n<h2>Main Content</h2>\n<p>[Write your main content here]</p>\n\n<h2>Conclusion</h2>\n<p>[Write your conclusion here]</p>'),
                ('Historical Timeline', 'Template for historical events with timeline structure',
                 '<h2>Historical Context</h2>\n<p>[Provide background information]</p>\n\n<h2>Timeline of Events</h2>\n<ul>\n<li><strong>[Date]:</strong> [Event description]</li>\n<li><strong>[Date]:</strong> [Event description]</li>\n</ul>\n\n<h2>Significance</h2>\n<p>[Explain the historical significance]</p>'),
                ('Cultural Deep Dive', 'Template for exploring Japanese cultural topics',
                 '<h2>Cultural Overview</h2>\n<p>[Introduction to the cultural topic]</p>\n\n<h2>Historical Origins</h2>\n<p>[Explain the historical background]</p>\n\n<h2>Modern Practice</h2>\n<p>[Describe how it\'s practiced today]</p>\n\n<h2>Cultural Impact</h2>\n<p>[Discuss its significance in Japanese society]</p>'),
                ('Biography', 'Template for writing about historical figures',
                 '<h2>Early Life</h2>\n<p>[Describe their early life and background]</p>\n\n<h2>Rise to Prominence</h2>\n<p>[Explain how they became important]</p>\n\n<h2>Major Achievements</h2>\n<p>[List and describe their key accomplishments]</p>\n\n<h2>Legacy</h2>\n<p>[Discuss their lasting impact]</p>')
            ]
            for name, description, template in default_templates:
                db.execute('INSERT INTO post_templates (name, description, content_template) VALUES (?, ?, ?)', 
                          (name, description, template))
        
        # Create default social links if none exist
        social_links_exist = db.execute('SELECT COUNT(*) FROM social_links').fetchone()[0]
        if social_links_exist == 0:
            default_social_links = [
                ('Twitter', '#', 'fab fa-twitter', 1),
                ('Facebook', '#', 'fab fa-facebook', 2),
                ('Instagram', '#', 'fab fa-instagram', 3),
                ('YouTube', '#', 'fab fa-youtube', 4)
            ]
            for name, url, icon_class, display_order in default_social_links:
                db.execute('INSERT INTO social_links (name, url, icon_class, display_order, is_active) VALUES (?, ?, ?, ?, ?)', 
                          (name, url, icon_class, display_order, 0))  # Start as inactive
        
        # Migration: Add activity_log table if it doesn't exist
        try:
            db.execute('SELECT COUNT(*) FROM activity_log LIMIT 1')
        except sqlite3.OperationalError:
            # Table doesn't exist, create it
            db.execute('''
                CREATE TABLE activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_username TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT,
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        # Create default quotes if none exist
        quotes_exist = db.execute('SELECT COUNT(*) FROM quotes').fetchone()[0]
        if quotes_exist == 0:
            default_quotes = [
                ('The ultimate aim of the ego is not to see something, but to be something.', 'Muhammad Iqbal', 'Islamic philosophy', 'en'),
                ('A journey of a thousand miles begins with a single step.', 'Lao Tzu', 'Tao Te Ching', 'en'),
                ('Fall seven times, stand up eight.', 'Japanese Proverb', 'Traditional Japanese wisdom', 'en'),
                ('The cherry blossoms fall, but the tree remains.', 'Japanese Saying', 'Buddhist philosophy', 'en'),
                ('Even monkeys fall from trees.', 'Japanese Proverb', 'Traditional Japanese wisdom', 'en'),
                ('The nail that sticks out gets hammered down.', 'Japanese Proverb', 'Traditional Japanese wisdom', 'en'),
                ('To know and to act are one and the same.', 'Wang Yangming', 'Confucian philosophy', 'en'),
                ('Be like water making its way through cracks.', 'Bruce Lee', 'Martial arts philosophy', 'en'),
                ('From ancient tombs to modern towers, Japan\'s story is one of resilience, ritual, and rebirth.', 'Japan\'s History Blog', 'Our mission', 'en'),
                ('History is not just what happened, but what we choose to remember and how we choose to tell it.', 'Historical Reflection', 'Modern thought', 'en')
            ]
            for text, author, source, language in default_quotes:
                db.execute('INSERT INTO quotes (text, author, source, language, is_active) VALUES (?, ?, ?, ?, ?)', 
                          (text, author, source, language, 1))
        
        db.commit()


def _create_default_data():
    """Create default data after database initialization."""
    db = get_db()
    
    # Create default admin user if none exists
    admin_exists = db.execute('SELECT COUNT(*) FROM admin_users').fetchone()[0]
    if admin_exists == 0:
        admin_password_hash = generate_password_hash('admin123')
        db.execute('INSERT INTO admin_users (username, password_hash) VALUES (?, ?)', 
                  ('admin', admin_password_hash))
    
    # Create default categories for articles
    categories_exist = db.execute('SELECT COUNT(*) FROM categories').fetchone()[0]
    if categories_exist == 0:
        db.execute('INSERT INTO categories (name, slug, description) VALUES (?, ?, ?)', 
                  ('Introduction', 'introduction', 'Learn more about Japan and this blog'))
    
    db.commit()


def init_db_legacy():
    """Legacy database initialization - kept for compatibility."""
    # This is the old init_db function, renamed for backward compatibility
    # New applications should use the migration system instead
    with current_app.app_context():
        _create_default_data()


class PostModel:
    """Model for handling post-related database operations."""
    
    @staticmethod
    def get_all_posts(limit=None):
        """Get all posts ordered by creation date."""
        db = get_db()
        query = 'SELECT * FROM posts ORDER BY created_at DESC'
        if limit:
            query += f' LIMIT {limit}'
        return db.execute(query).fetchall()
    
    @staticmethod
    def get_all_articles():
        """Get all articles."""
        db = get_db()
        return db.execute('''
            SELECT * FROM posts 
            ORDER BY created_at DESC
        ''').fetchall()
    
    @staticmethod
    def get_articles_paginated(page=1, per_page=6, category_id=None):
        """Get paginated published articles optionally filtered by category."""
        db = get_db()
        offset = (page - 1) * per_page
        
        if category_id:
            return db.execute('''
                SELECT p.*, c.name as category_name, c.slug as category_slug
                FROM posts p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.category_id = ? AND p.status = 'published' 
                AND (p.publish_date IS NULL OR p.publish_date <= CURRENT_TIMESTAMP)
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
            ''', (category_id, per_page, offset)).fetchall()
        else:
            return db.execute('''
                SELECT p.*, c.name as category_name, c.slug as category_slug
                FROM posts p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.status = 'published' 
                AND (p.publish_date IS NULL OR p.publish_date <= CURRENT_TIMESTAMP)
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
            ''', (per_page, offset)).fetchall()
    
    @staticmethod
    def count_articles(category_id=None):
        """Count articles optionally filtered by category."""
        db = get_db()
        if category_id:
            return db.execute('SELECT COUNT(*) FROM posts WHERE category_id = ?', 
                            (category_id,)).fetchone()[0]
        else:
            return db.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    
    @staticmethod
    def get_featured_post():
        """Get the currently featured post."""
        db = get_db()
        return db.execute('''
            SELECT * FROM posts 
            WHERE featured = 1 
            LIMIT 1
        ''').fetchone()
    
    @staticmethod
    def get_introduction_post():
        """Get the introduction post from the introduction category."""
        db = get_db()
        return db.execute('''
            SELECT p.* FROM posts p
            JOIN categories c ON p.category_id = c.id
            WHERE c.slug = 'introduction'
            LIMIT 1
        ''').fetchone()
    
    @staticmethod
    def get_non_featured_posts(limit=9):
        """Get non-featured posts."""
        db = get_db()
        return db.execute('''
            SELECT * FROM posts 
            WHERE featured = 0
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,)).fetchall()
    
    @staticmethod
    def get_post_by_id(post_id):
        """Get a post by its ID."""
        db = get_db()
        return db.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    
    @staticmethod
    def get_post_by_slug(slug):
        """Get a post by its slug."""
        db = get_db()
        return db.execute('SELECT * FROM posts WHERE slug = ?', (slug,)).fetchone()
    
    @staticmethod
    def create_post(title, content, excerpt, image_filename, post_type, slug, image_position_x='center', image_position_y='center', category_id=None, status='published', publish_date=None, template_id=None, meta_description=None, meta_keywords=None, canonical_url=None):
        """Create a new post."""
        db = get_db()
        cursor = db.execute('''
            INSERT INTO posts (title, content, excerpt, image_filename, image_position_x, image_position_y, post_type, slug, category_id, status, publish_date, template_id, meta_description, meta_keywords, canonical_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, content, excerpt, image_filename, image_position_x, image_position_y, post_type, slug, category_id, status, publish_date, template_id, meta_description, meta_keywords, canonical_url))
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def update_post(post_id, title, content, excerpt, image_filename, post_type, slug, image_position_x='center', image_position_y='center', category_id=None, status='published', publish_date=None, template_id=None, meta_description=None, meta_keywords=None, canonical_url=None):
        """Update an existing post."""
        db = get_db()
        db.execute('''
            UPDATE posts
            SET title = ?, content = ?, excerpt = ?, image_filename = ?, image_position_x = ?, image_position_y = ?, post_type = ?, slug = ?, category_id = ?, status = ?, publish_date = ?, template_id = ?, meta_description = ?, meta_keywords = ?, canonical_url = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (title, content, excerpt, image_filename, image_position_x, image_position_y, post_type, slug, category_id, status, publish_date, template_id, meta_description, meta_keywords, canonical_url, post_id))
        db.commit()
    
    @staticmethod
    def delete_post(post_id):
        """Delete a post."""
        db = get_db()
        db.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        db.commit()
    
    @staticmethod
    def feature_post(post_id):
        """Feature a post (unfeature all others first)."""
        db = get_db()
        # Unfeature all other posts first
        db.execute('UPDATE posts SET featured = 0')
        # Feature this post
        db.execute('UPDATE posts SET featured = 1 WHERE id = ?', (post_id,))
        db.commit()
    
    @staticmethod
    def unfeature_post(post_id):
        """Unfeature a post."""
        db = get_db()
        db.execute('UPDATE posts SET featured = 0 WHERE id = ?', (post_id,))
        db.commit()
    
    @staticmethod
    def slug_exists(slug, exclude_id=None):
        """Check if a slug already exists."""
        db = get_db()
        if exclude_id:
            result = db.execute('SELECT id FROM posts WHERE slug = ? AND id != ?', (slug, exclude_id)).fetchone()
        else:
            result = db.execute('SELECT id FROM posts WHERE slug = ?', (slug,)).fetchone()
        return result is not None
    
    @staticmethod
    def count_all_posts():
        """Count total number of posts."""
        db = get_db()
        return db.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    
    @staticmethod
    def count_non_featured_posts():
        """Count total number of non-featured posts."""
        db = get_db()
        return db.execute('SELECT COUNT(*) FROM posts WHERE featured = 0').fetchone()[0]
    
    @staticmethod
    def get_all_posts_paginated(page, per_page):
        """Get paginated posts."""
        db = get_db()
        offset = (page - 1) * per_page
        return db.execute('''
            SELECT * FROM posts 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (per_page, offset)).fetchall()
    
    @staticmethod
    def get_non_featured_posts_paginated(page, per_page):
        """Get paginated non-featured posts."""
        db = get_db()
        offset = (page - 1) * per_page
        return db.execute('''
            SELECT * FROM posts 
            WHERE featured = 0
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (per_page, offset)).fetchall()
    
    @staticmethod
    def search_posts(query, page=1, per_page=10):
        """Search posts by title, content, or excerpt."""
        db = get_db()
        offset = (page - 1) * per_page
        search_term = f'%{query}%'
        
        return db.execute('''
            SELECT DISTINCT p.*, GROUP_CONCAT(t.name, ', ') as tag_names
            FROM posts p
            LEFT JOIN post_tags pt ON p.id = pt.post_id
            LEFT JOIN tags t ON pt.tag_id = t.id
            WHERE p.title LIKE ? OR p.content LIKE ? OR p.excerpt LIKE ?
            GROUP BY p.id
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        ''', (search_term, search_term, search_term, per_page, offset)).fetchall()
    
    @staticmethod
    def count_search_results(query):
        """Count search results."""
        db = get_db()
        search_term = f'%{query}%'
        return db.execute('''
            SELECT COUNT(DISTINCT p.id) FROM posts p
            WHERE p.title LIKE ? OR p.content LIKE ? OR p.excerpt LIKE ?
        ''', (search_term, search_term, search_term)).fetchone()[0]
    
    @staticmethod
    def get_posts_by_tag(tag_slug, page=1, per_page=10):
        """Get posts filtered by tag."""
        db = get_db()
        offset = (page - 1) * per_page
        
        return db.execute('''
            SELECT DISTINCT p.*, GROUP_CONCAT(t.name, ', ') as tag_names
            FROM posts p
            JOIN post_tags pt ON p.id = pt.post_id
            JOIN tags t ON pt.tag_id = t.id
            JOIN tags filter_tag ON pt.tag_id = filter_tag.id
            LEFT JOIN post_tags pt2 ON p.id = pt2.post_id
            LEFT JOIN tags t2 ON pt2.tag_id = t2.id
            WHERE filter_tag.slug = ?
            GROUP BY p.id
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        ''', (tag_slug, per_page, offset)).fetchall()
    
    @staticmethod
    def count_posts_by_tag(tag_slug):
        """Count posts by tag."""
        db = get_db()
        return db.execute('''
            SELECT COUNT(DISTINCT p.id) FROM posts p
            JOIN post_tags pt ON p.id = pt.post_id
            JOIN tags t ON pt.tag_id = t.id
            WHERE t.slug = ?
        ''', (tag_slug,)).fetchone()[0]
    
    @staticmethod
    def get_post_tags(post_id):
        """Get tags for a specific post."""
        db = get_db()
        return db.execute('''
            SELECT t.* FROM tags t
            JOIN post_tags pt ON t.id = pt.tag_id
            WHERE pt.post_id = ?
            ORDER BY t.name
        ''', (post_id,)).fetchall()
    
    @staticmethod
    def add_tags_to_post(post_id, tag_names):
        """Add tags to a post."""
        if not tag_names:
            return
            
        db = get_db()
        # First, remove existing tags for this post
        db.execute('DELETE FROM post_tags WHERE post_id = ?', (post_id,))
        
        # Process each tag
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if not tag_name:
                continue
                
            # Create tag if it doesn't exist
            from utils import generate_tag_slug
            tag_slug = generate_tag_slug(tag_name)
            
            # Insert or get tag
            db.execute('''
                INSERT OR IGNORE INTO tags (name, slug) VALUES (?, ?)
            ''', (tag_name, tag_slug))
            
            # Get tag ID
            tag = db.execute('SELECT id FROM tags WHERE slug = ?', (tag_slug,)).fetchone()
            
            # Link post to tag
            db.execute('''
                INSERT OR IGNORE INTO post_tags (post_id, tag_id) VALUES (?, ?)
            ''', (post_id, tag['id']))
        
        db.commit()
    
    @staticmethod
    def get_search_suggestions(query, limit=5):
        """Get search suggestions from post titles."""
        db = get_db()
        search_term = f'%{query}%'
        
        return db.execute('''
            SELECT p.*, c.name as category_name
            FROM posts p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.title LIKE ? AND p.status = 'published'
            ORDER BY p.created_at DESC
            LIMIT ?
        ''', (search_term, limit)).fetchall()
    
    @staticmethod
    def advanced_search(query, page=1, per_page=10, category_filter='', tag_filter='', date_from='', date_to='', sort_by='relevance'):
        """Advanced search with filters and sorting."""
        db = get_db()
        offset = (page - 1) * per_page
        search_term = f'%{query}%'
        
        # Build the query dynamically based on filters
        base_query = '''
            SELECT DISTINCT p.*, c.name as category_name, c.slug as category_slug, 
                   GROUP_CONCAT(t.name, ', ') as tag_names
            FROM posts p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN post_tags pt ON p.id = pt.post_id
            LEFT JOIN tags t ON pt.tag_id = t.id
            WHERE p.status = 'published' 
            AND (p.title LIKE ? OR p.content LIKE ? OR p.excerpt LIKE ?)
        '''
        
        params = [search_term, search_term, search_term]
        
        # Add category filter
        if category_filter:
            base_query += ' AND c.slug = ?'
            params.append(category_filter)
        
        # Add tag filter
        if tag_filter:
            base_query += '''
                AND p.id IN (
                    SELECT DISTINCT pt2.post_id 
                    FROM post_tags pt2 
                    JOIN tags t2 ON pt2.tag_id = t2.id 
                    WHERE t2.slug = ?
                )
            '''
            params.append(tag_filter)
        
        # Add date filters
        if date_from:
            base_query += ' AND DATE(p.created_at) >= ?'
            params.append(date_from)
        
        if date_to:
            base_query += ' AND DATE(p.created_at) <= ?'
            params.append(date_to)
        
        # Group by post
        base_query += ' GROUP BY p.id'
        
        # Add sorting
        if sort_by == 'date_desc':
            base_query += ' ORDER BY p.created_at DESC'
        elif sort_by == 'date_asc':
            base_query += ' ORDER BY p.created_at ASC'
        elif sort_by == 'title':
            base_query += ' ORDER BY p.title ASC'
        else:  # relevance (default)
            base_query += ' ORDER BY p.created_at DESC'
        
        # Add pagination
        base_query += ' LIMIT ? OFFSET ?'
        params.extend([per_page, offset])
        
        return db.execute(base_query, params).fetchall()
    
    @staticmethod
    def count_advanced_search(query, category_filter='', tag_filter='', date_from='', date_to=''):
        """Count results for advanced search."""
        db = get_db()
        search_term = f'%{query}%'
        
        # Build the count query
        count_query = '''
            SELECT COUNT(DISTINCT p.id) 
            FROM posts p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN post_tags pt ON p.id = pt.post_id
            LEFT JOIN tags t ON pt.tag_id = t.id
            WHERE p.status = 'published' 
            AND (p.title LIKE ? OR p.content LIKE ? OR p.excerpt LIKE ?)
        '''
        
        params = [search_term, search_term, search_term]
        
        # Add category filter
        if category_filter:
            count_query += ' AND c.slug = ?'
            params.append(category_filter)
        
        # Add tag filter
        if tag_filter:
            count_query += '''
                AND p.id IN (
                    SELECT DISTINCT pt2.post_id 
                    FROM post_tags pt2 
                    JOIN tags t2 ON pt2.tag_id = t2.id 
                    WHERE t2.slug = ?
                )
            '''
            params.append(tag_filter)
        
        # Add date filters
        if date_from:
            count_query += ' AND DATE(p.created_at) >= ?'
            params.append(date_from)
        
        if date_to:
            count_query += ' AND DATE(p.created_at) <= ?'
            params.append(date_to)
        
        return db.execute(count_query, params).fetchone()[0]
    
    @staticmethod
    def get_related_posts(post_id, limit=4):
        """Get related posts based on shared tags and category."""
        db = get_db()
        
        # First get the current post's category and tags
        current_post = db.execute('SELECT category_id, post_type FROM posts WHERE id = ?', (post_id,)).fetchone()
        if not current_post:
            return []
        
        # Get related posts using a weighted scoring system
        query = '''
            SELECT DISTINCT p.*, c.name as category_name, c.slug as category_slug,
                   -- Scoring system: category match = 10 points, each shared tag = 3 points
                   (CASE WHEN p.category_id = ? THEN 10 ELSE 0 END) +
                   (SELECT COUNT(*) * 3 FROM post_tags pt1 
                    JOIN post_tags pt2 ON pt1.tag_id = pt2.tag_id 
                    WHERE pt1.post_id = ? AND pt2.post_id = p.id) as relevance_score
            FROM posts p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.id != ? 
            AND p.status = 'published'
            AND p.post_type = ?
            AND (p.publish_date IS NULL OR p.publish_date <= CURRENT_TIMESTAMP)
            AND (
                p.category_id = ? OR
                p.id IN (
                    SELECT pt2.post_id FROM post_tags pt1
                    JOIN post_tags pt2 ON pt1.tag_id = pt2.tag_id
                    WHERE pt1.post_id = ? AND pt2.post_id != ?
                )
            )
            ORDER BY relevance_score DESC, p.created_at DESC
            LIMIT ?
        '''
        
        return db.execute(query, (
            current_post['category_id'],  # For scoring
            post_id,                      # For tag matching in scoring
            post_id,                      # Exclude current post
            current_post['post_type'],    # Same post type
            current_post['category_id'],  # Category match condition
            post_id,                      # Tag matching condition
            post_id,                      # Exclude from tag matching
            limit
        )).fetchall()


class TagModel:
    """Model for handling tag-related database operations."""
    
    @staticmethod
    def get_all_tags():
        """Get all tags."""
        db = get_db()
        return db.execute('''
            SELECT t.*, COUNT(pt.post_id) as post_count
            FROM tags t
            LEFT JOIN post_tags pt ON t.id = pt.tag_id
            GROUP BY t.id
            ORDER BY t.name
        ''').fetchall()
    
    @staticmethod
    def get_popular_tags(limit=10):
        """Get most popular tags by post count."""
        db = get_db()
        return db.execute('''
            SELECT t.*, COUNT(pt.post_id) as post_count
            FROM tags t
            JOIN post_tags pt ON t.id = pt.tag_id
            GROUP BY t.id
            ORDER BY post_count DESC, t.name
            LIMIT ?
        ''', (limit,)).fetchall()
    
    @staticmethod
    def get_tag_by_slug(slug):
        """Get tag by slug."""
        db = get_db()
        return db.execute('SELECT * FROM tags WHERE slug = ?', (slug,)).fetchone()
    
    @staticmethod
    def get_tag_by_id(tag_id):
        """Get tag by ID."""
        db = get_db()
        return db.execute('SELECT * FROM tags WHERE id = ?', (tag_id,)).fetchone()
    
    @staticmethod
    def delete_tag(tag_id):
        """Delete a tag and its associations."""
        db = get_db()
        db.execute('DELETE FROM post_tags WHERE tag_id = ?', (tag_id,))
        db.execute('DELETE FROM tags WHERE id = ?', (tag_id,))
        db.commit()
    
    @staticmethod
    def get_tag_suggestions(query, limit=3):
        """Get tag suggestions for search."""
        db = get_db()
        search_term = f'%{query}%'
        
        return db.execute('''
            SELECT t.*, COUNT(pt.post_id) as post_count
            FROM tags t
            LEFT JOIN post_tags pt ON t.id = pt.tag_id
            WHERE t.name LIKE ?
            GROUP BY t.id
            ORDER BY post_count DESC, t.name
            LIMIT ?
        ''', (search_term, limit)).fetchall()
    
    @staticmethod
    def get_tags_with_posts(limit=20):
        """Get only tags that have at least one published post."""
        db = get_db()
        return db.execute('''
            SELECT t.*, COUNT(pt.post_id) as post_count
            FROM tags t
            INNER JOIN post_tags pt ON t.id = pt.tag_id
            INNER JOIN posts p ON pt.post_id = p.id
            WHERE p.status = 'published'
            GROUP BY t.id
            HAVING COUNT(pt.post_id) > 0
            ORDER BY post_count DESC, t.name
            LIMIT ?
        ''', (limit,)).fetchall()


class CategoryModel:
    """Model for handling category-related database operations."""
    
    @staticmethod
    def get_all_categories():
        """Get all categories."""
        db = get_db()
        return db.execute('''
            SELECT c.*, COUNT(p.id) as post_count
            FROM categories c
            LEFT JOIN posts p ON c.id = p.category_id
            GROUP BY c.id
            ORDER BY c.name
        ''').fetchall()
    
    @staticmethod
    def get_category_by_slug(slug):
        """Get category by slug."""
        db = get_db()
        return db.execute('SELECT * FROM categories WHERE slug = ?', (slug,)).fetchone()
    
    @staticmethod
    def get_category_by_id(category_id):
        """Get category by ID."""
        db = get_db()
        return db.execute('SELECT * FROM categories WHERE id = ?', (category_id,)).fetchone()
    
    @staticmethod
    def create_category(name, slug, description=None):
        """Create a new category."""
        db = get_db()
        db.execute('''
            INSERT INTO categories (name, slug, description)
            VALUES (?, ?, ?)
        ''', (name, slug, description))
        db.commit()
    
    @staticmethod
    def update_category(category_id, name, slug, description=None):
        """Update an existing category."""
        db = get_db()
        db.execute('''
            UPDATE categories
            SET name = ?, slug = ?, description = ?
            WHERE id = ?
        ''', (name, slug, description, category_id))
        db.commit()
    
    @staticmethod
    def delete_category(category_id):
        """Delete a category and unlink posts."""
        db = get_db()
        # First, unlink posts from this category
        db.execute('UPDATE posts SET category_id = NULL WHERE category_id = ?', (category_id,))
        # Then delete the category
        db.execute('DELETE FROM categories WHERE id = ?', (category_id,))
        db.commit()
    
    @staticmethod
    def slug_exists(slug, exclude_id=None):
        """Check if a category slug already exists."""
        db = get_db()
        if exclude_id:
            result = db.execute('SELECT id FROM categories WHERE slug = ? AND id != ?', (slug, exclude_id)).fetchone()
        else:
            result = db.execute('SELECT id FROM categories WHERE slug = ?', (slug,)).fetchone()
        return result is not None
    
    @staticmethod
    def get_categories_with_posts():
        """Get only categories that have at least one published post."""
        db = get_db()
        return db.execute('''
            SELECT c.*, COUNT(p.id) as post_count
            FROM categories c
            INNER JOIN posts p ON c.id = p.category_id 
            WHERE p.status = 'published'
            GROUP BY c.id
            HAVING COUNT(p.id) > 0
            ORDER BY c.name
        ''').fetchall()


class SocialLinksModel:
    """Model for handling social media links."""
    
    @staticmethod
    def get_all_social_links():
        """Get all social links ordered by display order."""
        db = get_db()
        return db.execute('''
            SELECT * FROM social_links 
            ORDER BY display_order ASC, name ASC
        ''').fetchall()
    
    @staticmethod
    def get_active_social_links():
        """Get only active social links ordered by display order."""
        db = get_db()
        return db.execute('''
            SELECT * FROM social_links 
            WHERE is_active = 1 
            ORDER BY display_order ASC, name ASC
        ''').fetchall()
    
    @staticmethod
    def get_social_link_by_id(link_id):
        """Get a social link by its ID."""
        db = get_db()
        return db.execute('SELECT * FROM social_links WHERE id = ?', (link_id,)).fetchone()
    
    @staticmethod
    def create_social_link(name, url, icon_class, display_order=0, is_active=True):
        """Create a new social link."""
        db = get_db()
        cursor = db.execute('''
            INSERT INTO social_links (name, url, icon_class, display_order, is_active) 
            VALUES (?, ?, ?, ?, ?)
        ''', (name, url, icon_class, display_order, is_active))
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def update_social_link(link_id, name, url, icon_class, display_order=0, is_active=True):
        """Update an existing social link."""
        db = get_db()
        db.execute('''
            UPDATE social_links 
            SET name = ?, url = ?, icon_class = ?, display_order = ?, is_active = ?, 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (name, url, icon_class, display_order, is_active, link_id))
        db.commit()
    
    @staticmethod
    def delete_social_link(link_id):
        """Delete a social link."""
        db = get_db()
        db.execute('DELETE FROM social_links WHERE id = ?', (link_id,))
        db.commit()
    
    @staticmethod
    def reorder_social_links(link_orders):
        """Update display order for multiple social links."""
        db = get_db()
        for link_id, display_order in link_orders.items():
            db.execute('''
                UPDATE social_links 
                SET display_order = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (display_order, link_id))
        db.commit()


class AdminModel:
    """Model for handling admin-related database operations."""
    
    @staticmethod
    def get_admin_by_username(username):
        """Get admin user by username."""
        db = get_db()
        return db.execute('SELECT * FROM admin_users WHERE username = ?', (username,)).fetchone()
    
    @staticmethod
    def get_post_statistics():
        """Get post statistics for the admin dashboard."""
        db = get_db()
        posts = PostModel.get_all_posts()
        return {
            'total_posts': len(posts),
            'total_articles': len(posts)
        }
    
    @staticmethod
    def verify_password(username, password):
        """Verify admin password."""
        from werkzeug.security import check_password_hash
        db = get_db()
        admin = db.execute('SELECT * FROM admin_users WHERE username = ?', (username,)).fetchone()
        if admin:
            return check_password_hash(admin['password_hash'], password)
        return False
    
    @staticmethod
    def update_password(username, new_password):
        """Update admin password."""
        from werkzeug.security import generate_password_hash
        db = get_db()
        
        # Hash the new password using Werkzeug's secure hashing
        password_hash = generate_password_hash(new_password)
        
        # Update the password
        db.execute('UPDATE admin_users SET password_hash = ? WHERE username = ?', 
                  (password_hash, username))
        db.commit()


class EmailConfigModel:
    """Model for handling email configuration."""
    
    @staticmethod
    def get_config():
        """Get email configuration."""
        db = get_db()
        return db.execute('SELECT * FROM email_config ORDER BY id DESC LIMIT 1').fetchone()
    
    @staticmethod
    def save_config(smtp_server, smtp_port, smtp_username, smtp_password, from_email, to_email, use_tls=True):
        """Save email configuration."""
        db = get_db()
        # Delete existing config first
        db.execute('DELETE FROM email_config')
        # Insert new config
        db.execute('''
            INSERT INTO email_config (smtp_server, smtp_port, smtp_username, smtp_password, from_email, to_email, use_tls)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (smtp_server, smtp_port, smtp_username, smtp_password, from_email, to_email, use_tls))
        db.commit()


class ContactModel:
    """Model for handling contact messages."""
    
    @staticmethod
    def save_message(name, email, subject, message):
        """Save a contact message."""
        db = get_db()
        db.execute('''
            INSERT INTO contact_messages (name, email, subject, message)
            VALUES (?, ?, ?, ?)
        ''', (name, email, subject, message))
        db.commit()
    
    @staticmethod
    def get_all_messages():
        """Get all contact messages."""
        db = get_db()
        return db.execute('SELECT * FROM contact_messages ORDER BY created_at DESC').fetchall()
    
    @staticmethod
    def get_recent_messages(limit=5):
        """Get recent contact messages for dashboard."""
        db = get_db()
        return db.execute('SELECT * FROM contact_messages ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
    
    @staticmethod
    def delete_message(message_id):
        """Delete a contact message."""
        db = get_db()
        db.execute('DELETE FROM contact_messages WHERE id = ?', (message_id,))
        db.commit()


class AboutModel:
    """Model for handling about page information."""
    
    @staticmethod
    def get_about_info():
        """Get about information."""
        db = get_db()
        return db.execute('SELECT * FROM about_info ORDER BY id DESC LIMIT 1').fetchone()
    
    @staticmethod
    def save_about_info(name, email, bio, image_filename, website_url, github_url, linkedin_url, twitter_url):
        """Save or update about information."""
        db = get_db()
        # Delete existing info first (only one record allowed)
        db.execute('DELETE FROM about_info')
        # Insert new info
        db.execute('''
            INSERT INTO about_info (name, email, bio, image_filename, website_url, github_url, linkedin_url, twitter_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, bio, image_filename, website_url, github_url, linkedin_url, twitter_url))
        db.commit()
    
    @staticmethod
    def update_about_info(name, email, bio, image_filename, website_url, github_url, linkedin_url, twitter_url):
        """Update existing about information."""
        db = get_db()
        existing = db.execute('SELECT * FROM about_info LIMIT 1').fetchone()
        
        if existing:
            db.execute('''
                UPDATE about_info 
                SET name = ?, email = ?, bio = ?, image_filename = ?, 
                    website_url = ?, github_url = ?, linkedin_url = ?, twitter_url = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (name, email, bio, image_filename, website_url, github_url, linkedin_url, twitter_url, existing['id']))
        else:
            db.execute('''
                INSERT INTO about_info (name, email, bio, image_filename, website_url, github_url, linkedin_url, twitter_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, email, bio, image_filename, website_url, github_url, linkedin_url, twitter_url))
        
        db.commit()


class PostTemplateModel:
    """Model for handling post template operations."""
    
    @staticmethod
    def get_all_templates():
        """Get all post templates."""
        db = get_db()
        return db.execute('SELECT * FROM post_templates ORDER BY name').fetchall()
    
    @staticmethod
    def get_template_by_id(template_id):
        """Get template by ID."""
        db = get_db()
        return db.execute('SELECT * FROM post_templates WHERE id = ?', (template_id,)).fetchone()
    
    @staticmethod
    def create_template(name, description, content_template):
        """Create a new post template."""
        db = get_db()
        cursor = db.execute('''
            INSERT INTO post_templates (name, description, content_template)
            VALUES (?, ?, ?)
        ''', (name, description, content_template))
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def update_template(template_id, name, description, content_template):
        """Update an existing post template."""
        db = get_db()
        db.execute('''
            UPDATE post_templates
            SET name = ?, description = ?, content_template = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (name, description, content_template, template_id))
        db.commit()
    
    @staticmethod
    def delete_template(template_id):
        """Delete a post template."""
        db = get_db()
        # First, unlink posts from this template
        db.execute('UPDATE posts SET template_id = NULL WHERE template_id = ?', (template_id,))
        # Then delete the template
        db.execute('DELETE FROM post_templates WHERE id = ?', (template_id,))
        db.commit()


class ImageGalleryModel:
    """Model for handling image gallery operations."""
    
    @staticmethod
    def get_all_images(page=1, per_page=20):
        """Get paginated images from gallery."""
        db = get_db()
        offset = (page - 1) * per_page
        return db.execute('''
            SELECT * FROM image_gallery 
            ORDER BY uploaded_at DESC 
            LIMIT ? OFFSET ?
        ''', (per_page, offset)).fetchall()
    
    @staticmethod
    def count_images():
        """Count total images in gallery."""
        db = get_db()
        return db.execute('SELECT COUNT(*) FROM image_gallery').fetchone()[0]
    
    @staticmethod
    def get_image_by_id(image_id):
        """Get image by ID."""
        db = get_db()
        return db.execute('SELECT * FROM image_gallery WHERE id = ?', (image_id,)).fetchone()
    
    @staticmethod
    def add_image(filename, original_filename, alt_text=None, caption=None, file_size=None, width=None, height=None):
        """Add an image to the gallery."""
        db = get_db()
        cursor = db.execute('''
            INSERT INTO image_gallery (filename, original_filename, alt_text, caption, file_size, width, height)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (filename, original_filename, alt_text, caption, file_size, width, height))
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def update_image(image_id, alt_text=None, caption=None):
        """Update image metadata."""
        db = get_db()
        db.execute('''
            UPDATE image_gallery
            SET alt_text = ?, caption = ?
            WHERE id = ?
        ''', (alt_text, caption, image_id))
        db.commit()
    
    @staticmethod
    def delete_image(image_id):
        """Delete an image from gallery."""
        db = get_db()
        db.execute('DELETE FROM image_gallery WHERE id = ?', (image_id,))
        db.commit()
    
    @staticmethod
    def search_images(query, page=1, per_page=20):
        """Search images by filename, alt text, or caption."""
        db = get_db()
        offset = (page - 1) * per_page
        search_term = f'%{query}%'
        return db.execute('''
            SELECT * FROM image_gallery
            WHERE filename LIKE ? OR alt_text LIKE ? OR caption LIKE ?
            ORDER BY uploaded_at DESC
            LIMIT ? OFFSET ?
        ''', (search_term, search_term, search_term, per_page, offset)).fetchall()


class ActivityLogModel:
    """Model for tracking admin activities."""
    
    @staticmethod
    def log_activity(admin_username, action, details=None, ip_address=None):
        """Log an admin activity."""
        from datetime import datetime
        db = get_db()
        db.execute('''
            INSERT INTO activity_log (admin_username, action, details, ip_address, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (admin_username, action, details, ip_address, datetime.now()))
        db.commit()
    
    @staticmethod
    def get_recent_activities(limit=50):
        """Get recent admin activities."""
        db = get_db()
        return db.execute('''
            SELECT * FROM activity_log
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,)).fetchall()
    
    @staticmethod
    def get_activities_paginated(page=1, per_page=20):
        """Get paginated admin activities."""
        db = get_db()
        offset = (page - 1) * per_page
        return db.execute('''
            SELECT * FROM activity_log
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        ''', (per_page, offset)).fetchall()
    
    @staticmethod
    def count_activities():
        """Count total number of activity log entries."""
        db = get_db()
        return db.execute('SELECT COUNT(*) FROM activity_log').fetchone()[0]
    
    @staticmethod
    def get_activities_by_admin(admin_username, limit=50):
        """Get activities for a specific admin user."""
        db = get_db()
        return db.execute('''
            SELECT * FROM activity_log
            WHERE admin_username = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (admin_username, limit)).fetchall()
    
    @staticmethod
    def delete_old_activities(days_to_keep=30):
        """Delete activity log entries older than specified days."""
        from datetime import datetime, timedelta
        db = get_db()
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        db.execute('''
            DELETE FROM activity_log
            WHERE timestamp < ?
        ''', (cutoff_date,))
        db.commit()
    
    @staticmethod
    def search_activities(query, page=1, per_page=20):
        """Search activities by action or details."""
        db = get_db()
        offset = (page - 1) * per_page
        search_term = f'%{query}%'
        return db.execute('''
            SELECT * FROM activity_log
            WHERE action LIKE ? OR details LIKE ? OR admin_username LIKE ?
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        ''', (search_term, search_term, search_term, per_page, offset)).fetchall()


class QuoteModel:
    """Model for handling quote operations."""
    
    @staticmethod
    def get_all_quotes():
        """Get all quotes ordered by display order."""
        db = get_db()
        return db.execute('''
            SELECT * FROM quotes 
            ORDER BY display_order ASC, created_at DESC
        ''').fetchall()
    
    @staticmethod
    def get_active_quotes():
        """Get only active quotes."""
        db = get_db()
        return db.execute('''
            SELECT * FROM quotes 
            WHERE is_active = 1 
            ORDER BY display_order ASC, created_at DESC
        ''').fetchall()
    
    @staticmethod
    def get_random_quote():
        """Get a random active quote."""
        db = get_db()
        return db.execute('''
            SELECT * FROM quotes 
            WHERE is_active = 1 
            ORDER BY RANDOM() 
            LIMIT 1
        ''').fetchone()
    
    @staticmethod
    def get_quote_by_id(quote_id):
        """Get quote by ID."""
        db = get_db()
        return db.execute('SELECT * FROM quotes WHERE id = ?', (quote_id,)).fetchone()
    
    @staticmethod
    def create_quote(text, author, source=None, language='en', is_active=True, display_order=0):
        """Create a new quote."""
        db = get_db()
        cursor = db.execute('''
            INSERT INTO quotes (text, author, source, language, is_active, display_order)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (text, author, source, language, is_active, display_order))
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def update_quote(quote_id, text, author, source=None, language='en', is_active=True, display_order=0):
        """Update an existing quote."""
        db = get_db()
        db.execute('''
            UPDATE quotes
            SET text = ?, author = ?, source = ?, language = ?, is_active = ?, display_order = ?, 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (text, author, source, language, is_active, display_order, quote_id))
        db.commit()
    
    @staticmethod
    def delete_quote(quote_id):
        """Delete a quote."""
        db = get_db()
        db.execute('DELETE FROM quotes WHERE id = ?', (quote_id,))
        db.commit()
    
    @staticmethod
    def toggle_active(quote_id):
        """Toggle active status of a quote."""
        db = get_db()
        db.execute('''
            UPDATE quotes 
            SET is_active = NOT is_active, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (quote_id,))
        db.commit()
    
    @staticmethod
    def reorder_quotes(quote_orders):
        """Update display order for multiple quotes."""
        db = get_db()
        for quote_id, display_order in quote_orders.items():
            db.execute('''
                UPDATE quotes 
                SET display_order = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (display_order, quote_id))
        db.commit()
    
    @staticmethod
    def count_quotes():
        """Count total number of quotes."""
        db = get_db()
        return db.execute('SELECT COUNT(*) FROM quotes').fetchone()[0]
    
    @staticmethod
    def count_active_quotes():
        """Count active quotes."""
        db = get_db()
        return db.execute('SELECT COUNT(*) FROM quotes WHERE is_active = 1').fetchone()[0]


class AnalyticsModel:
    """Model for handling analytics and page view tracking."""
    
    @staticmethod
    def track_page_view(url, page_title=None, user_agent=None, ip_address=None, referrer=None, post_id=None):
        """Track a page view."""
        from datetime import date
        db = get_db()
        view_date = date.today()
        
        # Record the page view
        db.execute('''
            INSERT INTO page_views (url, page_title, user_agent, ip_address, referrer, post_id, view_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (url, page_title, user_agent, ip_address, referrer, post_id, view_date))
        
        # Update daily analytics
        db.execute('''
            INSERT OR REPLACE INTO daily_analytics (date, total_views, unique_visitors)
            VALUES (?, 
                COALESCE((SELECT total_views FROM daily_analytics WHERE date = ?), 0) + 1,
                (SELECT COUNT(DISTINCT ip_address) FROM page_views WHERE view_date = ?)
            )
        ''', (view_date, view_date, view_date))
        
        # Update post analytics if this is a post view
        if post_id:
            db.execute('''
                INSERT OR REPLACE INTO post_analytics (post_id, views_count, unique_views, last_viewed)
                VALUES (?, 
                    COALESCE((SELECT views_count FROM post_analytics WHERE post_id = ?), 0) + 1,
                    (SELECT COUNT(DISTINCT ip_address) FROM page_views WHERE post_id = ?),
                    CURRENT_TIMESTAMP
                )
            ''', (post_id, post_id, post_id))
        
        db.commit()
    
    @staticmethod
    def get_daily_stats(days=30):
        """Get daily analytics for the last N days."""
        db = get_db()
        return db.execute('''
            SELECT date, total_views, unique_visitors
            FROM daily_analytics
            ORDER BY date DESC
            LIMIT ?
        ''', (days,)).fetchall()
    
    @staticmethod
    def get_total_views():
        """Get total page views."""
        db = get_db()
        result = db.execute('SELECT COUNT(*) FROM page_views').fetchone()
        return result[0] if result else 0
    
    @staticmethod
    def get_unique_visitors():
        """Get unique visitors count."""
        db = get_db()
        result = db.execute('SELECT COUNT(DISTINCT ip_address) FROM page_views').fetchone()
        return result[0] if result else 0
    
    @staticmethod
    def get_popular_posts(limit=10):
        """Get most popular posts by view count."""
        db = get_db()
        return db.execute('''
            SELECT p.*, pa.views_count, pa.unique_views, pa.last_viewed
            FROM posts p
            JOIN post_analytics pa ON p.id = pa.post_id
            ORDER BY pa.views_count DESC
            LIMIT ?
        ''', (limit,)).fetchall()
    
    @staticmethod
    def get_recent_referrers(limit=10):
        """Get recent referrer URLs."""
        db = get_db()
        return db.execute('''
            SELECT referrer, COUNT(*) as count, MAX(created_at) as last_visit
            FROM page_views
            WHERE referrer IS NOT NULL AND referrer != ''
            GROUP BY referrer
            ORDER BY count DESC, last_visit DESC
            LIMIT ?
        ''', (limit,)).fetchall()
    
    @staticmethod
    def get_popular_pages(limit=10):
        """Get most popular pages by view count."""
        db = get_db()
        return db.execute('''
            SELECT url, page_title, COUNT(*) as views, COUNT(DISTINCT ip_address) as unique_views
            FROM page_views
            GROUP BY url
            ORDER BY views DESC
            LIMIT ?
        ''', (limit,)).fetchall()
    
    @staticmethod
    def get_post_analytics(post_id):
        """Get analytics for a specific post."""
        db = get_db()
        return db.execute('''
            SELECT * FROM post_analytics WHERE post_id = ?
        ''', (post_id,)).fetchone()
    
    @staticmethod
    def get_analytics_summary():
        """Get a summary of analytics data."""
        db = get_db()
        
        # Get today's stats
        from datetime import date
        today = date.today()
        today_stats = db.execute('''
            SELECT total_views, unique_visitors
            FROM daily_analytics
            WHERE date = ?
        ''', (today,)).fetchone()
        
        # Get total stats
        total_views = AnalyticsModel.get_total_views()
        unique_visitors = AnalyticsModel.get_unique_visitors()
        
        # Get post count with views
        posts_with_views = db.execute('''
            SELECT COUNT(*) FROM post_analytics WHERE views_count > 0
        ''').fetchone()[0]
        
        return {
            'total_views': total_views,
            'unique_visitors': unique_visitors,
            'today_views': today_stats['total_views'] if today_stats else 0,
            'today_unique': today_stats['unique_visitors'] if today_stats else 0,
            'posts_with_views': posts_with_views
        }