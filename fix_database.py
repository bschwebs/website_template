#!/usr/bin/env python3
"""
Fix database by creating missing email_config table.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db
from flask import Flask
import sqlite3

# Create a minimal Flask app for database context
app = Flask(__name__)
app.config['DATABASE'] = 'blog.db'

def fix_database():
    """Create missing email_config table."""
    
    with app.app_context():
        print("Fixing database - creating email_config table...")
        
        try:
            db = get_db()
            
            # Create the email_config table if it doesn't exist
            db.execute('''
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
            ''')
            
            db.commit()
            print("SUCCESS: email_config table created")
            
            # Check if table exists and has the right structure
            cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='email_config'")
            if cursor.fetchone():
                print("SUCCESS: email_config table verified")
                
                # Show table structure
                cursor = db.execute("PRAGMA table_info(email_config)")
                columns = cursor.fetchall()
                print("\nTable structure:")
                for col in columns:
                    print(f"  {col[1]} ({col[2]})")
                
                return True
            else:
                print("ERROR: email_config table not found after creation")
                return False
                
        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {str(e)}")
            return False

if __name__ == "__main__":
    success = fix_database()
    if success:
        print("\nDatabase fixed successfully! You can now configure email settings.")
        sys.exit(0)
    else:
        print("\nFailed to fix database.")
        sys.exit(1)