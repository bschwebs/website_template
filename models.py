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
    """Initialize the database with tables and default data."""
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
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
        
        db.commit()


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
    def get_posts_by_type(post_type):
        """Get posts filtered by type."""
        db = get_db()
        return db.execute('''
            SELECT * FROM posts 
            WHERE post_type = ?
            ORDER BY created_at DESC
        ''', (post_type,)).fetchall()
    
    @staticmethod
    def get_posts_by_type_paginated(post_type, page=1, per_page=6, category_id=None):
        """Get paginated posts filtered by type and optionally by category."""
        db = get_db()
        offset = (page - 1) * per_page
        
        if category_id and post_type == 'article':
            return db.execute('''
                SELECT p.*, c.name as category_name, c.slug as category_slug
                FROM posts p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.post_type = ? AND p.category_id = ?
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
            ''', (post_type, category_id, per_page, offset)).fetchall()
        else:
            return db.execute('''
                SELECT p.*, c.name as category_name, c.slug as category_slug
                FROM posts p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.post_type = ?
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
            ''', (post_type, per_page, offset)).fetchall()
    
    @staticmethod
    def count_posts_by_type(post_type, category_id=None):
        """Count posts by type and optionally by category."""
        db = get_db()
        if category_id and post_type == 'article':
            return db.execute('SELECT COUNT(*) FROM posts WHERE post_type = ? AND category_id = ?', 
                            (post_type, category_id)).fetchone()[0]
        else:
            return db.execute('SELECT COUNT(*) FROM posts WHERE post_type = ?', (post_type,)).fetchone()[0]
    
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
    def create_post(title, content, excerpt, image_filename, post_type, slug, image_position_x='center', image_position_y='center', category_id=None):
        """Create a new post."""
        db = get_db()
        db.execute('''
            INSERT INTO posts (title, content, excerpt, image_filename, image_position_x, image_position_y, post_type, slug, category_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, content, excerpt, image_filename, image_position_x, image_position_y, post_type, slug, category_id))
        db.commit()
    
    @staticmethod
    def update_post(post_id, title, content, excerpt, image_filename, post_type, slug, image_position_x='center', image_position_y='center', category_id=None):
        """Update an existing post."""
        db = get_db()
        db.execute('''
            UPDATE posts
            SET title = ?, content = ?, excerpt = ?, image_filename = ?, image_position_x = ?, image_position_y = ?, post_type = ?, slug = ?, category_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (title, content, excerpt, image_filename, image_position_x, image_position_y, post_type, slug, category_id, post_id))
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


class CategoryModel:
    """Model for handling category-related database operations."""
    
    @staticmethod
    def get_all_categories():
        """Get all categories."""
        db = get_db()
        return db.execute('''
            SELECT c.*, COUNT(p.id) as post_count
            FROM categories c
            LEFT JOIN posts p ON c.id = p.category_id AND p.post_type = 'article'
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
            'total_stories': len([p for p in posts if p['post_type'] == 'story']),
            'total_articles': len([p for p in posts if p['post_type'] == 'article'])
        }


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
    def delete_message(message_id):
        """Delete a contact message."""
        db = get_db()
        db.execute('DELETE FROM contact_messages WHERE id = ?', (message_id,))
        db.commit()