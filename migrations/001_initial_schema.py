"""
Migration: Initial Schema
Description: Create the initial database schema with all base tables
Created: 2025-08-21 02:30:00
"""
from migrations.migration import Migration


class InitialSchemaMigration(Migration):
    """
    Create the initial database schema with all base tables
    """
    
    def __init__(self):
        super().__init__()
        self.description = "Create the initial database schema with all base tables"
    
    def up(self, db):
        """Apply the migration."""
        
        # Core content tables
        self.execute_sql(db, '''
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
                meta_description TEXT,
                meta_keywords TEXT,
                canonical_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL,
                FOREIGN KEY (template_id) REFERENCES post_templates (id) ON DELETE SET NULL
            )
        ''')
        
        self.execute_sql(db, '''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.execute_sql(db, '''
            CREATE TABLE IF NOT EXISTS post_tags (
                post_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (post_id, tag_id),
                FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
            )
        ''')
        
        self.execute_sql(db, '''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Admin and user management
        self.execute_sql(db, '''
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Content management
        self.execute_sql(db, '''
            CREATE TABLE IF NOT EXISTS post_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                content_template TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.execute_sql(db, '''
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
            )
        ''')
        
        self.execute_sql(db, '''
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
            )
        ''')
        
        # Site configuration
        self.execute_sql(db, '''
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
            )
        ''')
        
        self.execute_sql(db, '''
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.execute_sql(db, '''
            CREATE TABLE IF NOT EXISTS social_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                icon_class TEXT NOT NULL,
                display_order INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.execute_sql(db, '''
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
            )
        ''')
    
    def down(self, db):
        """Rollback the migration."""
        
        # Drop tables in reverse order to handle foreign key constraints
        tables = [
            'post_tags',
            'posts', 
            'tags',
            'categories',
            'admin_users',
            'post_templates',
            'image_gallery',
            'quotes',
            'email_config',
            'contact_messages',
            'social_links',
            'about_info'
        ]
        
        for table in tables:
            self.execute_sql(db, f'DROP TABLE IF EXISTS {table}')