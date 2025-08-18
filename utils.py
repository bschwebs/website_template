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


def generate_meta_description(content, excerpt=None, max_length=160):
    """Generate a meta description from post content or excerpt."""
    if excerpt:
        description = excerpt.strip()
    else:
        # Remove HTML tags and get plain text
        import re
        clean_content = re.sub('<[^<]+?>', '', content)
        description = clean_content.strip()
    
    # Truncate to max_length and add ellipsis if needed
    if len(description) > max_length:
        description = description[:max_length-3].rsplit(' ', 1)[0] + '...'
    
    return description


def generate_keywords(tags, additional_keywords=None):
    """Generate SEO keywords from tags and additional context."""
    keywords = []
    
    # Add tags as keywords
    if tags:
        keywords.extend([tag.strip().lower() for tag in tags if tag.strip()])
    
    # Add additional keywords
    if additional_keywords:
        if isinstance(additional_keywords, str):
            additional_keywords = [kw.strip() for kw in additional_keywords.split(',')]
        keywords.extend([kw.strip().lower() for kw in additional_keywords if kw.strip()])
    
    # Add default site keywords
    default_keywords = ['blog', 'Japan history', 'articles', 'Japanese culture', 'writing']
    keywords.extend(default_keywords)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword not in seen:
            unique_keywords.append(keyword)
            seen.add(keyword)
    
    return ', '.join(unique_keywords[:20])  # Limit to 20 keywords


def get_canonical_url(request, slug=None, post_id=None):
    """Generate canonical URL for SEO."""
    base_url = request.url_root.rstrip('/')
    
    if slug:
        return f"{base_url}/post/{slug}"
    elif post_id:
        return f"{base_url}/post/{post_id}"
    else:
        return request.url


def clean_html_for_seo(html_content, max_length=200):
    """Clean HTML content for SEO meta tags."""
    import re
    
    # Remove HTML tags
    clean_text = re.sub('<[^<]+?>', '', html_content)
    
    # Remove extra whitespace
    clean_text = ' '.join(clean_text.split())
    
    # Truncate if needed
    if len(clean_text) > max_length:
        clean_text = clean_text[:max_length-3].rsplit(' ', 1)[0] + '...'
    
    return clean_text


def calculate_reading_time(content, words_per_minute=200):
    """Calculate estimated reading time for content."""
    import re
    import math
    
    if not content:
        return 1
    
    # Remove HTML tags
    clean_content = re.sub('<[^<]+?>', '', content)
    
    # Count words
    words = len(clean_content.split())
    
    # Calculate reading time in minutes
    reading_time = math.ceil(words / words_per_minute)
    
    return max(1, reading_time)


def get_category_color_class(category_name):
    """Get CSS class for category color coding."""
    if not category_name:
        return 'category-default'
    
    category_colors = {
        'history': 'category-history',
        'culture': 'category-culture', 
        'art': 'category-art',
        'politics': 'category-politics',
        'society': 'category-society',
        'technology': 'category-technology'
    }
    
    normalized_name = category_name.lower().replace(' ', '').replace('-', '')
    return category_colors.get(normalized_name, 'category-default')


def truncate_content_smart(content, max_length=120):
    """Intelligently truncate content at word boundaries."""
    if not content or len(content) <= max_length:
        return content or ''
    
    # Remove HTML tags first
    import re
    clean_content = re.sub('<[^<]+?>', '', content)
    
    if len(clean_content) <= max_length:
        return clean_content
    
    # Truncate at word boundary
    truncated = clean_content[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + '...'


def get_card_size_class(content, index):
    """Determine card size based on content length and position."""
    content_length = len(content) if content else 0
    
    # Every 7th card is extra large
    if index % 7 == 0:
        return 'card-size-xl'
    elif content_length > 150:
        return 'card-size-large' 
    elif content_length > 100:
        return 'card-size-medium'
    else:
        return 'card-size-small'


def get_tag_size(post_count, max_count):
    """Determine tag size class based on post count."""
    if max_count <= 1:
        return 'md'
    
    ratio = post_count / max_count
    
    if ratio >= 0.8:
        return 'xl'
    elif ratio >= 0.6:
        return 'lg'
    elif ratio >= 0.4:
        return 'md'
    elif ratio >= 0.2:
        return 'sm'
    else:
        return 'xs'


def get_tag_icon(tag_name):
    """Get FontAwesome icon for a tag based on its name."""
    tag_icons = {
        'history': 'scroll',
        'culture': 'torii-gate',
        'art': 'palette',
        'politics': 'university',
        'society': 'users',
        'technology': 'microchip',
        'samurai': 'sword',
        'temple': 'place-of-worship',
        'festival': 'festival',
        'food': 'utensils',
        'anime': 'tv',
        'manga': 'book',
        'tradition': 'leaf',
        'modern': 'city',
        'ancient': 'monument',
        'religion': 'prayer',
        'war': 'shield-alt',
        'peace': 'dove',
        'economy': 'chart-line',
        'education': 'graduation-cap',
        'travel': 'plane',
        'nature': 'tree',
        'language': 'comment-alt',
        'literature': 'feather-alt',
        'music': 'music',
        'dance': 'heart',
        'martial-arts': 'fist-raised',
        'zen': 'om',
        'buddhism': 'dharmachakra',
        'shinto': 'torii-gate'
    }
    
    normalized_name = tag_name.lower().replace(' ', '-').replace('_', '-')
    
    # Check for exact matches first
    if normalized_name in tag_icons:
        return tag_icons[normalized_name]
    
    # Check for partial matches
    for key, icon in tag_icons.items():
        if key in normalized_name or normalized_name in key:
            return icon
    
    # Default icon
    return 'tag'


def get_tag_description(tag_name, post_count):
    """Generate a description for a tag based on its name and usage."""
    descriptions = {
        'history': f"Explore {post_count} article{'s' if post_count != 1 else ''} about Japanese historical events, periods, and influential figures.",
        'culture': f"Discover {post_count} post{'s' if post_count != 1 else ''} exploring the rich cultural traditions and customs of Japan.",
        'art': f"Browse {post_count} article{'s' if post_count != 1 else ''} showcasing Japanese artistic expressions and creative traditions.",
        'politics': f"Read {post_count} post{'s' if post_count != 1 else ''} about Japan's political system, governance, and international relations.",
        'society': f"Learn from {post_count} article{'s' if post_count != 1 else ''} about Japanese social structures, customs, and modern life.",
        'technology': f"Explore {post_count} post{'s' if post_count != 1 else ''} covering Japan's technological innovations and digital culture.",
        'samurai': f"Delve into {post_count} article{'s' if post_count != 1 else ''} about the legendary warrior class and their code of honor.",
        'temple': f"Visit {post_count} post{'s' if post_count != 1 else ''} exploring Japan's sacred spaces and religious architecture.",
        'festival': f"Experience {post_count} article{'s' if post_count != 1 else ''} about Japan's vibrant festivals and celebrations.",
        'food': f"Savor {post_count} post{'s' if post_count != 1 else ''} about Japanese cuisine, cooking techniques, and food culture."
    }
    
    normalized_name = tag_name.lower().replace(' ', '').replace('-', '').replace('_', '')
    
    # Check for exact matches
    for key, desc in descriptions.items():
        if key.replace('-', '') == normalized_name:
            return desc
    
    # Check for partial matches
    for key, desc in descriptions.items():
        if key.replace('-', '') in normalized_name or normalized_name in key.replace('-', ''):
            return desc
    
    # Generic description
    if post_count == 1:
        return f"Discover 1 article tagged with '{tag_name}' and explore related content."
    else:
        return f"Browse {post_count} articles tagged with '{tag_name}' covering various aspects of this topic."