"""
Main routes for the Story Hub application.
"""
from flask import Blueprint, render_template, request
from models import PostModel, TagModel, CategoryModel
from utils import is_admin_logged_in

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Home page with featured post and latest posts."""
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 3  # Show 3 posts per page
    
    # Get featured post
    featured_post = PostModel.get_featured_post()
    
    # Get total count of non-featured posts
    if featured_post:
        total_posts = PostModel.count_non_featured_posts()
        posts = PostModel.get_non_featured_posts_paginated(page, per_page)
    else:
        total_posts = PostModel.count_all_posts()
        posts = PostModel.get_all_posts_paginated(page, per_page)
    
    # Calculate pagination info
    total_pages = (total_posts + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    prev_page = page - 1 if has_prev else None
    next_page = page + 1 if has_next else None
    
    # Get popular tags for sidebar
    popular_tags = TagModel.get_popular_tags(8)
    
    return render_template('index.html', 
                         posts=posts, 
                         featured_post=featured_post,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=prev_page,
                         next_page=next_page,
                         popular_tags=popular_tags)


@main.route('/stories')
def stories():
    """Stories page with pagination."""
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    
    # Responsive pagination - 6 for larger devices, 3 for mobile
    # We'll use JavaScript to determine this, but default to 6
    per_page = request.args.get('per_page', 6, type=int)
    if per_page not in [3, 6]:
        per_page = 6  # Default fallback
    
    # Get paginated stories
    stories = PostModel.get_posts_by_type_paginated('story', page, per_page)
    total_stories = PostModel.count_posts_by_type('story')
    
    # Calculate pagination info
    total_pages = (total_stories + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    prev_page = page - 1 if has_prev else None
    next_page = page + 1 if has_next else None
    
    return render_template('stories.html', 
                         stories=stories,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=prev_page,
                         next_page=next_page,
                         per_page=per_page,
                         total_stories=total_stories)


@main.route('/articles')
def articles():
    """Articles page with pagination."""
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    
    # Responsive pagination - 6 for larger devices, 3 for mobile
    # We'll use JavaScript to determine this, but default to 6
    per_page = request.args.get('per_page', 6, type=int)
    if per_page not in [3, 6]:
        per_page = 6  # Default fallback
    
    # Get paginated articles
    articles = PostModel.get_posts_by_type_paginated('article', page, per_page)
    total_articles = PostModel.count_posts_by_type('article')
    
    # Calculate pagination info
    total_pages = (total_articles + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    prev_page = page - 1 if has_prev else None
    next_page = page + 1 if has_next else None
    
    return render_template('articles.html', 
                         articles=articles,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=prev_page,
                         next_page=next_page,
                         per_page=per_page,
                         total_articles=total_articles)


@main.route('/articles/category/<category_slug>')
def articles_by_category(category_slug):
    """Articles page filtered by category with pagination."""
    # Get the category
    category = CategoryModel.get_category_by_slug(category_slug)
    if not category:
        return render_template('404.html'), 404
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    
    # Responsive pagination - 6 for larger devices, 3 for mobile
    per_page = request.args.get('per_page', 6, type=int)
    if per_page not in [3, 6]:
        per_page = 6  # Default fallback
    
    # Get paginated articles for this category
    articles = PostModel.get_posts_by_type_paginated('article', page, per_page, category['id'])
    total_articles = PostModel.count_posts_by_type('article', category['id'])
    
    # Calculate pagination info
    total_pages = (total_articles + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    prev_page = page - 1 if has_prev else None
    next_page = page + 1 if has_next else None
    
    return render_template('articles.html', 
                         articles=articles,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=prev_page,
                         next_page=next_page,
                         per_page=per_page,
                         total_articles=total_articles,
                         category=category)


# Add admin status and categories to template context
@main.app_context_processor
def inject_template_vars():
    """Inject admin login status and categories into all templates."""
    # Only show categories that have articles
    all_categories = CategoryModel.get_all_categories()
    categories_with_articles = [cat for cat in all_categories if cat['post_count'] > 0]
    
    return {
        'is_admin_logged_in': is_admin_logged_in(),
        'categories': categories_with_articles
    }