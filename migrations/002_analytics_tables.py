"""
Migration: Analytics Tables
Description: Add analytics and page view tracking tables
Created: 2025-08-21 02:35:00
"""
from migrations.migration import Migration


class AnalyticsTablesMigration(Migration):
    """
    Add analytics and page view tracking tables
    """
    
    def __init__(self):
        super().__init__()
        self.description = "Add analytics and page view tracking tables"
    
    def up(self, db):
        """Apply the migration."""
        
        # Page views tracking
        self.execute_sql(db, '''
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
            )
        ''')
        
        # Daily analytics aggregation
        self.execute_sql(db, '''
            CREATE TABLE IF NOT EXISTS daily_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL UNIQUE,
                total_views INTEGER DEFAULT 0,
                unique_visitors INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Post-specific analytics
        self.execute_sql(db, '''
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
            )
        ''')
        
        # Create indexes for better performance
        self.execute_sql(db, '''
            CREATE INDEX IF NOT EXISTS idx_page_views_date 
            ON page_views (view_date)
        ''')
        
        self.execute_sql(db, '''
            CREATE INDEX IF NOT EXISTS idx_page_views_post_id 
            ON page_views (post_id)
        ''')
        
        self.execute_sql(db, '''
            CREATE INDEX IF NOT EXISTS idx_page_views_ip_date 
            ON page_views (ip_address, view_date)
        ''')
    
    def down(self, db):
        """Rollback the migration."""
        
        # Drop indexes first
        self.execute_sql(db, 'DROP INDEX IF EXISTS idx_page_views_date')
        self.execute_sql(db, 'DROP INDEX IF EXISTS idx_page_views_post_id')
        self.execute_sql(db, 'DROP INDEX IF EXISTS idx_page_views_ip_date')
        
        # Drop tables
        self.execute_sql(db, 'DROP TABLE IF EXISTS post_analytics')
        self.execute_sql(db, 'DROP TABLE IF EXISTS daily_analytics')
        self.execute_sql(db, 'DROP TABLE IF EXISTS page_views')