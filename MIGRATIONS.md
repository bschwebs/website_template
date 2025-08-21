# Database Migration System

This document describes the database migration system for the Story Hub application.

## Overview

The migration system allows you to:
- **Version control your database schema** changes
- **Apply changes incrementally** and safely
- **Rollback changes** when needed
- **Track migration history** and status
- **Generate new migrations** easily

## Quick Start

### Check Migration Status
```bash
python -m flask db status
```

### Apply All Pending Migrations
```bash
python -m flask db migrate
```

### Create a New Migration
```bash
python -m flask db create-migration "add_new_table" --description "Add table for new feature"
```

## Commands Reference

### `status`
Shows the current migration status including applied and pending migrations.

```bash
python -m flask db status
```

**Example output:**
```
=== Migration Status ===
Applied migrations: 2
Pending migrations: 0

Applied migrations:
  [X] 002: AnalyticsTablesMigration (2025-08-20 20:48:33)
  [X] 001: InitialSchemaMigration (2025-08-20 20:48:33)

Database is up to date!
```

### `migrate`
Applies all pending migrations in order.

```bash
python -m flask db migrate
```

### `migrate-to <version>`
Migrates to a specific version (useful for partial updates).

```bash
python -m flask db migrate-to 001
```

### `rollback <version>`
Rolls back to a specific version (removes newer migrations).

```bash
python -m flask db rollback 001
```

**⚠️ Warning:** This is destructive and will remove data from newer migrations.

### `create-migration <name>`
Creates a new migration file template.

```bash
python -m flask db create-migration "add_user_settings" --description "Add user settings table"
```

### `init`
Initializes the database (applies all migrations + creates default data).

```bash
python -m flask db init
```

### `reset`
**⚠️ DESTRUCTIVE:** Completely resets the database (deletes all data).

```bash
python -m flask db reset
```

### `backup`
Creates a backup of the current database.

```bash
python -m flask db backup
```

### `show-schema`
Shows the current database schema.

```bash
python -m flask db show-schema
```

## Creating Migrations

### 1. Generate Migration File
```bash
python -m flask db create-migration "add_comments_table" --description "Add comments system"
```

This creates a file like `migrations/003_add_comments_table.py`.

### 2. Edit the Migration
Open the generated file and implement the `up()` and `down()` methods:

```python
def up(self, db):
    """Apply the migration."""
    self.execute_sql(db, '''
        CREATE TABLE comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            author_name TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
        )
    ''')
    
    # Add index for better performance
    self.execute_sql(db, '''
        CREATE INDEX idx_comments_post_id ON comments (post_id)
    ''')

def down(self, db):
    """Rollback the migration."""
    self.execute_sql(db, 'DROP INDEX IF EXISTS idx_comments_post_id')
    self.execute_sql(db, 'DROP TABLE IF EXISTS comments')
```

### 3. Apply the Migration
```bash
python -m flask db migrate
```

## Migration Helper Methods

Your migration class inherits helpful methods:

### `execute_sql(db, sql, params=None)`
Execute SQL with optional parameters.

```python
self.execute_sql(db, "INSERT INTO settings (key, value) VALUES (?, ?)", 
                ("theme", "dark"))
```

### `table_exists(db, table_name)`
Check if a table exists.

```python
if not self.table_exists(db, "comments"):
    # Create table
```

### `column_exists(db, table_name, column_name)`
Check if a column exists.

```python
if not self.column_exists(db, "users", "email"):
    self.execute_sql(db, "ALTER TABLE users ADD COLUMN email TEXT")
```

### `index_exists(db, index_name)`
Check if an index exists.

```python
if not self.index_exists(db, "idx_posts_category"):
    self.execute_sql(db, "CREATE INDEX idx_posts_category ON posts (category_id)")
```

## Best Practices

### 1. **Always Write Rollback Logic**
Every `up()` method should have a corresponding `down()` method that reverses the changes.

### 2. **Use Descriptive Names**
Migration names should clearly describe what they do:
- ✅ `add_user_preferences_table`
- ✅ `add_email_index_to_users`
- ❌ `update_db`
- ❌ `fix_stuff`

### 3. **Test Migrations**
Test both applying and rolling back your migrations:

```bash
# Apply
python -m flask db migrate

# Test rollback
python -m flask db rollback <previous_version>

# Apply again
python -m flask db migrate
```

### 4. **Make Incremental Changes**
Create separate migrations for different features rather than one large migration.

### 5. **Backup Before Major Changes**
```bash
python -m flask db backup
```

### 6. **Check Column/Table Existence**
Use helper methods to make migrations idempotent:

```python
def up(self, db):
    if not self.table_exists(db, "new_table"):
        self.execute_sql(db, "CREATE TABLE new_table (...)")
    
    if not self.column_exists(db, "posts", "new_column"):
        self.execute_sql(db, "ALTER TABLE posts ADD COLUMN new_column TEXT")
```

## Migration File Structure

```
migrations/
├── __init__.py
├── migration.py              # Base migration classes
├── 001_initial_schema.py     # Initial database schema
├── 002_analytics_tables.py   # Analytics system tables
└── 003_add_comments.py       # Your new migrations
```

## Troubleshooting

### Migration Fails
1. **Check the error message** in the output
2. **Fix the migration file** 
3. **Try again** - failed migrations aren't recorded as applied

### Need to Skip a Migration
If you need to mark a migration as applied without running it:

```sql
INSERT INTO schema_migrations (version, name, applied_at) 
VALUES ('003', 'SkippedMigration', datetime('now'));
```

### Reset Everything
If you need to start over:

```bash
python -m flask db reset
```

This will delete all data and reapply all migrations.

## Database Schema Tracking

The system uses a `schema_migrations` table to track applied migrations:

```sql
CREATE TABLE schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checksum TEXT
);
```

## Integration with Development

### Environment Setup
Set the Flask app environment variable:

```bash
# Windows
set FLASK_APP=app.py

# Linux/macOS
export FLASK_APP=app.py
```

### Deployment
In production, run migrations as part of your deployment process:

```bash
python -m flask db migrate
```

This ensures your production database is always up to date with your code.