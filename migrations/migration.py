"""
Database migration system for the Story Hub application.
"""
import os
import sqlite3
import importlib.util
from datetime import datetime
from abc import ABC, abstractmethod
from flask import current_app


class Migration(ABC):
    """Base class for all database migrations."""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.version = None
        self.description = ""
    
    @abstractmethod
    def up(self, db):
        """Apply the migration."""
        pass
    
    @abstractmethod
    def down(self, db):
        """Rollback the migration."""
        pass
    
    def execute_sql(self, db, sql, params=None):
        """Execute SQL with optional parameters."""
        if params:
            db.execute(sql, params)
        else:
            db.execute(sql)
    
    def table_exists(self, db, table_name):
        """Check if a table exists."""
        cursor = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
            (table_name,)
        )
        return cursor.fetchone() is not None
    
    def column_exists(self, db, table_name, column_name):
        """Check if a column exists in a table."""
        cursor = db.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        return column_name in columns
    
    def index_exists(self, db, index_name):
        """Check if an index exists."""
        cursor = db.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name=?", 
            (index_name,)
        )
        return cursor.fetchone() is not None


class MigrationManager:
    """Manages database migrations."""
    
    def __init__(self, app=None):
        self.app = app
        self.migrations_dir = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the migration manager with Flask app."""
        self.app = app
        self.migrations_dir = os.path.join(app.root_path, 'migrations')
        
        # Ensure migrations table exists
        with app.app_context():
            self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """Create the migrations tracking table if it doesn't exist."""
        from models import get_db
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                checksum TEXT
            )
        ''')
        db.commit()
    
    def get_pending_migrations(self):
        """Get list of migrations that haven't been applied yet."""
        applied_versions = self._get_applied_versions()
        all_migrations = self._discover_migrations()
        
        pending = []
        for version, migration_file in all_migrations:
            if version not in applied_versions:
                pending.append((version, migration_file))
        
        return sorted(pending)
    
    def get_applied_migrations(self):
        """Get list of applied migrations."""
        from models import get_db
        db = get_db()
        cursor = db.execute('''
            SELECT version, name, applied_at 
            FROM schema_migrations 
            ORDER BY applied_at DESC
        ''')
        return cursor.fetchall()
    
    def _get_applied_versions(self):
        """Get set of applied migration versions."""
        from models import get_db
        db = get_db()
        cursor = db.execute('SELECT version FROM schema_migrations')
        return {row[0] for row in cursor.fetchall()}
    
    def _discover_migrations(self):
        """Discover all migration files in the migrations directory."""
        migrations = []
        
        if not os.path.exists(self.migrations_dir):
            return migrations
        
        for filename in os.listdir(self.migrations_dir):
            if filename.endswith('.py') and filename != '__init__.py' and filename != 'migration.py':
                # Extract version from filename (e.g., "001_initial_schema.py" -> "001")
                if '_' in filename:
                    version = filename.split('_')[0]
                    migrations.append((version, filename))
        
        return migrations
    
    def _load_migration(self, filename):
        """Load a migration class from a file."""
        filepath = os.path.join(self.migrations_dir, filename)
        
        spec = importlib.util.spec_from_file_location("migration", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find the Migration class in the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, Migration) and 
                attr != Migration):
                return attr()
        
        raise ValueError(f"No Migration class found in {filename}")
    
    def migrate_up(self, target_version=None):
        """Apply pending migrations up to target version."""
        from models import get_db
        
        pending = self.get_pending_migrations()
        if not pending:
            return "No pending migrations."
        
        applied_count = 0
        results = []
        
        for version, filename in pending:
            if target_version and version > target_version:
                break
            
            try:
                migration = self._load_migration(filename)
                migration.version = version
                
                db = get_db()
                
                # Apply the migration
                migration.up(db)
                
                # Record the migration as applied
                db.execute('''
                    INSERT INTO schema_migrations (version, name, applied_at)
                    VALUES (?, ?, ?)
                ''', (version, migration.name, datetime.now()))
                
                db.commit()
                applied_count += 1
                results.append(f"Applied migration {version}: {migration.name}")
                
            except Exception as e:
                db.rollback()
                results.append(f"Failed to apply migration {version}: {str(e)}")
                break
        
        return results
    
    def migrate_down(self, target_version):
        """Rollback migrations down to target version."""
        from models import get_db
        
        applied = self.get_applied_migrations()
        rollback_count = 0
        results = []
        
        for migration_info in applied:
            version = migration_info['version']
            
            if version <= target_version:
                break
            
            try:
                # Find the migration file
                filename = None
                for v, f in self._discover_migrations():
                    if v == version:
                        filename = f
                        break
                
                if not filename:
                    results.append(f"Migration file not found for version {version}")
                    continue
                
                migration = self._load_migration(filename)
                migration.version = version
                
                db = get_db()
                
                # Rollback the migration
                migration.down(db)
                
                # Remove the migration record
                db.execute('DELETE FROM schema_migrations WHERE version = ?', (version,))
                
                db.commit()
                rollback_count += 1
                results.append(f"Rolled back migration {version}: {migration.name}")
                
            except Exception as e:
                db.rollback()
                results.append(f"Failed to rollback migration {version}: {str(e)}")
                break
        
        return results
    
    def generate_migration(self, name, description=""):
        """Generate a new migration file."""
        if not os.path.exists(self.migrations_dir):
            os.makedirs(self.migrations_dir)
        
        # Get next version number
        existing_migrations = self._discover_migrations()
        if existing_migrations:
            last_version = max(int(v) for v, _ in existing_migrations)
            next_version = f"{last_version + 1:03d}"
        else:
            next_version = "001"
        
        # Generate filename
        safe_name = name.lower().replace(' ', '_').replace('-', '_')
        filename = f"{next_version}_{safe_name}.py"
        filepath = os.path.join(self.migrations_dir, filename)
        
        # Generate migration template
        template = f'''"""
Migration: {name}
Description: {description}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
from migrations.migration import Migration


class {name.replace(' ', '').replace('_', '')}Migration(Migration):
    """
    {description}
    """
    
    def __init__(self):
        super().__init__()
        self.description = "{description}"
    
    def up(self, db):
        """Apply the migration."""
        # Add your migration logic here
        # Example:
        # self.execute_sql(db, """
        #     CREATE TABLE example (
        #         id INTEGER PRIMARY KEY AUTOINCREMENT,
        #         name TEXT NOT NULL
        #     )
        # """)
        pass
    
    def down(self, db):
        """Rollback the migration."""
        # Add your rollback logic here
        # Example:
        # self.execute_sql(db, "DROP TABLE IF EXISTS example")
        pass
'''
        
        with open(filepath, 'w') as f:
            f.write(template)
        
        return f"Generated migration: {filename}"
    
    def status(self):
        """Get migration status."""
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()
        
        status = {
            'applied_count': len(applied),
            'pending_count': len(pending),
            'applied': applied,
            'pending': pending
        }
        
        return status


# Global migration manager instance
migration_manager = MigrationManager()