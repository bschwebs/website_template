"""
Command line interface for the Story Hub application.
Includes database migration commands.
"""
import click
from flask import Flask
from flask.cli import with_appcontext
from migrations.migration import migration_manager


def init_cli(app: Flask):
    """Initialize CLI commands with the Flask app."""
    app.cli.add_command(db_cli, name='db')


@click.group()
def db_cli():
    """Database management commands."""
    pass


@db_cli.command()
@with_appcontext
def status():
    """Show migration status."""
    status_info = migration_manager.status()
    
    click.echo("=== Migration Status ===")
    click.echo(f"Applied migrations: {status_info['applied_count']}")
    click.echo(f"Pending migrations: {status_info['pending_count']}")
    
    if status_info['applied']:
        click.echo("\nApplied migrations:")
        for migration in status_info['applied'][:10]:  # Show last 10
            click.echo(f"  [X] {migration['version']}: {migration['name']} ({migration['applied_at']})")
    
    if status_info['pending']:
        click.echo("\nPending migrations:")
        for version, filename in status_info['pending']:
            click.echo(f"  [ ] {version}: {filename}")
    
    if not status_info['pending']:
        click.echo(click.style("\nDatabase is up to date!", fg='green'))


@db_cli.command()
@with_appcontext
def migrate():
    """Apply pending migrations."""
    click.echo("Applying migrations...")
    results = migration_manager.migrate_up()
    
    for result in results:
        if "Failed" in result:
            click.echo(click.style(f"[ERROR] {result}", fg='red'))
        else:
            click.echo(click.style(f"[OK] {result}", fg='green'))


@db_cli.command()
@click.argument('version')
@with_appcontext
def migrate_to(version):
    """Migrate to a specific version."""
    click.echo(f"Migrating to version {version}...")
    results = migration_manager.migrate_up(target_version=version)
    
    for result in results:
        if "Failed" in result:
            click.echo(click.style(f"[ERROR] {result}", fg='red'))
        else:
            click.echo(click.style(f"[OK] {result}", fg='green'))


@db_cli.command()
@click.argument('version')
@with_appcontext 
def rollback(version):
    """Rollback to a specific version."""
    if not click.confirm(f'Are you sure you want to rollback to version {version}?'):
        click.echo("Rollback cancelled.")
        return
    
    click.echo(f"Rolling back to version {version}...")
    results = migration_manager.migrate_down(target_version=version)
    
    for result in results:
        if "Failed" in result:
            click.echo(click.style(f"[ERROR] {result}", fg='red'))
        else:
            click.echo(click.style(f"[OK] {result}", fg='green'))


@db_cli.command()
@click.argument('name')
@click.option('--description', '-d', default='', help='Migration description')
@with_appcontext
def create_migration(name, description):
    """Create a new migration file."""
    result = migration_manager.generate_migration(name, description)
    click.echo(click.style(f"[OK] {result}", fg='green'))


@db_cli.command()
@with_appcontext
def init():
    """Initialize the database with current schema."""
    from models import init_db
    init_db()
    click.echo(click.style("✓ Database initialized", fg='green'))


@db_cli.command()
@with_appcontext
def reset():
    """Reset the database (WARNING: This will delete all data!)."""
    if not click.confirm('This will delete ALL data. Are you sure?'):
        click.echo("Reset cancelled.")
        return
    
    import os
    from flask import current_app
    
    # Close any existing connections
    from models import get_db, close_db
    close_db(None)
    
    # Delete the database file
    db_path = current_app.config['DATABASE']
    if os.path.exists(db_path):
        os.remove(db_path)
        click.echo("Database file deleted.")
    
    # Reinitialize
    init_db()
    click.echo(click.style("✓ Database reset and reinitialized", fg='green'))


# Additional utility commands
@db_cli.command()
@with_appcontext
def backup():
    """Create a backup of the current database."""
    import shutil
    from datetime import datetime
    from flask import current_app
    
    db_path = current_app.config['DATABASE']
    backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    backup_path = os.path.join(os.path.dirname(db_path), backup_name)
    
    shutil.copy2(db_path, backup_path)
    click.echo(click.style(f"✓ Database backed up to: {backup_name}", fg='green'))


@db_cli.command()
@with_appcontext
def show_schema():
    """Show current database schema."""
    from models import get_db
    
    db = get_db()
    cursor = db.execute("""
        SELECT name, sql 
        FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    
    tables = cursor.fetchall()
    
    click.echo("=== Current Database Schema ===")
    for table in tables:
        click.echo(f"\nTable: {table['name']}")
        if table['sql']:
            click.echo(table['sql'])


if __name__ == '__main__':
    db_cli()