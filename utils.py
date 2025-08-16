"""
Utility functions for the Story Hub application.
"""
import os
from functools import wraps
from flask import session, flash, redirect, url_for, current_app
from slugify import slugify
from models import PostModel


def allowed_file(filename):
    """Check if uploaded file has allowed extension."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def admin_required(f):
    """Decorator to require admin authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Admin access required.', 'error')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def is_admin_logged_in():
    """Check if admin user is currently logged in."""
    return session.get('admin_logged_in', False)


def generate_unique_slug(title, post_id=None):
    """Generate a unique slug for a post title."""
    base_slug = slugify(title)
    if not base_slug:
        base_slug = 'untitled'
    
    slug = base_slug
    counter = 1
    
    while PostModel.slug_exists(slug, post_id):
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug


def delete_file(filename):
    """Delete an uploaded file if it exists."""
    if filename:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)


def save_uploaded_file(file, upload_folder):
    """Save an uploaded file and return the filename."""
    import uuid
    from werkzeug.utils import secure_filename
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower())
        file.save(os.path.join(upload_folder, filename))
        return filename
    return None


def generate_tag_slug(tag_name):
    """Generate a URL-friendly slug for a tag."""
    return slugify(tag_name.lower())


def parse_tags(tag_string):
    """Parse a comma-separated string of tags into a list."""
    if not tag_string:
        return []
    
    # Split by comma and clean up
    tags = [tag.strip() for tag in tag_string.split(',')]
    # Remove empty tags and duplicates while preserving order
    seen = set()
    result = []
    for tag in tags:
        if tag and tag.lower() not in seen:
            result.append(tag)
            seen.add(tag.lower())
    
    return result